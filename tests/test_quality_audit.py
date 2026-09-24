"""Tests for the repository-level, agent-neutral quality audit."""

import importlib
from pathlib import Path

audit_module = importlib.import_module("scripts.audit_quality_score")


def audit_result() -> dict:
    return audit_module.run()


def test_quality_audit_has_complete_score() -> None:
    result = audit_result()
    assert result["maximum"] == 100
    assert len(result["checks"]) == 9


def test_quality_audit_current_repository_passes() -> None:
    result = audit_result()
    assert result["gates_pass"] is True
    assert result["score"] == 100


def test_skill_and_catalog_checks_use_current_inventory() -> None:
    result = audit_result()
    skill_count = len(list(Path("skills").glob("*/SKILL.md")))
    assert result["checks"][0]["evidence"] == f"{skill_count} SKILL.md files inspected"
    assert result["checks"][1]["passed"] is True
