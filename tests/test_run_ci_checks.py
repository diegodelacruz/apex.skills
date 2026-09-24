"""Tests for the local CI runner's patch whitespace validation."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from run_ci_checks import run_whitespace_check  # noqa: E402


def initialize_git_repo(path: Path) -> None:
    """Create an isolated Git repository for whitespace checks."""
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)


@pytest.mark.unit
def test_whitespace_check_includes_new_untracked_files(tmp_path):
    """Detect trailing spaces in new files that Git diff does not include."""
    initialize_git_repo(tmp_path)
    (tmp_path / "new.md").write_text("line with trailing space \n", encoding="utf-8")

    assert run_whitespace_check(tmp_path) == 1


@pytest.mark.unit
def test_whitespace_check_includes_staged_files(tmp_path):
    """Detect trailing spaces in staged files."""
    initialize_git_repo(tmp_path)
    path = tmp_path / "staged.md"
    path.write_text("line with trailing tab\t\n", encoding="utf-8")
    subprocess.run(["git", "add", "staged.md"], cwd=tmp_path, check=True)

    assert run_whitespace_check(tmp_path) == 2
