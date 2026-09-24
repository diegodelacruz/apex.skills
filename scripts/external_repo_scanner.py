"""
ExternalRepoScanner: Analyze external repositories (GitHub or local) without cloning.
Supports GitHub URLs (public) and local filesystem paths.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class ExternalRepoScanner:
    """Scan external repositories and extract metadata without cloning."""

    def __init__(self, repo_source: str):
        """
        Initialize scanner with repository source.

        Args:
                repo_source: GitHub URL (https://github.com/user/repo) or local path
        """
        self.repo_source = repo_source
        self.is_github = self._is_github_url()
        self.is_local = Path(repo_source).exists() if not self.is_github else False
        self.repo_path: Optional[Path] = None
        self.repo_name: Optional[str] = None
        self._validate_source()

    def _is_github_url(self) -> bool:
        """Check if source is a GitHub URL."""
        return self.repo_source.startswith("https://github.com/")

    def _validate_source(self) -> None:
        """Validate that repository source is accessible."""
        if self.is_github:
            self._validate_github_url()
        elif self.is_local:
            self._validate_local_path()
        else:
            raise ValueError(f"Invalid source: {self.repo_source}")

    def _validate_github_url(self) -> None:
        """Validate GitHub URL format and accessibility."""
        pattern = r"^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+/?$"
        if not re.match(pattern, self.repo_source):
            raise ValueError(f"Invalid GitHub URL format: {self.repo_source}")

        # Extract repo identifier
        parts = self.repo_source.rstrip("/").split("/")
        self.repo_name = f"github-{parts[-2]}-{parts[-1]}"

    def _validate_local_path(self) -> None:
        """Validate local path exists and is accessible."""
        self.repo_path = Path(self.repo_source).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Local path does not exist: {self.repo_source}")
        if not self.repo_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.repo_source}")
        if not list(self.repo_path.iterdir()):
            raise ValueError(f"Directory is empty: {self.repo_source}")

        self.repo_name = f"local-{self.repo_path.name}"

    def scan(self) -> Dict:
        """
        Scan repository and extract metadata.

        Returns:
                Dictionary with repository structure and metadata
        """
        if self.is_local:
            return self._scan_local_repo()
        else:
            return self._scan_github_repo()

    def _scan_local_repo(self) -> Dict:
        """Scan local repository on filesystem."""
        if not self.repo_path:
            raise RuntimeError("repo_path not set")

        files, extensions, languages = self._analyze_structure(self.repo_path)
        description = self._extract_readme_description(self.repo_path)

        return {
            "identifier": self.repo_name,
            "source": str(self.repo_source),
            "source_type": "local_path",
            "scanned_at": datetime.utcnow().isoformat() + "Z",
            "repo_info": {
                "description": description,
                "languages_detected": languages,
                "file_extensions_found": sorted(extensions),
                "total_files": files,
                "structure_summary": self._build_structure_summary(self.repo_path),
            },
            "version_hash": None,
        }

    def _scan_github_repo(self) -> Dict:
        """Scan GitHub repository via API (public repos only)."""
        try:
            import requests
        except ImportError:
            raise ImportError("requests library required for GitHub scanning")

        # Extract user and repo
        parts = self.repo_source.rstrip("/").split("/")
        user, repo = parts[-2], parts[-1]

        # Get repository info
        repo_url = f"https://api.github.com/repos/{user}/{repo}"
        response = requests.get(repo_url, timeout=10)
        if response.status_code == 404:
            raise ValueError(f"Repository not found: {self.repo_source}")
        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error: {response.status_code}")

        repo_data = response.json()

        # Get repository contents (top-level structure)
        contents_url = f"https://api.github.com/repos/{user}/{repo}/contents"
        contents_response = requests.get(contents_url, timeout=10)
        if contents_response.status_code != 200:
            raise RuntimeError(f"Failed to fetch repository contents: {contents_response.status_code}")

        contents = contents_response.json()
        if isinstance(contents, dict) and "message" in contents:
            raise ValueError(f"Repository is empty: {self.repo_source}")

        # Analyze structure
        files, extensions, languages = self._analyze_github_contents(contents)

        return {
            "identifier": self.repo_name,
            "source": self.repo_source,
            "source_type": "github_url",
            "scanned_at": datetime.utcnow().isoformat() + "Z",
            "repo_info": {
                "description": repo_data.get("description", ""),
                "languages_detected": self._detect_languages(repo_data),
                "file_extensions_found": sorted(extensions),
                "total_files": files,
                "structure_summary": self._build_github_structure_summary(contents),
            },
            "version_hash": repo_data.get("default_branch"),
        }

    def _analyze_structure(
        self, path: Path, max_depth: int = 3, current_depth: int = 0
    ) -> Tuple[int, Set[str], List[str]]:
        """
        Recursively analyze directory structure.

        Returns:
                (total_files, extensions_set, languages_list)
        """
        extensions: Set[str] = set()
        file_count = 0
        ignore_patterns = {".git", ".github", "node_modules", ".venv", "__pycache__", ".env"}

        if current_depth >= max_depth:
            return file_count, extensions, []

        try:
            for item in path.iterdir():
                if item.name.startswith(".") and item.name not in {".github", ".gitignore"}:
                    continue
                if item.name in ignore_patterns:
                    continue

                if item.is_file():
                    file_count += 1
                    if item.suffix:
                        extensions.add(item.suffix)
                elif item.is_dir():
                    sub_count, sub_ext, _ = self._analyze_structure(item, max_depth, current_depth + 1)
                    file_count += sub_count
                    extensions.update(sub_ext)
        except PermissionError:
            pass

        languages = self._infer_languages(extensions)
        return file_count, extensions, languages

    def _analyze_github_contents(self, contents: List[Dict]) -> Tuple[int, Set[str], List[str]]:
        """Analyze GitHub API contents response."""
        extensions: Set[str] = set()
        file_count = len([c for c in contents if c["type"] == "file"])

        for item in contents:
            if item["type"] == "file" and "." in item["name"]:
                ext = "." + item["name"].split(".")[-1]
                extensions.add(ext)

        languages = self._infer_languages(extensions)
        return file_count, extensions, languages

    def _infer_languages(self, extensions: Set[str]) -> List[str]:
        """Infer programming languages from file extensions."""
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "JSX",
            ".tsx": "TSX",
            ".sql": "SQL",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".yml": "YAML",
            ".yaml": "YAML",
            ".json": "JSON",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".md": "Markdown",
            ".sh": "Shell",
        }

        languages = set()
        for ext in extensions:
            if ext in language_map:
                languages.add(language_map[ext])

        return sorted(list(languages))

    def _build_structure_summary(self, path: Path) -> str:
        """Build human-readable directory structure summary."""
        summary = []
        try:
            for item in sorted(path.iterdir())[:10]:  # Top 10 items
                if item.is_dir() and not item.name.startswith("."):
                    file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                    summary.append(f"{item.name}/ ({file_count} files)")
                elif item.is_file():
                    summary.append(f"{item.name}")
        except PermissionError:
            pass

        return ", ".join(summary) if summary else "[Unable to read structure]"

    def _build_github_structure_summary(self, contents: List[Dict]) -> str:
        """Build structure summary from GitHub API contents."""
        items = []
        for item in contents[:10]:
            if item["type"] == "dir":
                items.append(f"{item['name']}/")
            else:
                items.append(item["name"])
        return ", ".join(items)

    def _extract_readme_description(self, path: Path) -> str:
        """Extract description from README file if available."""
        readme_names = ["README.md", "readme.md", "README", "readme.txt"]
        for name in readme_names:
            readme_path = path / name
            if readme_path.exists():
                try:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        content = f.read(500)  # First 500 chars
                        return content.strip()
                except Exception:
                    pass
        return ""

    def _detect_languages(self, repo_data: Dict) -> List[str]:
        """Extract primary language from GitHub repo data."""
        language = repo_data.get("language")
        if language:
            return [language]
        return []


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python external_repo_scanner.py <url_or_path>")
        sys.exit(1)

    scanner = ExternalRepoScanner(sys.argv[1])
    result = scanner.scan()
    print(json.dumps(result, indent=2))
