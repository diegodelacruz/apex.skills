"""
ExternalRepoIndexer: Manage persistence and indexing of learned external repositories.
Handles CRUD operations on external-repos JSON files and maintains central index.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ExternalRepoIndexer:
    """Manage external repository learning storage and indexing."""

    def __init__(self, repos_dir: Optional[Path] = None):
        """
        Initialize indexer.

        Args:
                repos_dir: Path to external-repos directory.
                        Defaults to control-proyecto/external-repos/
        """
        if repos_dir is None:
            # Default: control-proyecto/external-repos/
            from scripts.path_setup import get_repo_root

            repos_dir = get_repo_root() / "control-proyecto" / "external-repos"

        self.repos_dir = Path(repos_dir)
        self.index_file = self.repos_dir / "external-repos-index.json"
        self._ensure_structure()

    def _ensure_structure(self) -> None:
        """Create external-repos directory if it doesn't exist."""
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_file.exists():
            self._write_index({})

    def _read_index(self) -> Dict:
        """Read central index file."""
        if not self.index_file.exists():
            return {}
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _write_index(self, index: Dict) -> None:
        """Write central index file atomically."""
        # Use temporary file to ensure atomic write
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.repos_dir, delete=False, suffix=".tmp"
        ) as tmp_file:
            json.dump(index, tmp_file, indent=2)
            tmp_path = Path(tmp_file.name)

        # Atomically replace the original file
        tmp_path.replace(self.index_file)

    def save_learned_repo(self, repo_metadata: Dict, analysis_summary: Dict) -> str:
        """
        Save a learned repository with analysis.

        Args:
                repo_metadata: Output from ExternalRepoScanner.scan()
                analysis_summary: User-provided analysis (what they learned)

        Returns:
                Repository identifier (filename without .json)
        """
        repo_id = repo_metadata["identifier"]
        repo_file = self.repos_dir / f"{repo_id}.json"

        # Combine metadata with analysis
        full_data = {
            **repo_metadata,
            "learning_summary": analysis_summary,
        }

        # Write repo JSON
        with open(repo_file, "w", encoding="utf-8") as f:
            json.dump(full_data, f, indent=2)

        # Update index
        index = self._read_index()
        index[repo_id] = {
            "source": repo_metadata["source"],
            "source_type": repo_metadata["source_type"],
            "scanned_at": repo_metadata["scanned_at"],
            "learned_at": datetime.utcnow().isoformat() + "Z",
        }
        self._write_index(index)

        return repo_id

    def get_learned_repo(self, repo_id: str) -> Optional[Dict]:
        """
        Retrieve a learned repository data.

        Args:
                repo_id: Repository identifier

        Returns:
                Repository data dict or None if not found
        """
        repo_file = self.repos_dir / f"{repo_id}.json"
        if not repo_file.exists():
            return None

        try:
            with open(repo_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def list_all(self) -> List[Dict]:
        """
        List all learned repositories.

        Returns:
                List of repository entries from index
        """
        index = self._read_index()
        return [
            {
                "identifier": repo_id,
                **repo_data,
            }
            for repo_id, repo_data in sorted(index.items())
        ]

    def search_by_source(self, source: str) -> Optional[str]:
        """
        Search for a repository by source URL or path.

        Args:
                source: GitHub URL or local path

        Returns:
                Repository identifier if found, None otherwise
        """
        index = self._read_index()
        for repo_id, data in index.items():
            if data["source"] == source:
                return repo_id
        return None

    def repo_exists(self, repo_id: str) -> bool:
        """Check if a learned repository exists."""
        return (self.repos_dir / f"{repo_id}.json").exists()

    def delete_learned_repo(self, repo_id: str) -> bool:
        """
        Delete a learned repository.

        Args:
                repo_id: Repository identifier

        Returns:
                True if deleted, False if not found
        """
        repo_file = self.repos_dir / f"{repo_id}.json"
        if not repo_file.exists():
            return False

        repo_file.unlink()

        # Update index
        index = self._read_index()
        if repo_id in index:
            del index[repo_id]
            self._write_index(index)

        return True

    def get_context(self, repo_id: str) -> Optional[str]:
        """
        Get learning summary context for a repository.
        Used by other skills to inject context automatically.

        Args:
                repo_id: Repository identifier

        Returns:
                Learning summary string or None if not found
        """
        repo_data = self.get_learned_repo(repo_id)
        if not repo_data:
            return None

        summary = repo_data.get("learning_summary", {})
        if not summary:
            return None

        # Format context
        lines = []
        if summary.get("extracted_by_user"):
            lines.append(f"Extracted: {summary['extracted_by_user']}")
        if summary.get("analysis"):
            lines.append(f"Analysis: {summary['analysis']}")
        if summary.get("key_findings"):
            lines.append("Key findings:")
            for finding in summary["key_findings"]:
                lines.append(f"  - {finding}")

        return "\n".join(lines)

    def get_context_for_skill(self, repo_id: str, format_type: str = "text") -> Optional[str]:
        """
        Get context in format suitable for skill injection.

        Args:
                repo_id: Repository identifier
                format_type: "text" or "json"

        Returns:
                Formatted context or None if not found
        """
        repo_data = self.get_learned_repo(repo_id)
        if not repo_data:
            return None

        if format_type == "json":
            return json.dumps(repo_data, indent=2)
        else:
            return self.get_context(repo_id)


if __name__ == "__main__":
    # Example usage
    indexer = ExternalRepoIndexer()

    # List all
    print("Learned repositories:")
    for repo in indexer.list_all():
        print(f"  - {repo['identifier']}: {repo['source']}")
