"""Unit tests for path_setup module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from path_setup import setup_scripts_path, setup_skills_path, setup_test_path


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
