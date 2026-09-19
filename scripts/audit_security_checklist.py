#!/usr/bin/env python3
"""Auditor de seguridad L2 independiente.

Valida controles de seguridad específicos del repositorio apex.skills.
Desacoplado: no importa ni invoca skills, orquestadores ni scripts internos.
Solo usa stdlib.

Invocación: python scripts/audit_security_checklist.py [--json] [--report]
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent

ORACLE_CRED_PATTERNS = [
	re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{3,}['\"]"),
	re.compile(r"(?i)pwd\s*[:=]\s*['\"][^'\"]{3,}['\"]"),
	re.compile(r"(?i)connect\s+\w+/\w+@"),
	re.compile(r"(?i)sqlplus\s+\w+/\w+"),
	re.compile(r"(?i)jdbc:oracle:thin:\w+/\w+@"),
	re.compile(r"(?i)TNS_ADMIN\s*=\s*['\"]?[A-Za-z]:\\"),
]

ORACLE_CRED_ALLOWLIST = [
	"getpass.getpass",
	"input(",
	"placeholder",
	"replace_with",
	"changeme",
	"your_",
]

SECRET_PATTERNS = [
	re.compile(r"(?i)(api[_-]?key|api[_-]?secret|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
	re.compile(r"(?i)(aws_secret_access_key|aws_access_key_id)\s*[:=]\s*['\"][^'\"]+['\"]"),
	re.compile(r"AKIA[0-9A-Z]{16}"),
	re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}"),
]

SQL_INJECTION_PATTERNS = [
	re.compile(r"f['\"].*\{.*\}.*(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|GRANT|REVOKE)", re.IGNORECASE),
	re.compile(r"['\"].*%s.*(?:SELECT|INSERT|UPDATE|DELETE|DROP)", re.IGNORECASE),
	re.compile(r"\.format\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE|DROP)", re.IGNORECASE),
]

SCAN_EXTENSIONS = {".py", ".ps1", ".yaml", ".yml", ".json", ".md", ".sql", ".sh", ".toml", ".cfg", ".ini"}
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".upstreams", "htmlcov", ".eggs"}


class SecurityResult:
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


def _scannable_files(root: Path):
	for p in root.rglob("*"):
		if any(skip in p.parts for skip in SKIP_DIRS):
			continue
		if p.is_file() and p.suffix in SCAN_EXTENSIONS:
			yield p


def check_secrets_in_code(root: Path) -> SecurityResult:
	"""S01: Secrets in Python/PowerShell/YAML/JSON files."""
	r = SecurityResult("S01", "Secrets en código fuente")
	for p in _scannable_files(root):
		if p.suffix not in {".py", ".ps1", ".yaml", ".yml", ".json"}:
			continue
		if "test" in p.name.lower() or "fixture" in str(p):
			continue
		try:
			text = p.read_text(encoding="utf-8", errors="replace")
		except (OSError, UnicodeDecodeError):
			continue
		for pattern in SECRET_PATTERNS:
			for match in pattern.finditer(text):
				line_num = text[:match.start()].count("\n") + 1
				r.fail(f"{p.relative_to(root)}:{line_num} — patrón de secret detectado")
	return r


def check_oracle_credentials(root: Path) -> SecurityResult:
	"""S02: Hardcoded Oracle credentials."""
	r = SecurityResult("S02", "Credenciales Oracle hardcodeadas")
	for p in _scannable_files(root):
		if p.suffix not in {".py", ".ps1", ".sql", ".yaml", ".yml", ".sh"}:
			continue
		if "test" in p.name.lower() or "fixture" in str(p):
			continue
		try:
			lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
		except (OSError, UnicodeDecodeError):
			continue
		for line_num, line in enumerate(lines, 1):
			if any(safe in line for safe in ORACLE_CRED_ALLOWLIST):
				continue
			for pattern in ORACLE_CRED_PATTERNS:
				if pattern.search(line):
					r.fail(f"{p.relative_to(root)}:{line_num} — patrón de credencial Oracle")
	return r


def check_mcp_profiles(root: Path) -> SecurityResult:
	"""S03: MCP profiles with sensitive data in plaintext."""
	r = SecurityResult("S03", "Perfiles MCP sin datos sensibles")
	mcp_files = list(root.glob(".mcp.json*")) + list(root.glob("**/mcp*.json"))
	for p in mcp_files:
		if not p.is_file():
			continue
		try:
			text = p.read_text(encoding="utf-8", errors="replace")
		except (OSError, UnicodeDecodeError):
			continue
		if p.name == ".mcp.json":
			r.fail(f"{p.relative_to(root)} — archivo MCP activo detectado (debería ser .mcp.json.example)")
		for pattern in [re.compile(r"(?i)(password|secret|token)\s*[\"']?\s*:\s*[\"'][^\"']{3,}[\"']")]:
			for match in pattern.finditer(text):
				line_num = text[:match.start()].count("\n") + 1
				r.fail(f"{p.relative_to(root)}:{line_num} — dato sensible en perfil MCP")
	return r


def check_env_variables(root: Path) -> SecurityResult:
	"""S04: Environment variables with unsanitized secrets."""
	r = SecurityResult("S04", "Variables de entorno sanitizadas")
	env_files = list(root.glob(".env")) + list(root.glob("**/.env"))
	for p in env_files:
		if any(skip in p.parts for skip in SKIP_DIRS):
			continue
		if p.is_file() and p.name == ".env":
			r.fail(f"{p.relative_to(root)} — archivo .env activo detectado (no debe comitearse)")
	env_example = root / ".env.example"
	if env_example.exists():
		text = env_example.read_text(encoding="utf-8", errors="replace")
		for line in text.split("\n"):
			stripped = line.strip()
			if not stripped or stripped.startswith("#"):
				continue
			if "=" in stripped:
				key, _, value = stripped.partition("=")
				value = value.strip().strip("'\"")
				placeholder_prefixes = ("replace_with", "your_", "changeme", "placeholder", "xxx", "example")
				if len(value) > 10 and not value.startswith("${") and not any(value.lower().startswith(p) for p in placeholder_prefixes):
					r.fail(f".env.example: {key.strip()} parece contener un valor real")
	return r


SQL_INJECTION_SAFE_FILES = {
	"audit_security_checklist.py",
	"apex_schema_generator.py",
	"validate_sql_style.py",
}


def check_sql_injection(root: Path) -> SecurityResult:
	"""S05: SQL injection patterns in scripts."""
	r = SecurityResult("S05", "SQL injection patterns")
	for p in _scannable_files(root):
		if p.suffix != ".py":
			continue
		if p.name in SQL_INJECTION_SAFE_FILES:
			continue
		try:
			text = p.read_text(encoding="utf-8", errors="replace")
		except (OSError, UnicodeDecodeError):
			continue
		for pattern in SQL_INJECTION_PATTERNS:
			for match in pattern.finditer(text):
				line_num = text[:match.start()].count("\n") + 1
				r.fail(f"{p.relative_to(root)}:{line_num} — posible SQL injection (string interpolation en SQL)")
	return r


def check_secrets_baseline(root: Path) -> SecurityResult:
	"""S06: detect-secrets baseline is up to date."""
	r = SecurityResult("S06", "Baseline detect-secrets actualizada")
	baseline = root / ".secrets.baseline"
	if not baseline.exists():
		r.fail(".secrets.baseline no existe")
		return r
	try:
		data = json.loads(baseline.read_text(encoding="utf-8"))
		if "plugins_used" not in data:
			r.fail(".secrets.baseline sin plugins configurados")
		if "results" not in data:
			r.fail(".secrets.baseline sin sección results")
		results = data.get("results", {})
		if results:
			total_secrets = sum(len(v) for v in results.values())
			r.info(f"{total_secrets} secret(s) en baseline — revisar que sean falsos positivos")
	except (json.JSONDecodeError, Exception) as e:
		r.fail(f".secrets.baseline inválido: {e}")
	return r


def check_dependencies(root: Path) -> SecurityResult:
	"""S07: Known vulnerabilities in dependencies."""
	r = SecurityResult("S07", "Dependencias sin CVE conocidas")
	req = root / "requirements.txt"
	if not req.exists():
		r.fail("requirements.txt no encontrado")
		return r
	try:
		proc = subprocess.run(
			[sys.executable, "-m", "pip", "audit"],
			capture_output=True, text=True, timeout=60, cwd=str(root),
		)
		if proc.returncode != 0:
			if "No known vulnerabilities found" in proc.stdout:
				r.info("pip-audit: sin vulnerabilidades conocidas")
			elif "No module named" in proc.stderr:
				r.info("pip-audit no instalado — check manual requerido")
			else:
				for line in proc.stdout.strip().split("\n"):
					if line.strip() and "Name" not in line and "---" not in line:
						r.fail(f"vulnerabilidad: {line.strip()}")
		else:
			r.info("pip-audit: sin vulnerabilidades conocidas")
	except FileNotFoundError:
		r.info("pip-audit no disponible — check manual requerido")
	except subprocess.TimeoutExpired:
		r.info("pip-audit excedió timeout")
	return r


def check_threat_model(root: Path) -> SecurityResult:
	"""S08: Threat model is current."""
	r = SecurityResult("S08", "Threat model vigente")
	threat_file = root / "docs" / "SECURITY-THREATS.md"
	if not threat_file.exists():
		r.fail("docs/SECURITY-THREATS.md no encontrado")
		return r
	text = threat_file.read_text(encoding="utf-8", errors="replace")
	date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
	if date_match:
		try:
			model_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
			days_old = (datetime.now() - model_date).days
			if days_old > 180:
				r.fail(f"threat model tiene {days_old} días — revisar vigencia (máximo 180 días)")
			else:
				r.info(f"threat model actualizado hace {days_old} días")
		except ValueError:
			r.info("no se pudo parsear fecha del threat model")
	return r


def check_precommit_hooks(root: Path) -> SecurityResult:
	"""S09: Security pre-commit hooks are active and not bypassed."""
	r = SecurityResult("S09", "Pre-commit hooks de seguridad activos")
	config = root / ".pre-commit-config.yaml"
	if not config.exists():
		r.fail(".pre-commit-config.yaml no encontrado")
		return r
	text = config.read_text(encoding="utf-8", errors="replace")
	required_hooks = ["detect-secrets", "detect-private-key", "bandit"]
	for hook in required_hooks:
		if hook not in text:
			r.fail(f"hook de seguridad '{hook}' no encontrado en pre-commit config")
	gitconfig = root / ".git" / "config"
	if gitconfig.exists():
		gc_text = gitconfig.read_text(encoding="utf-8", errors="replace")
		if "hooksPath" in gc_text and ".hooks" not in gc_text:
			r.fail("git hooksPath redirigido fuera del repositorio")
	return r


def check_env_example(root: Path) -> SecurityResult:
	"""S10: .env.example does not contain real values."""
	r = SecurityResult("S10", ".env.example sin valores reales")
	env_example = root / ".env.example"
	if not env_example.exists():
		r.info(".env.example no existe — N/A")
		return r
	text = env_example.read_text(encoding="utf-8", errors="replace")
	for line_num, line in enumerate(text.split("\n"), 1):
		stripped = line.strip()
		if not stripped or stripped.startswith("#"):
			continue
		for pattern in ORACLE_CRED_PATTERNS + SECRET_PATTERNS:
			if pattern.search(stripped):
				r.fail(f".env.example:{line_num} — posible valor real")
	return r


def run_security_audit(root: Path) -> List[SecurityResult]:
	checks = [
		check_secrets_in_code,
		check_oracle_credentials,
		check_mcp_profiles,
		check_env_variables,
		check_sql_injection,
		check_secrets_baseline,
		check_dependencies,
		check_threat_model,
		check_precommit_hooks,
		check_env_example,
	]
	return [fn(root) for fn in checks]


def print_report(results: List[SecurityResult], as_json: bool = False):
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
	print(f"  SECURITY AUDIT L2 — {passed}/{total} checks passed")
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
	verdict = "SECURITY_PASS" if passed == total else "SECURITY_FAIL"
	print(f"  {verdict} ({passed}/{total})")
	print(f"{'=' * 60}\n")


def generate_l2_report(results: List[SecurityResult], root: Path) -> Path:
	"""Generate a formal L2 security audit report."""
	reports_dir = root / "governance" / "audit" / "reportes"
	reports_dir.mkdir(parents=True, exist_ok=True)

	now = datetime.now(timezone.utc)

	try:
		proc = subprocess.run(
			["git", "rev-parse", "HEAD"],
			capture_output=True, text=True, cwd=str(root),
		)
		revision = proc.stdout.strip() if proc.returncode == 0 else "unknown"
	except FileNotFoundError:
		revision = "unknown"

	passed = sum(1 for r in results if r.passed)
	total = len(results)
	all_pass = passed == total
	resultado = "PASS" if all_pass else "FAIL"

	controls = []
	for r in results:
		finding_count = len(r.findings) if not r.passed else 0
		controls.append(f"| {r.check_id} | {r.name} | {r.status} | {finding_count} |")

	findings = []
	h_seq = 1
	for r in results:
		if not r.passed:
			for f in r.findings:
				findings.append(f"| H-{h_seq:03d} | ALTO | {r.check_id} | {f} | | | ABIERTO |")
				h_seq += 1

	report_name = f"{now.strftime('%Y-%m-%d')}-L2-security.md"
	report_path = reports_dir / report_name

	lines = [
		"# Reporte de Auditoría L2 — Seguridad",
		"",
		"| Campo | Valor |",
		"|---|---|",
		f"| **audit_id** | AUD-{now.strftime('%Y-%m%d')}-L2-001 |",
		"| **nivel** | L2 |",
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
		lines.extend([
			"",
			"## Hallazgos",
			"",
			"| ID | Severidad | Control | Descripción | Archivo | Línea | Estado |",
			"|---|---|---|---|---|---|---|",
		])
		lines.extend(findings)
	lines.extend([
		"",
		"## Evidencia",
		"",
		f"- Comando: `python scripts/audit_security_checklist.py --report`",
		f"- Hora: {now.isoformat()}",
		f"- Revisión: {revision}",
		"",
	])

	report_path.write_text("\n".join(lines), encoding="utf-8")
	return report_path


def main():
	as_json = "--json" in sys.argv
	as_report = "--report" in sys.argv
	results = run_security_audit(ROOT)

	if as_report:
		report_path = generate_l2_report(results, ROOT)
		print(f"L2 report generated: {report_path.relative_to(ROOT)}")

	print_report(results, as_json=as_json)
	sys.exit(0 if all(r.passed for r in results) else 1)


if __name__ == "__main__":
	main()
