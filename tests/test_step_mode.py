"""Regression coverage for the controlled Oracle/APEX step modes."""

import re
from pathlib import Path

import scripts.apex_controlled_mcp as mcp

ROOT = Path(__file__).resolve().parents[1]
STEP_MODE = ROOT / "skills/apex/references/step-mode.md"
VALIDATION_QUERIES = ROOT / "skills/apex/references/step-validation-queries.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_step_mode_defines_all_user_decisions_and_boundaries():
    skill = _read(ROOT / "skills/apex/SKILL.md")
    protocol = _read(STEP_MODE)

    for phrase in (
        "Modo paso a paso / todos los pasos",
        "paso a paso",
        "todos los pasos",
        "lecturas y diagnósticos",
        "execute_readonly_batch",
    ):
        assert phrase in skill or phrase in protocol

    for phrase in (
        "ambiente",
        "objeto",
        "acción",
        "backup",
        "no se infiere",
        "línea base",
        "una vez por objeto",
        "no verificable",
        "sin rollback ni corrección automática",
    ):
        assert phrase in protocol.lower()

    assert "máximo 5 iteraciones" not in protocol.lower()
    assert "Paso N/M" in protocol


def test_step_mode_explicitly_reconciles_single_confirmation():
    skill = _read(ROOT / "skills/apex/SKILL.md")
    live = _read(ROOT / "skills/apex/references/live-change-protocol.md")
    protocol = _read(STEP_MODE)

    assert "una sola confirmación" in skill
    assert "no viola" in protocol
    assert "unidad de alcance" in protocol
    assert "paso a paso" in live
    assert "step-mode.md" in live


def test_adapters_point_to_existing_step_mode_reference():
    for path in (ROOT / "CLAUDE.md", ROOT / "AGENTS.md"):
        content = _read(path)
        assert "skills/apex/references/step-mode.md" in content
    assert STEP_MODE.is_file()


def test_validation_templates_are_single_read_only_selects():
    text = _read(VALIDATION_QUERIES)
    queries = [line.strip() for line in text.splitlines() if line.strip().lower().startswith("select ")]

    assert len(queries) >= 15
    for query in queries:
        mcp.validate_read_only_query(query)
        assert "{{" not in query
        assert ";" not in query
        assert re.search(r"'[^']+'", query)

    assert "select comments from all_tab_comments where owner = 'DATA' and table_name = 'T_APEX_LOG'" in queries


def test_all_steps_stops_after_the_first_execution_error():
    protocol = _read(STEP_MODE).lower()

    assert "primer error de ejecución" in protocol
    assert "no ejecutado" in protocol
    assert "no corrige ni revierte de forma automática" in protocol


def test_repository_change_instructions_have_no_unreconciled_step_mode_contradiction():
    candidates = [
        ROOT / "CLAUDE.md",
        ROOT / "AGENTS.md",
        ROOT / "skills/apex/SKILL.md",
        ROOT / "skills/apex/references/live-change-protocol.md",
        ROOT / "skills/oracle-data-change-governance-final/SKILL.md",
    ]
    patterns = re.compile(
        r"paso a paso|step-by-step|single confirmation|no solicites otra aprobación|do not ask again after that", re.I
    )
    hits = [(path, line) for path in candidates for line in _read(path).splitlines() if patterns.search(line)]

    assert hits
    assert all("step-mode.md" in _read(path) or path == STEP_MODE for path, _ in hits)
