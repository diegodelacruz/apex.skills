#!/usr/bin/env python3
"""Auditor post-implementación independiente.

Valida la integridad del repositorio apex.skills DESPUÉS de cualquier cambio.
Desacoplado: no importa ni invoca skills, orquestadores ni scripts internos.
Solo usa stdlib + yaml (única dependencia externa).

Invocación: python scripts/post_impl_audit.py [--fix] [--json]
Desde Claude: /post-audit
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#][^)]*)\)")
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
			capture_output=True, text=True, timeout=120, cwd=str(root),
		)
		last_line = [l for l in proc.stdout.strip().split("\n") if l.strip()][-1] if proc.stdout.strip() else ""
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
				r.fail(f"coverage threshold: pyproject.toml [coverage.report]={toml_report_threshold} vs pytest.ini={ini_threshold}")

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
		"CLAUDE.md", "README.md", "requirements.txt", "pytest.ini", "pyproject.toml",
		".pre-commit-config.yaml", ".bandit.yaml", ".gitignore",
		"skills/README.md", "skills/SKILLS-QUICK-REFERENCE.md",
		"docs/MANUAL-DE-USO.md", "docs/GUIA-CREAR-NUEVA-SKILL.md",
		"docs/POLITICA-EVOLUCION-ECOSISTEMA.md",
		"scripts/cli_utils.py", "scripts/apex_metadata.py", "scripts/path_setup.py",
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
			capture_output=True, text=True, cwd=str(root),
		)
		uncommitted = [l for l in proc.stdout.strip().split("\n") if l.strip()]
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
		data = [
			{"id": r.check_id, "name": r.name, "status": r.status, "findings": r.findings}
			for r in results
		]
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
			prefix = "     FAIL:" if not r.passed and f in [x for x in r.findings if r.findings] else "     info:"
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


def main():
	as_json = "--json" in sys.argv
	results = run_audit(ROOT)
	print_report(results, as_json=as_json)
	sys.exit(0 if all(r.passed for r in results) else 1)


if __name__ == "__main__":
	main()
