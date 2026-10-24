"""Tests for the read-only semantic audit salvaged from PR #15 (SM08, SM09)."""

import shutil
import subprocess
from datetime import date
from pathlib import Path

import pytest

from scripts import audit_semantic_checks as semantic

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")


def _repo(tmp_path: Path, files: dict) -> Path:
    for relative, content in files.items():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    return tmp_path


def test_orphan_check_reports_unmentioned_scripts_and_docs_only(tmp_path):
    root = _repo(
        tmp_path,
        {
            "README.md": "See [guide](docs/guide.md) and run scripts/tool.py.\n",
            "docs/guide.md": "# Guide\n",
            "docs/forgotten.md": "# Forgotten\n",
            "scripts/__init__.py": "",
            "scripts/tool.py": "from helper import value\n",
            "scripts/helper.py": "value = 1\n",
            "scripts/unused.py": "print('x')\n",
        },
    )
    (root / "notes.md").write_text("scripts/unused.py docs/forgotten.md\n", encoding="utf-8")

    result = semantic.check_orphan_files(root, semantic.tracked_files(root))

    assert not result.passed
    assert result.findings == [
        "docs/forgotten.md: no other tracked file mentions it",
        "scripts/unused.py: no other tracked file mentions it",
    ]


def test_freshness_check_uses_labelled_dates_and_injected_today(tmp_path):
    root = _repo(
        tmp_path,
        {
            "CLAUDE.md": "**Last Updated:** 2026-01-01\n",
            "README.md": "Released on 2020-01-01 without a label.\n",
            "docs/current.md": "- **Fecha:** 2026-10-01\n",
            "docs/decisiones/old.md": "- **Fecha:** 2020-01-01\n",
        },
    )

    result = semantic.check_doc_freshness(root, semantic.tracked_files(root), today=date(2026, 10, 23))

    assert result.findings == ["CLAUDE.md: last labelled update 2026-01-01 is 295 days old"]
    assert result.notes == ["2 of 3 key docs declare a labelled update date"]


def test_audit_is_read_only_and_reports_with_exit_code(tmp_path, monkeypatch, capsys):
    root = _repo(tmp_path, {"README.md": "x\n", "docs/forgotten.md": "# Forgotten\n"})
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file() and ".git" not in path.parts}
    monkeypatch.setattr(semantic, "ROOT", root)

    assert semantic.main([]) == 1
    output = capsys.readouterr().out
    assert "SEMANTIC_FINDINGS: read-only report; nothing was changed" in output
    after = {path: path.read_bytes() for path in root.rglob("*") if path.is_file() and ".git" not in path.parts}
    assert after == before


def test_audit_reports_incomplete_when_git_listing_fails(monkeypatch, capsys):
    def fail(root, max_age_days):
        raise subprocess.CalledProcessError(128, ["git", "ls-files"])

    monkeypatch.setattr(semantic, "run", fail)

    assert semantic.main([]) == 2
    assert "SEMANTIC_INCOMPLETE" in capsys.readouterr().out


def test_update_upstreams_v2_has_no_unreachable_legacy_block():
    script = (ROOT / "scripts" / "Update-ApexSkillUpstreams-V2.ps1").read_text(encoding="utf-8")

    assert "$repos" not in script
    assert script.count("UPDATE_COMPLETE") == 1
