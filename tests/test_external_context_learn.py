"""
Tests for apex-external-context-learn skill.
Tests scanner, indexer, and main script functionality.
"""

import tempfile
from pathlib import Path

import pytest

from scripts.external_repo_indexer import ExternalRepoIndexer
from scripts.external_repo_scanner import ExternalRepoScanner


class TestExternalRepoScanner:
    """Test ExternalRepoScanner functionality."""

    def test_is_github_url(self):
        """Test GitHub URL detection."""
        scanner = ExternalRepoScanner.__new__(ExternalRepoScanner)
        scanner.repo_source = "https://github.com/user/repo"
        assert scanner._is_github_url()

        scanner.repo_source = "/local/path"
        assert not scanner._is_github_url()

    def test_validate_github_url(self):
        """Test GitHub URL validation."""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            ExternalRepoScanner("https://github.com/invalid")

    def test_validate_github_url_valid(self):
        """Test valid GitHub URL."""
        scanner = ExternalRepoScanner.__new__(ExternalRepoScanner)
        scanner.repo_source = "https://github.com/user/repo"
        scanner._validate_github_url()
        assert scanner.repo_name == "github-user-repo"

    def test_validate_local_path_not_exists(self):
        """Test local path validation when path doesn't exist."""
        with pytest.raises(ValueError, match="Invalid source"):
            ExternalRepoScanner("/nonexistent/path")

    def test_validate_local_path_empty(self):
        """Test local path validation when directory is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Directory is empty"):
                ExternalRepoScanner(tmpdir)

    def test_validate_local_path_valid(self):
        """Test valid local path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            Path(tmpdir, "test.txt").touch()
            scanner = ExternalRepoScanner(tmpdir)
            assert scanner.repo_path == Path(tmpdir).resolve()

    def test_infer_languages(self):
        """Test language inference from extensions."""
        scanner = ExternalRepoScanner.__new__(ExternalRepoScanner)
        extensions = {".py", ".sql", ".js"}
        languages = scanner._infer_languages(extensions)
        assert "Python" in languages
        assert "SQL" in languages
        assert "JavaScript" in languages

    def test_scan_local_repo(self):
        """Test scanning a local repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test structure
            tmp_path = Path(tmpdir)
            tmp_path.joinpath("src").mkdir()
            tmp_path.joinpath("src/main.py").touch()
            tmp_path.joinpath("tests").mkdir()
            tmp_path.joinpath("tests/test.py").touch()
            tmp_path.joinpath("README.md").write_text("Test project")

            scanner = ExternalRepoScanner(tmpdir)
            result = scanner.scan()

            assert result["identifier"].startswith("local-")
            assert result["source_type"] == "local_path"
            assert result["repo_info"]["total_files"] >= 3
            assert "Python" in result["repo_info"]["languages_detected"]
            assert ".py" in result["repo_info"]["file_extensions_found"]


class TestExternalRepoIndexer:
    """Test ExternalRepoIndexer functionality."""

    def test_indexer_initialization(self):
        """Test indexer initialization creates directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repos_dir = Path(tmpdir) / "external-repos"
            indexer = ExternalRepoIndexer(repos_dir)
            assert repos_dir.exists()
            assert indexer.index_file.exists()

    def test_save_and_retrieve_repo(self):
        """Test saving and retrieving a learned repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repos_dir = Path(tmpdir) / "external-repos"
            indexer = ExternalRepoIndexer(repos_dir)

            metadata = {
                "identifier": "test-repo",
                "source": "https://github.com/test/repo",
                "source_type": "github_url",
                "scanned_at": "2026-09-23T10:00:00Z",
                "repo_info": {
                    "description": "Test",
                    "languages_detected": ["Python"],
                    "file_extensions_found": [".py"],
                    "total_files": 5,
                    "structure_summary": "src/ tests/",
                },
                "version_hash": "main",
            }

            analysis = {
                "extracted_by_user": "Test analysis",
                "analysis": "This is a test",
                "key_findings": ["Finding 1"],
            }

            repo_id = indexer.save_learned_repo(metadata, analysis)
            assert repo_id == "test-repo"

            retrieved = indexer.get_learned_repo(repo_id)
            assert retrieved is not None
            assert retrieved["source"] == "https://github.com/test/repo"
            assert retrieved["learning_summary"]["extracted_by_user"] == "Test analysis"

    def test_list_repos(self):
        """Test listing all learned repositories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repos_dir = Path(tmpdir) / "external-repos"
            indexer = ExternalRepoIndexer(repos_dir)

            # Save multiple repos
            for i in range(3):
                metadata = {
                    "identifier": f"test-repo-{i}",
                    "source": f"https://github.com/test/repo{i}",
                    "source_type": "github_url",
                    "scanned_at": "2026-09-23T10:00:00Z",
                    "repo_info": {
                        "description": f"Test {i}",
                        "languages_detected": ["Python"],
                        "file_extensions_found": [".py"],
                        "total_files": 5,
                        "structure_summary": "src/",
                    },
                    "version_hash": "main",
                }
                indexer.save_learned_repo(metadata, {"extracted_by_user": f"Test {i}"})

            repos = indexer.list_all()
            assert len(repos) == 3

    def test_search_by_source(self):
        """Test searching repository by source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repos_dir = Path(tmpdir) / "external-repos"
            indexer = ExternalRepoIndexer(repos_dir)

            metadata = {
                "identifier": "test-repo",
                "source": "https://github.com/test/repo",
                "source_type": "github_url",
                "scanned_at": "2026-09-23T10:00:00Z",
                "repo_info": {
                    "description": "Test",
                    "languages_detected": ["Python"],
                    "file_extensions_found": [".py"],
                    "total_files": 5,
                    "structure_summary": "src/",
                },
                "version_hash": "main",
            }

            indexer.save_learned_repo(metadata, {"extracted_by_user": "Test"})
            found_id = indexer.search_by_source("https://github.com/test/repo")
            assert found_id == "test-repo"

    def test_delete_repo(self):
        """Test deleting a learned repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repos_dir = Path(tmpdir) / "external-repos"
            indexer = ExternalRepoIndexer(repos_dir)

            metadata = {
                "identifier": "test-repo",
                "source": "https://github.com/test/repo",
                "source_type": "github_url",
                "scanned_at": "2026-09-23T10:00:00Z",
                "repo_info": {
                    "description": "Test",
                    "languages_detected": ["Python"],
                    "file_extensions_found": [".py"],
                    "total_files": 5,
                    "structure_summary": "src/",
                },
                "version_hash": "main",
            }

            indexer.save_learned_repo(metadata, {"extracted_by_user": "Test"})
            assert indexer.repo_exists("test-repo")

            deleted = indexer.delete_learned_repo("test-repo")
            assert deleted
            assert not indexer.repo_exists("test-repo")

    def test_get_context(self):
        """Test getting context for a learned repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repos_dir = Path(tmpdir) / "external-repos"
            indexer = ExternalRepoIndexer(repos_dir)

            metadata = {
                "identifier": "test-repo",
                "source": "https://github.com/test/repo",
                "source_type": "github_url",
                "scanned_at": "2026-09-23T10:00:00Z",
                "repo_info": {
                    "description": "Test",
                    "languages_detected": ["Python"],
                    "file_extensions_found": [".py"],
                    "total_files": 5,
                    "structure_summary": "src/",
                },
                "version_hash": "main",
            }

            analysis = {
                "extracted_by_user": "Test analysis",
                "analysis": "This is a test",
                "key_findings": ["Finding 1", "Finding 2"],
            }

            indexer.save_learned_repo(metadata, analysis)
            context = indexer.get_context("test-repo")
            assert context is not None
            assert "Extracted: Test analysis" in context
            assert "Finding 1" in context


@pytest.mark.unit
class TestIntegration:
    """Integration tests."""

    def test_scan_and_persist_local_repo(self):
        """Test full flow: scan local repo and persist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test repo
            repo_path = Path(tmpdir) / "test-repo"
            repo_path.mkdir()
            repo_path.joinpath("main.py").touch()
            repo_path.joinpath("test.py").touch()

            # Create external repos storage
            storage_path = Path(tmpdir) / "external-repos"

            # Scan
            scanner = ExternalRepoScanner(str(repo_path))
            metadata = scanner.scan()

            # Persist
            indexer = ExternalRepoIndexer(storage_path)
            repo_id = indexer.save_learned_repo(
                metadata,
                {"extracted_by_user": "Test", "analysis": "Full integration test"},
            )

            # Verify
            retrieved = indexer.get_learned_repo(repo_id)
            assert retrieved["source"] == str(repo_path)
            assert retrieved["repo_info"]["total_files"] >= 2
