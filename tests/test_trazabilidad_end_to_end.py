"""Regression coverage for the Trazabilidad End-to-End diagnostic method."""

import re
from pathlib import Path

import scripts.apex_controlled_mcp as mcp

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills/apex-database-diagnostics"
CORE = SKILL_DIR / "references/trazabilidad-end-to-end.md"
ADAPTER = SKILL_DIR / "references/trazabilidad-adaptador-oracle-apex.md"
TEMPLATE = SKILL_DIR / "assets/mapa-trazabilidad.template.md"
CODES = (
    "D0 NO_EXISTE_EN_FUENTE",
    "D1 NO_LEIDO",
    "D2 LEIDO_EXCLUIDO",
    "D3 TRANSFORMADO",
    "D4 PERSISTIDO_NO_CONSOLIDADO",
    "D5 CONSOLIDADO_NO_VISIBLE",
    "D6 AGREGADO_NETEADO",
    "D7 PENDIENTE",
    "DX EXPECTATIVA_INCORRECTA",
)
STATES = ("NO_VERIFICADO", "PRESENTE", "ALTERADO", "AUSENTE", "AGREGADO", "NETEADO", "PENDIENTE", "NO_OBSERVABLE")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sql_queries(text: str) -> list[str]:
    blocks = re.findall(r"```sql\n(.*?)```", text, re.S)
    return [
        line.strip() for block in blocks for line in block.splitlines() if line.strip().lower().startswith("select ")
    ]


def test_core_method_is_domain_agnostic():
    body = re.sub(r"\]\([^)]*\)", "]", _read(CORE))

    for term in ("APEX", "Oracle", "ALL_", "SQLcl", "WWV_FLOW", "execute_readonly"):
        assert term not in body, term


def test_core_defines_contract_states_taxonomy_and_closure_rules():
    text = _read(CORE)
    lower = text.lower()

    for code in CODES:
        assert code in text
    for state in STATES:
        assert f"`{state}`" in text
    for phrase in (
        "registro testigo",
        "testigo de control",
        "resultado esperado",
        "resultado observado",
        "primera divergencia",
        "hacia atrás",
        "hacia adelante",
        "bisección",
        "causa raíz confirmada",
        "causa probable",
        "limitación de evidencia",
        "regla anti-configuración",
        "solo lectura",
        "modo ligero",
        "reglas de costo",
        "linaje de llaves",
        "d1–d6 frente a dx",
        "no se elige `dx` en silencio",
        "nunca `ausente`",
    ):
        assert phrase in lower, phrase


def test_divergence_uses_conformity_not_mere_presence():
    lower = _read(CORE).lower()

    assert "la divergencia se mide contra la conformidad, no contra `presente`" in lower
    assert "[última conforme, primera no conforme]" in lower
    assert "una agregación o un neteo correctos y verificados" in lower
    assert "un valor distinto o un duplicado en en" in lower
    assert "conforme:" in _read(TEMPLATE).lower()


def test_control_record_is_mandatory_for_confirmed_root_cause():
    lower = _read(CORE).lower()

    assert "| **testigo de control**" in lower
    assert "no existe testigo de control" in lower
    assert "evaluado sobre el testigo de control" in lower


def test_template_is_markdown_only_with_required_sections():
    text = _read(TEMPLATE)

    for section in (
        "## Encabezado",
        "## Etapas",
        "## Linaje de llaves",
        "## Ramas podadas",
        "## Evidencia por etapa",
        "## Veredicto",
    ):
        assert section in text
    for field in ("Registro testigo", "Testigo de control", "Resultado esperado", "Resultado observado"):
        assert field in text
    for certainty in ("causa raíz confirmada", "causa probable", "limitación de evidencia"):
        assert certainty in text
    for code in CODES:
        assert code in text
    assert "```yaml" not in text


def test_adapter_probes_are_bounded_single_line_read_only_selects():
    queries = _sql_queries(_read(ADAPTER))

    assert len(queries) >= 15
    for query in queries:
        mcp.validate_read_only_query(query)
        assert set(re.findall(r":([a-z_]+)", query)) <= {"application_id", "page_id"}
        assert "wwv_flow" not in query.lower()
        assert "select *" not in query.lower()
        assert re.search(r"fetch first \d+ rows only|where .*(=|like)", query.lower()), query


def test_adapters_and_routing_point_to_existing_method_files():
    skill = _read(SKILL_DIR / "SKILL.md")
    for target in (CORE, ADAPTER, TEMPLATE):
        assert target.is_file()
        assert target.relative_to(SKILL_DIR).as_posix() in skill

    core_path = "skills/apex-database-diagnostics/references/trazabilidad-end-to-end.md"
    for path in (ROOT / "CLAUDE.md", ROOT / "AGENTS.md", ROOT / ".claude/commands/apex-database-diagnostics.md"):
        assert core_path in _read(path), path
    assert "references/trazabilidad-end-to-end.md" in _read(SKILL_DIR / "agents/openai.yaml")
    assert "trazabilidad-end-to-end.md" in _read(ROOT / "skills/apex/references/routing.md")
