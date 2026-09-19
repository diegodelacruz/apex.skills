#!/usr/bin/env python3
"""Auditoría desacoplada unificada (L1 + L2 + L3).

Punto de entrada único para la auditoría independiente del repositorio
apex.skills. Ejecuta los tres niveles automatizables en secuencia y
produce un veredicto consolidado.

ALCANCE: estrictamente el repositorio apex.skills y sus skills.
No audita proyectos del usuario ni aplicaciones APEX externas.

DESACOPLAMIENTO: no importa ni invoca skills, orquestadores ni scripts
internos del framework (cli_utils, apex_metadata, etc.).
Solo usa stdlib + subprocess para orquestar los auditores de cada nivel.
El repositorio no es juez y parte.

Invocación:
    python scripts/audit_desacoplada.py              # Todos los niveles
    python scripts/audit_desacoplada.py --level L1   # Solo L1
    python scripts/audit_desacoplada.py --level L2   # Solo L2
    python scripts/audit_desacoplada.py --level L3   # Solo L3
    python scripts/audit_desacoplada.py --report     # Con reportes formales
    python scripts/audit_desacoplada.py --json       # Salida JSON

Desde Claude: /post-audit
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LEVELS = {
	"L1": {
		"script": "scripts/post_impl_audit.py",
		"name": "Estructura e Integridad",
		"description": "Sintaxis, tests, skills, frontmatter, enlaces, config, imports, archivos, secrets, git",
	},
	"L2": {
		"script": "scripts/audit_security_checklist.py",
		"name": "Seguridad",
		"description": "Secrets, Oracle creds, MCP, env vars, SQL injection, CVE, threat model, hooks",
	},
	"L3": {
		"script": "scripts/audit_semantic_checks.py",
		"name": "Semántica",
		"description": "Ejemplos, tags, routing, categorías, references, scripts referenciados, descripciones",
	},
}


def run_level(level: str, extra_args: list) -> dict:
	"""Run a single audit level and capture its result."""
	info = LEVELS[level]
	script = ROOT / info["script"]
	if not script.exists():
		return {
			"level": level,
			"name": info["name"],
			"status": "ERROR",
			"message": f"script no encontrado: {info['script']}",
			"returncode": 1,
			"output": "",
		}

	cmd = [sys.executable, str(script)] + extra_args
	try:
		proc = subprocess.run(
			cmd,
			capture_output=True,
			text=True,
			timeout=300,
			cwd=str(ROOT),
		)
		return {
			"level": level,
			"name": info["name"],
			"status": "PASS" if proc.returncode == 0 else "FAIL",
			"returncode": proc.returncode,
			"output": proc.stdout + proc.stderr,
		}
	except subprocess.TimeoutExpired:
		return {
			"level": level,
			"name": info["name"],
			"status": "TIMEOUT",
			"returncode": 1,
			"output": "excedió 300s de timeout",
		}


def main():
	args = sys.argv[1:]

	selected_levels = list(LEVELS.keys())
	extra_args = []

	if "--level" in args:
		idx = args.index("--level")
		if idx + 1 < len(args):
			lvl = args[idx + 1].upper()
			if lvl in LEVELS:
				selected_levels = [lvl]
			else:
				print(f"Nivel desconocido: {lvl}. Disponibles: {', '.join(LEVELS.keys())}")
				sys.exit(2)

	as_json = "--json" in args
	as_report = "--report" in args

	if as_json:
		extra_args.append("--json")
	if as_report:
		extra_args.append("--report")

	results = []
	for level in selected_levels:
		results.append(run_level(level, extra_args))

	if as_json:
		consolidated = {
			"levels": results,
			"verdict": "AUDIT_PASS" if all(r["status"] == "PASS" for r in results) else "AUDIT_FAIL",
		}
		print(json.dumps(consolidated, indent=2, ensure_ascii=False))
		sys.exit(0 if consolidated["verdict"] == "AUDIT_PASS" else 1)

	print(f"\n{'=' * 70}")
	print(f"  AUDITORÍA DESACOPLADA — {len(selected_levels)} nivel(es)")
	print(f"{'=' * 70}")

	all_pass = True
	for r in results:
		icon = "OK" if r["status"] == "PASS" else "!!"
		print(f"\n  [{icon}] {r['level']} — {r['name']}")

		output_lines = [l for l in r["output"].strip().split("\n") if l.strip()]
		for line in output_lines:
			if line.startswith("=") or not line.strip():
				continue
			if "report generated" in line.lower():
				print(f"       {line.strip()}")
			elif "[OK]" in line or "[!!]" in line:
				print(f"       {line.strip()}")
			elif "PASS" in line and "(" in line:
				print(f"       {line.strip()}")
			elif "FAIL" in line and "(" in line:
				print(f"       {line.strip()}")

		if r["status"] != "PASS":
			all_pass = False

	print(f"\n{'=' * 70}")
	verdict = "AUDIT_PASS" if all_pass else "AUDIT_FAIL"
	passed = sum(1 for r in results if r["status"] == "PASS")
	print(f"  {verdict} ({passed}/{len(results)} niveles)")
	print(f"{'=' * 70}\n")

	sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
	main()
