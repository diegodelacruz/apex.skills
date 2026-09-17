"""Unit tests for path_setup module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from path_setup import (  # noqa: E402
    get_repo_root,
    get_script_dir,
    setup_scripts_path,
    setup_skills_path,
    setup_test_path,
)


class TestPathSetup:
    """Tests for path setup functions."""

    @pytest.mark.unit
    def test_setup_scripts_path(self):
        """Setup scripts path."""
        # Simulate __file__ from a script in scripts/
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "dummy.py"
        result = setup_scripts_path(str(script_path))

        assert result.name == "scripts"
        assert str(result) in sys.path or result.parent.name == "apex.skills"

    @pytest.mark.unit
    def test_setup_scripts_path_returns_path(self):
        """Verify setup_scripts_path returns a Path object."""
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "test.py"
        result = setup_scripts_path(str(script_path))

        assert isinstance(result, Path)
        assert result.is_dir()

    @pytest.mark.unit
    def test_setup_test_path(self):
        """Setup test path."""
        result = setup_test_path(__file__)

        assert result.name == "scripts"
        assert result in [Path(p) for p in sys.path]

    @pytest.mark.unit
    def test_setup_test_path_returns_path(self):
        """Verify setup_test_path returns a Path object."""
        result = setup_test_path(__file__)

        assert isinstance(result, Path)
        assert result.name == "scripts"

    @pytest.mark.unit
    def test_path_not_duplicated(self):
        """Verify path is not added twice."""
        script_path = Path(__file__).resolve().parent.parent / "scripts" / "test.py"

        # Add path first time
        setup_scripts_path(str(script_path))
        count_first = sys.path.count(str(script_path.parent))

        # Add path second time
        setup_scripts_path(str(script_path))
        count_second = sys.path.count(str(script_path.parent))

        # Should be same count (not added twice)
        assert count_first == count_second

    @pytest.mark.unit
    def test_setup_test_path_idempotent(self):
        """Verify setup_test_path is idempotent."""
        result1 = setup_test_path(__file__)
        result2 = setup_test_path(__file__)

        assert result1 == result2
        assert isinstance(result1, Path)
        assert isinstance(result2, Path)

    @pytest.mark.unit
    def test_get_repo_root(self):
        """Get repository root from test file."""
        result = get_repo_root(__file__)

        assert result.name == "apex.skills"
        assert (result / ".git").exists()
        assert (result / "CLAUDE.md").exists()

    @pytest.mark.unit
    def test_get_repo_root_from_scripts_dir(self):
        """Get repository root from scripts directory."""
        script_path = Path(__file__).resolve().parent.parent / "scripts"
        result = get_repo_root(str(script_path))

        assert result.name == "apex.skills"
        assert (result / "scripts").exists()

    @pytest.mark.unit
    def test_get_repo_root_from_directory(self):
        """Verify get_repo_root works when given a directory."""
        result = get_repo_root(str(Path(__file__).resolve().parent))

        assert result.name == "apex.skills"
        assert (result / ".git").is_dir()

    @pytest.mark.unit
    def test_get_repo_root_not_found_raises_error(self):
        """Verify get_repo_root raises RuntimeError when .git not found."""
        # Use a temporary directory without .git
        with pytest.raises(RuntimeError, match="Could not find repository root"):
            get_repo_root("/tmp/nonexistent/path")

    @pytest.mark.unit
    def test_get_script_dir(self):
        """Get scripts directory."""
        result = get_script_dir()

        assert result.name == "scripts"
        assert (result / "cli_utils.py").exists()
        assert (result / "path_setup.py").exists()

    @pytest.mark.unit
    def test_get_script_dir_returns_path_object(self):
        """Verify get_script_dir returns Path object."""
        result = get_script_dir()

        assert isinstance(result, Path)
        assert result.is_dir()

    @pytest.mark.unit
    def test_setup_skills_path(self):
        """Setup skills path from a skill script location."""
        # Simulate __file__ from a skill script:
        # skills/apex-export-qa-safe/scripts/validate.py
        skill_script = (
            Path(__file__).resolve().parent.parent / "skills" / "apex-export-qa-safe" / "scripts" / "validate.py"
        )
        result = setup_skills_path(str(skill_script))

        assert result.name == "scripts"
        assert str(result) in sys.path
        assert (result / "path_setup.py").exists()

    @pytest.mark.unit
    def test_setup_skills_path_idempotent(self):
        """Verify setup_skills_path is idempotent."""
        skill_script = (
            Path(__file__).resolve().parent.parent / "skills" / "apex-export-qa-safe" / "scripts" / "validate.py"
        )
        result1 = setup_skills_path(str(skill_script))
        result2 = setup_skills_path(str(skill_script))

        assert result1 == result2
