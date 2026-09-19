#!/usr/bin/env python3
"""Auditor post-implementación independiente.

Valida la integridad del repositorio apex.skills DESPUÉS de cualquier cambio.
Desacoplado: no importa ni invoca skills, orquestadores ni scripts internos.
Solo usa stdlib + yaml (única dependencia externa).

Invocación: python scripts/post_impl_audit.py [--fix] [--json] [--report]
Desde Claude: /post-audit
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
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#][^)]*)\)")
YAML_DELIM = "---"

L1_CONTROL_MAP = {
    "P01": "L1-06",
    "P02": "L1-06",
    "P03": "L1-04",
    "P04": "L1-01",
    "P05": "L1-05",
    "P06": "L1-07",
    "P07": "L1-08",
    "P08": "L1-09",
    "P09": "L1-07",
    "P10": "L1-10",
}


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


class AuditResult:
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


def check_python_syntax(root: Path) -> AuditResult:
    r = AuditResult("P01", "Sintaxis Python")
    for py in root.joinpath("scripts").rglob("*.py"):
        try:
            ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError as e:
            r.fail(f"{py.relative_to(root)}:{e.lineno} — {e.msg}")
    for py in root.joinpath("tests").rglob("*.py"):
        try:
            ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError as e:
            r.fail(f"{py.relative_to(root)}:{e.lineno} — {e.msg}")
    return r


def check_tests(root: Path) -> AuditResult:
    r = AuditResult("P02", "Suite de tests")
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line", "--no-header"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(root),
        )
        last_line = [ln for ln in proc.stdout.strip().split("\n") if ln.strip()][-1] if proc.stdout.strip() else ""
        r.info(last_line)
        if proc.returncode != 0:
            failed = re.findall(r"FAILED (tests/\S+)", proc.stdout)
            for f in failed:
                r.fail(f"test fallido: {f}")
            if not failed:
                r.fail(f"pytest retornó código {proc.returncode}")
    except FileNotFoundError:
        r.fail("pytest no encontrado")
    except subprocess.TimeoutExpired:
        r.fail("tests excedieron 120s de timeout")
    return r


STANDALONE_COMMANDS = {"post-audit"}


def check_skill_registry(root: Path) -> AuditResult:
    r = AuditResult("P03", "Registro de skills")
    skills_dir = root / "skills"
    commands_dir = root / ".claude" / "commands"
    skill_dirs = {d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()}
    command_files = {f.stem for f in commands_dir.glob("*.md")} if commands_dir.exists() else set()

    for skill in sorted(skill_dirs):
        if skill not in command_files:
            r.fail(f"skill '{skill}' sin comando en .claude/commands/")
    for cmd in sorted(command_files - STANDALONE_COMMANDS):
        if cmd not in skill_dirs:
            r.fail(f"comando '{cmd}' sin directorio de skill")
    return r


def check_frontmatter(root: Path) -> AuditResult:
    r = AuditResult("P04", "Frontmatter YAML")
    required_fields = {"name", "description", "order", "tags"}
    skills_dir = root / "skills"
    orders = {}
    for d in sorted(skills_dir.iterdir()):
        skill_md = d / "SKILL.md"
        if not d.is_dir() or not skill_md.exists():
            continue
        meta = _parse_frontmatter(skill_md)
        if not meta:
            r.fail(f"{d.name}: frontmatter vacío o inválido")
            continue
        for field in required_fields:
            if field not in meta:
                r.fail(f"{d.name}: falta campo '{field}'")
        order = meta.get("order")
        if order is not None:
            if order in orders:
                r.fail(f"{d.name}: order {order} duplicado con {orders[order]}")
            orders[order] = d.name
    return r


def check_markdown_links(root: Path) -> AuditResult:
    r = AuditResult("P05", "Enlaces Markdown")
    scan_dirs = [root / "docs", root / "skills"]
    for base in scan_dirs:
        if not base.exists():
            continue
        for md in base.rglob("*.md"):
            text = md.read_text(encoding="utf-8", errors="replace")
            for target in LINK_RE.findall(text):
                target = target.split("#", 1)[0].strip()
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (md.parent / target).resolve()
                if not resolved.exists():
                    r.fail(f"{md.relative_to(root)} -> {target}")
    return r


def check_config_consistency(root: Path) -> AuditResult:
    r = AuditResult("P06", "Consistencia de configuración")
    pytest_ini = root / "pytest.ini"
    pyproject = root / "pyproject.toml"

    ini_threshold = None
    toml_threshold = None

    if pytest_ini.exists():
        for line in pytest_ini.read_text(encoding="utf-8").split("\n"):
            m = re.search(r"--cov-fail-under=(\d+)", line)
            if m:
                ini_threshold = int(m.group(1))

    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        m = re.search(r"--cov-fail-under=(\d+)", text)
        if m:
            toml_threshold = int(m.group(1))
        m2 = re.search(r"fail_under\s*=\s*(\d+)", text)
        toml_report_threshold = int(m2.group(1)) if m2 else None
        if toml_report_threshold is not None and ini_threshold is not None:
            if toml_report_threshold != ini_threshold:
                r.fail(
                    f"coverage threshold: pyproject.toml [coverage.report]="
                    f"{toml_report_threshold} vs pytest.ini={ini_threshold}"
                )

    if ini_threshold is not None and toml_threshold is not None:
        if ini_threshold != toml_threshold:
            r.fail(f"coverage threshold: pytest.ini={ini_threshold} vs pyproject.toml [pytest]={toml_threshold}")

    claude_md = root / "CLAUDE.md"
    readme = root / "README.md"
    skills_readme = root / "skills" / "README.md"
    counts = {}
    for f in [claude_md, readme, skills_readme]:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"(\d+)\s*skills?\b", text, re.IGNORECASE)
        if m:
            counts[f.name] = int(m.group(1))
    values = list(counts.values())
    if values and len(set(values)) > 1:
        detail = ", ".join(f"{k}={v}" for k, v in counts.items())
        r.fail(f"conteo de skills inconsistente: {detail}")
    return r


def check_imports(root: Path) -> AuditResult:
    r = AuditResult("P07", "Coherencia de imports")
    scripts_dir = root / "scripts"
    bare_imports = []
    qualified_imports = []
    for py in scripts_dir.glob("*.py"):
        if py.name == "__init__.py":
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#") or not stripped:
                continue
            if re.match(r"from\s+(cli_utils|apex_metadata|path_setup)\s+import", stripped):
                bare_imports.append(f"{py.name}: {stripped.split('#')[0].strip()}")
            elif re.match(r"from\s+scripts\.(cli_utils|apex_metadata|path_setup)\s+import", stripped):
                qualified_imports.append(py.name)
    if bare_imports and qualified_imports:
        r.fail(f"imports mixtos: bare en {[b.split(':')[0] for b in bare_imports]}, qualified en {qualified_imports}")
    return r


def check_required_files(root: Path) -> AuditResult:
    r = AuditResult("P08", "Archivos requeridos")
    required = [
        "CLAUDE.md",
        "README.md",
        "requirements.txt",
        "pytest.ini",
        "pyproject.toml",
        ".pre-commit-config.yaml",
        ".bandit.yaml",
        ".gitignore",
        "skills/README.md",
        "skills/SKILLS-QUICK-REFERENCE.md",
        "docs/MANUAL-DE-USO.md",
        "docs/GUIA-CREAR-NUEVA-SKILL.md",
        "docs/POLITICA-EVOLUCION-ECOSISTEMA.md",
        "scripts/cli_utils.py",
        "scripts/apex_metadata.py",
        "scripts/path_setup.py",
        ".claude/settings.json",
    ]
    for rel in required:
        if not (root / rel).exists():
            r.fail(f"falta: {rel}")
    return r


def check_secrets_baseline(root: Path) -> AuditResult:
    r = AuditResult("P09", "Baseline de secretos")
    baseline = root / ".secrets.baseline"
    if not baseline.exists():
        r.fail(".secrets.baseline no existe")
        return r
    try:
        data = json.loads(baseline.read_text(encoding="utf-8"))
        if "results" not in data:
            r.fail(".secrets.baseline sin sección 'results'")
    except (json.JSONDecodeError, Exception) as e:
        r.fail(f".secrets.baseline inválido: {e}")
    return r


def check_git_status(root: Path) -> AuditResult:
    r = AuditResult("P10", "Estado Git")
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        uncommitted = [ln for ln in proc.stdout.strip().split("\n") if ln.strip()]
        if uncommitted:
            r.info(f"{len(uncommitted)} archivo(s) sin commit")
            for f in uncommitted[:5]:
                r.info(f"  {f}")
    except FileNotFoundError:
        r.fail("git no disponible")
    return r


def run_audit(root: Path) -> List[AuditResult]:
    checks = [
        check_python_syntax,
        check_tests,
        check_skill_registry,
        check_frontmatter,
        check_markdown_links,
        check_config_consistency,
        check_imports,
        check_required_files,
        check_secrets_baseline,
        check_git_status,
    ]
    return [fn(root) for fn in checks]


def print_report(results: List[AuditResult], as_json: bool = False):
    if as_json:
        data = [{"id": r.check_id, "name": r.name, "status": r.status, "findings": r.findings} for r in results]
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    print(f"\n{'=' * 60}")
    print(f"  POST-IMPLEMENTATION AUDIT — {passed}/{total} checks passed")
    print(f"{'=' * 60}\n")

    for r in results:
        icon = "OK" if r.passed else "!!"
        print(f"  [{icon}] {r.check_id} {r.name}")
        for f in r.findings:
            if f.startswith("  "):
                print(f"          {f}")
            elif r.passed:
                print(f"     info: {f}")
            else:
                print(f"     FAIL: {f}")

    print(f"\n{'=' * 60}")
    verdict = "AUDIT_PASS" if passed == total else "AUDIT_FAIL"
    print(f"  {verdict} ({passed}/{total})")
    print(f"{'=' * 60}\n")


def _get_git_revision(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        return proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except FileNotFoundError:
        return "unknown"


def _get_git_user(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%an <%ae>"],
            capture_output=True,
            text=True,
            cwd=str(root),
        )
        return proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except FileNotFoundError:
        return "unknown"


def _next_audit_id(registry_path: Path) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m%d")
    seq = 1
    if registry_path.exists():
        text = registry_path.read_text(encoding="utf-8", errors="replace")
        existing = re.findall(rf"AUD-{today}-L1-(\d+)", text)
        if existing:
            seq = max(int(x) for x in existing) + 1
    return f"AUD-{today}-L1-{seq:03d}"


def _severity_for_check(check_id: str) -> str:
    critical = {"P01", "P03", "P09"}
    high = {"P02", "P04", "P05"}
    if check_id in critical:
        return "CRITICO"
    if check_id in high:
        return "ALTO"
    return "MEDIO"


def generate_l1_report(results: List[AuditResult], root: Path) -> Path:
    """Generate a formal L1 audit report in governance/audit/reportes/."""
    reports_dir = root / "governance" / "audit" / "reportes"
    reports_dir.mkdir(parents=True, exist_ok=True)
    registry_path = root / "governance" / "audit" / "REGISTRO-AUDITORIAS.md"

    now = datetime.now(timezone.utc)
    revision = _get_git_revision(root)
    auditor = _get_git_user(root)
    audit_id = _next_audit_id(registry_path)

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    all_pass = passed == total
    has_info = any(r.findings for r in results if r.passed)

    if all_pass and has_info:
        resultado = "PASS_WITH_OBSERVATIONS"
    elif all_pass:
        resultado = "PASS"
    else:
        resultado = "FAIL"

    findings_table = []
    h_seq = 1
    for r in results:
        if not r.passed:
            for f in r.findings:
                severity = _severity_for_check(r.check_id)
                control = L1_CONTROL_MAP.get(r.check_id, r.check_id)
                findings_table.append(f"| H-{h_seq:03d} | {severity} | {control} | {f} | | ABIERTO |")
                h_seq += 1

    controls_table = []
    for r in results:
        control_id = L1_CONTROL_MAP.get(r.check_id, r.check_id)
        finding_count = len(r.findings) if not r.passed else 0
        controls_table.append(f"| {control_id} | {r.name} | {r.status} | {finding_count} hallazgo(s) |")

    report_name = f"{now.strftime('%Y-%m-%d')}-L1-full.md"
    report_path = reports_dir / report_name

    lines = [
        "# Reporte de Auditoría L1 — Estructura e Integridad",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| **audit_id** | {audit_id} |",
        "| **nivel** | L1 |",
        f"| **fecha** | {now.isoformat()} |",
        f"| **revision** | {revision} |",
        "| **scope** | full-repository |",
        f"| **auditor** | {auditor} |",
        f"| **resultado** | {resultado} |",
        "",
        "## Resumen ejecutivo",
        "",
        f"Auditoría L1 automatizada sobre el repositorio completo. {passed}/{total} controles pasaron.",
        "" if all_pass else f"{total - passed} control(es) fallaron y requieren atención.",
        "",
        "## Controles ejecutados",
        "",
        "| ID | Control | Resultado | Hallazgos |",
        "|---|---|---|---|",
    ]
    lines.extend(controls_table)

    if findings_table:
        lines.extend(
            [
                "",
                "## Hallazgos",
                "",
                "| ID | Severidad | Control | Descripción | Archivo | Estado |",
                "|---|---|---|---|---|---|",
            ]
        )
        lines.extend(findings_table)

    lines.extend(
        [
            "",
            "## Evidencia",
            "",
            "- Comando ejecutado: `python scripts/post_impl_audit.py --report`",
            f"- Hora de ejecución: {now.isoformat()}",
            f"- Revisión: {revision}",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")

    _update_registry(registry_path, audit_id, now, revision, auditor, resultado, len(findings_table), report_name)

    return report_path


def _update_registry(
    registry_path: Path,
    audit_id: str,
    now: datetime,
    revision: str,
    auditor: str,
    resultado: str,
    finding_count: int,
    report_name: str,
):
    """Append an entry to the central audit registry."""
    if not registry_path.exists():
        return
    text = registry_path.read_text(encoding="utf-8")
    placeholder = "| *(vacío — se pobla con cada auditoría ejecutada)* | | | | | | | | |"
    entry = (
        f"| {audit_id} | L1 | {now.strftime('%Y-%m-%d')} | {revision[:8]} "
        f"| full-repository | {auditor} | {resultado} | {finding_count} "
        f"| `reportes/{report_name}` |"
    )
    if placeholder in text:
        text = text.replace(placeholder, entry)
    else:
        text = text.rstrip() + "\n" + entry + "\n"
    registry_path.write_text(text, encoding="utf-8")


def main():
    as_json = "--json" in sys.argv
    as_report = "--report" in sys.argv
    results = run_audit(ROOT)

    if as_report:
        report_path = generate_l1_report(results, ROOT)
        print(f"L1 report generated: {report_path.relative_to(ROOT)}")

    print_report(results, as_json=as_json)
    sys.exit(0 if all(r.passed for r in results) else 1)


if __name__ == "__main__":
    main()
