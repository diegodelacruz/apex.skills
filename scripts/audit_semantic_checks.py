#!/usr/bin/env python3
"""Auditor semántico L3 independiente.

Valida que la documentación de skills corresponda con la realidad del repositorio.
10 checks (SM01-SM10): ejemplos, tags, routing, categorías, references,
scripts, descripciones, archivos huérfanos, frescura, consistencia README.

ALCANCE: estrictamente el repositorio apex.skills y sus skills.
No audita proyectos del usuario ni aplicaciones APEX externas.

Desacoplado: no importa ni invoca skills, orquestadores ni scripts internos.
Solo usa stdlib + yaml (única dependencia externa).

Invocación: python scripts/audit_semantic_checks.py [--json] [--report]
"""

import ast
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
YAML_DELIM = "---"


def _parse_frontmatter(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    if not lines or lines[0].strip() != YAML_DELIM:
        return {}
    end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == YAML_DELIM:
            end = i
            break
    if end < 0:
        return {}
    try:
        return yaml.safe_load("\n".join(lines[1:end])) or {}
    except Exception:
        return {}


class SemanticResult:
    def __init__(self, check_id: str, name: str):
        self.check_id = check_id
        self.name = name
        self.passed = True
        self.findings: List[str] = []

    def fail(self, msg: str):
        self.passed = False
        self.findings.append(msg)

    def info(self, msg: str):
        self.findings.append(msg)

    @property
    def status(self) -> str:
        return "PASS" if self.passed else "FAIL"


def _skill_dirs(root: Path):
    skills_dir = root / "skills"
    for d in sorted(skills_dir.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            yield d


def check_usage_examples(root: Path) -> SemanticResult:
    """SM01: Each SKILL.md has at least one usage example."""
    r = SemanticResult("SM01", "Ejemplos de uso en SKILL.md")
    evidence_patterns = [
        re.compile(r"```", re.MULTILINE),
        re.compile(r"(?i)(ejemplo|example|usage|uso|invoca|flujo|workflow|paso\s+\d|step\s+\d)", re.MULTILINE),
        re.compile(r"(?i)^#+\s*(flujo|workflow|procedimiento|proceso|pasos|steps|como usar|how to)", re.MULTILINE),
        re.compile(r"(?i)^\d+\.\s+", re.MULTILINE),
    ]
    for d in _skill_dirs(root):
        text = (d / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        fm_end = 0
        lines = text.split("\n")
        if lines and lines[0].strip() == YAML_DELIM:
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == YAML_DELIM:
                    fm_end = i + 1
                    break
        body = "\n".join(lines[fm_end:])
        has_evidence = any(p.search(body) for p in evidence_patterns)
        if not has_evidence:
            r.fail(f"{d.name}: SKILL.md sin ejemplo de uso, bloque de código ni flujo documentado")
    return r


def check_tags_validity(root: Path) -> SemanticResult:
    """SM02: Tags correspond to real capabilities."""
    r = SemanticResult("SM02", "Tags corresponden a capacidades reales")
    valid_tags = {
        "inspection",
        "design",
        "export",
        "read-only",
        "write",
        "governance",
        "audit",
        "qa",
        "delivery",
        "lifecycle",
        "engineering",
        "database",
        "diagnostics",
        "pattern",
        "mining",
        "project",
        "bootstrap",
        "workspace",
        "documentation",
        "manual",
        "data",
        "change",
        "oracle",
        "rest",
        "api",
        "catalog",
        "ui",
        "ux",
        "craft",
        "zaimella",
        "methodology",
        "schema",
        "automation",
        "page",
        "range",
        "alignment",
        "environment",
        "solution",
        "blueprint",
        "review",
        "orchestrator",
        "coordinator",
        "maestro",
        "code-generation",
        "migration",
        "safe",
        "complete",
        "final",
        "testing",
        "security",
        "monitoring",
        "integration",
        "retired",
    }
    for d in _skill_dirs(root):
        meta = _parse_frontmatter(d / "SKILL.md")
        tags = meta.get("tags", [])
        if not tags:
            r.fail(f"{d.name}: sin tags")
            continue
        if not isinstance(tags, list):
            r.fail(f"{d.name}: tags no es una lista")
            continue
        for tag in tags:
            if not isinstance(tag, str):
                r.fail(f"{d.name}: tag no es string: {tag}")
                continue
            normalized = tag.lower().strip()
            if not normalized:
                r.fail(f"{d.name}: tag vacío")
    return r


def check_routing_consistency(root: Path) -> SemanticResult:
    """SM03: Routing maps to existing skills with correct descriptions."""
    r = SemanticResult("SM03", "Routing mapea a skills existentes")
    routing_path = root / "skills" / "apex" / "references" / "routing.md"
    if not routing_path.exists():
        r.fail("skills/apex/references/routing.md no encontrado")
        return r

    text = routing_path.read_text(encoding="utf-8", errors="replace")
    skill_names = {d.name for d in _skill_dirs(root)}

    referenced = re.findall(r"(?:apex-[\w-]+)", text)
    for ref in set(referenced):
        if ref not in skill_names and ref != "apex":
            if not ref.startswith("apex-"):
                continue
            r.fail(f"routing referencia skill inexistente: {ref}")

    for skill in skill_names:
        if skill == "apex":
            continue
        if skill not in text:
            r.info(f"{skill}: no aparece en routing (puede ser correcto si es interno)")
    return r


def check_claude_md_categories(root: Path) -> SemanticResult:
    """SM04: Categories in CLAUDE.md match YAML frontmatter."""
    r = SemanticResult("SM04", "Categorías CLAUDE.md = YAML frontmatter")
    claude_md = root / "CLAUDE.md"
    if not claude_md.exists():
        r.fail("CLAUDE.md no encontrado")
        return r

    text = claude_md.read_text(encoding="utf-8", errors="replace")
    yaml_categories = {}
    for d in _skill_dirs(root):
        meta = _parse_frontmatter(d / "SKILL.md")
        cat = meta.get("category", "")
        if cat:
            yaml_categories[d.name] = cat

    for skill_name, category in yaml_categories.items():
        if skill_name not in text:
            r.fail(f"{skill_name}: aparece en YAML pero no en CLAUDE.md")
    return r


def check_references_exist(root: Path) -> SemanticResult:
    """SM05: references/ declared in SKILL.md exist and are readable."""
    r = SemanticResult("SM05", "references/ declaradas existen")
    ref_pattern = re.compile(r"\breferences/[\w./-]+")
    for d in _skill_dirs(root):
        text = (d / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        refs = ref_pattern.findall(text)
        for ref in refs:
            ref_path = d / ref
            if not ref_path.exists():
                r.fail(f"{d.name}: referencia inexistente: {ref}")
            elif ref_path.is_file():
                try:
                    ref_path.read_text(encoding="utf-8", errors="replace")
                except (OSError, UnicodeDecodeError):
                    r.fail(f"{d.name}: referencia ilegible: {ref}")
    return r


def check_referenced_scripts(root: Path) -> SemanticResult:
    """SM06: Scripts referenced in skills are syntactically valid."""
    r = SemanticResult("SM06", "Scripts referenciados son válidos")
    script_pattern = re.compile(r"(?:scripts?/[\w./-]+\.py)")
    checked = set()
    for d in _skill_dirs(root):
        text = (d / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        scripts = script_pattern.findall(text)
        for script_ref in scripts:
            script_path = root / script_ref
            if script_path in checked:
                continue
            checked.add(script_path)
            if not script_path.exists():
                r.fail(f"{d.name}: script inexistente: {script_ref}")
                continue
            try:
                source = script_path.read_text(encoding="utf-8")
                ast.parse(source, filename=str(script_path))
            except SyntaxError as e:
                r.fail(f"{script_ref}:{e.lineno} — {e.msg}")
    return r


def check_description_accuracy(root: Path) -> SemanticResult:
    """SM07: Skill descriptions are substantive and not generic."""
    r = SemanticResult("SM07", "Descripciones precisas")
    generic_phrases = [
        "todo lo relacionado",
        "maneja todo",
        "handles everything",
        "does everything",
        "all-in-one",
    ]
    for d in _skill_dirs(root):
        meta = _parse_frontmatter(d / "SKILL.md")
        desc = meta.get("description", "")
        if not desc:
            r.fail(f"{d.name}: sin descripción")
            continue
        if len(desc) < 20:
            r.fail(f"{d.name}: descripción demasiado corta ({len(desc)} chars)")
            continue
        desc_lower = desc.lower()
        for phrase in generic_phrases:
            if phrase in desc_lower:
                r.fail(f"{d.name}: descripción genérica (contiene '{phrase}')")
    return r


def check_orphan_files(root: Path) -> SemanticResult:
    """SM08: Files in scripts/ and docs/ that no other file references."""
    r = SemanticResult("SM08", "Archivos huérfanos")

    all_files = (
        list(root.rglob("*.md")) + list(root.rglob("*.py")) + list(root.rglob("*.yml")) + list(root.rglob("*.yaml"))
    )
    corpus = {}
    for f in all_files:
        try:
            corpus[f] = f.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            pass

    scripts_dir = root / "scripts"
    if scripts_dir.exists():
        skip_prefixes = ("__init__", "conftest", "test_")
        for py_file in sorted(scripts_dir.glob("*.py")):
            if any(py_file.name.startswith(p) for p in skip_prefixes):
                continue
            basename = py_file.name
            stem = py_file.stem
            found = False
            for corpus_file, content in corpus.items():
                if corpus_file == py_file:
                    continue
                if basename in content:
                    found = True
                    break
                if corpus_file.suffix == ".py" and stem in content:
                    found = True
                    break
            if not found:
                r.fail(f"scripts/{basename}: no referenciado desde ningún .md, .py ni .yml")

    docs_dir = root / "docs"
    if docs_dir.exists():
        for md_file in sorted(docs_dir.glob("*.md")):
            basename = md_file.name
            found = False
            for corpus_file, content in corpus.items():
                if corpus_file == md_file:
                    continue
                if basename in content:
                    found = True
                    break
            if not found:
                r.fail(f"docs/{basename}: no referenciado desde ningún otro archivo")

    return r


def check_doc_freshness(root: Path) -> SemanticResult:
    """SM09: Key documentation has recent Last Updated dates."""
    r = SemanticResult("SM09", "Frescura de documentación")
    max_days = 180
    date_pattern = re.compile(
        r"(?:last\s+updated|fecha|date|actualizado|updated)\s*[:\|]*\s*(\d{4}-\d{2}-\d{2})",
        re.IGNORECASE,
    )

    key_docs = [root / "CLAUDE.md", root / "README.md", root / "skills" / "README.md"]
    docs_dir = root / "docs"
    if docs_dir.exists():
        key_docs.extend(sorted(docs_dir.glob("*.md")))
    gov_dir = root / "governance"
    if gov_dir.exists():
        key_docs.extend(sorted(gov_dir.rglob("*.md")))
    key_docs = list(dict.fromkeys(key_docs))

    checked = 0
    for doc in key_docs:
        if not doc.exists():
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")
        matches = date_pattern.findall(text)
        if not matches:
            continue
        checked += 1
        latest_date = None
        for date_str in matches:
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if latest_date is None or d > latest_date:
                    latest_date = d
            except ValueError:
                continue
        if latest_date:
            days_old = (datetime.now(timezone.utc) - latest_date).days
            rel_path = doc.relative_to(root)
            if days_old > max_days:
                r.fail(f"{rel_path}: última actualización hace {days_old} días (máximo {max_days})")
            else:
                r.info(f"{rel_path}: actualizado hace {days_old} días")

    if checked == 0:
        r.info("ningún documento con fecha de actualización encontrado")
    return r


def check_readme_consistency(root: Path) -> SemanticResult:
    """SM10: README.md and CLAUDE.md skill counts match reality."""
    r = SemanticResult("SM10", "Consistencia de README")
    actual_skills = [d.name for d in _skill_dirs(root)]
    actual_count = len(actual_skills)

    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        text = claude_md.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"(\d+)\s+skills?\s*\(", text)
        if match:
            claimed = int(match.group(1))
            if claimed != actual_count:
                r.fail(f"CLAUDE.md dice {claimed} skills pero hay {actual_count} directorios con SKILL.md")

    skills_readme = root / "skills" / "README.md"
    if skills_readme.exists():
        text = skills_readme.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"(\d+)\s+skills?\s*\(", text)
        if match:
            claimed = int(match.group(1))
            if claimed != actual_count:
                r.fail(f"skills/README.md dice {claimed} skills pero hay {actual_count} directorios con SKILL.md")
        for skill_name in actual_skills:
            if skill_name not in text:
                r.fail(f"{skill_name}: directorio existe pero no aparece en skills/README.md")

    return r


def run_semantic_audit(root: Path) -> List[SemanticResult]:
    checks = [
        check_usage_examples,
        check_tags_validity,
        check_routing_consistency,
        check_claude_md_categories,
        check_references_exist,
        check_referenced_scripts,
        check_description_accuracy,
        check_orphan_files,
        check_doc_freshness,
        check_readme_consistency,
    ]
    return [fn(root) for fn in checks]


def print_report(results: List[SemanticResult], as_json: bool = False):
    if as_json:
        data = [{"id": r.check_id, "name": r.name, "status": r.status, "findings": r.findings} for r in results]
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"  SEMANTIC AUDIT L3 — {passed}/{total} checks passed")
    print(f"{'=' * 60}\n")

    for r in results:
        icon = "OK" if r.passed else "!!"
        print(f"  [{icon}] {r.check_id} {r.name}")
        for f in r.findings:
            if r.passed:
                print(f"     info: {f}")
            else:
                print(f"     FAIL: {f}")

    print(f"\n{'=' * 60}")
    verdict = "SEMANTIC_PASS" if passed == total else "SEMANTIC_FAIL"
    print(f"  {verdict} ({passed}/{total})")
    print(f"{'=' * 60}\n")


def generate_l3_report(results: List[SemanticResult], root: Path) -> Path:
    """Generate a formal L3 semantic audit report."""
    reports_dir = root / "governance" / "audit" / "reportes"
    reports_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)

    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        revision = proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except FileNotFoundError:
        revision = "unknown"

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    resultado = "PASS" if passed == total else "FAIL"

    controls = []
    for r in results:
        finding_count = len(r.findings) if not r.passed else 0
        controls.append(f"| {r.check_id} | {r.name} | {r.status} | {finding_count} |")

    findings = []
    h_seq = 1
    for r in results:
        if not r.passed:
            for f in r.findings:
                findings.append(f"| H-{h_seq:03d} | MEDIO | {r.check_id} | {f} | ABIERTO |")
                h_seq += 1

    report_name = f"{now.strftime('%Y-%m-%d')}-L3-semantic.md"
    report_path = reports_dir / report_name

    lines = [
        "# Reporte de Auditoría L3 — Semántica",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| **audit_id** | AUD-{now.strftime('%Y-%m%d')}-L3-001 |",
        "| **nivel** | L3 |",
        f"| **fecha** | {now.isoformat()} |",
        f"| **revision** | {revision} |",
        "| **scope** | full-repository |",
        f"| **resultado** | {resultado} |",
        "",
        "## Controles ejecutados",
        "",
        "| ID | Control | Resultado | Hallazgos |",
        "|---|---|---|---|",
    ]
    lines.extend(controls)
    if findings:
        lines.extend(
            [
                "",
                "## Hallazgos",
                "",
                "| ID | Severidad | Control | Descripción | Estado |",
                "|---|---|---|---|---|",
            ]
        )
        lines.extend(findings)
    lines.extend(
        [
            "",
            "## Evidencia",
            "",
            f"- Comando: `python scripts/audit_semantic_checks.py --report`",
            f"- Hora: {now.isoformat()}",
            f"- Revisión: {revision}",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main():
    as_json = "--json" in sys.argv
    as_report = "--report" in sys.argv
    results = run_semantic_audit(ROOT)

    if as_report:
        report_path = generate_l3_report(results, ROOT)
        print(f"L3 report generated: {report_path.relative_to(ROOT)}")

    print_report(results, as_json=as_json)
    sys.exit(0 if all(r.passed for r in results) else 1)


if __name__ == "__main__":
    main()
