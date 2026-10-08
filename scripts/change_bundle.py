#!/usr/bin/env python3
"""Validate and render portable Oracle/APEX live-change bundles.

A bundle is a JSON manifest plus reviewed SQL artifacts.  It records the
baseline observed during diagnosis and lets an executor run a bounded preflight
then apply/verification sequence.  This module deliberately
does not open an Oracle connection: adapters own credentials and execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SUPPORTED_KINDS = {"oracle_ddl", "oracle_data", "apex_page", "apex_component"}
REQUIRED_PHASES = ("preflight", "apply", "verify", "rollback")
FORBIDDEN_SQLCL_COMMAND = re.compile(r"(?im)^\s*(?:@@?|!|connect\b|exit\b|host\b|start\b|spool\b)")


class ChangeBundleError(ValueError):
    """A bundle cannot be executed safely as declared."""


def _inside(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ChangeBundleError("Cada artefacto debe declarar una ruta relativa no vacía.")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ChangeBundleError(f"Artefacto fuera del checkout: {relative}") from exc
    if candidate.suffix.lower() != ".sql" or not candidate.is_file():
        raise ChangeBundleError(f"Artefacto SQL inexistente o inválido: {relative}")
    return candidate


def load_bundle(path: Path, root: Path) -> dict[str, Any]:
    """Load and validate a bundle, returning resolved artifact paths separately."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ChangeBundleError(f"No se pudo leer change.json: {exc}") from exc
    if not isinstance(raw, dict):
        raise ChangeBundleError("change.json debe ser un objeto JSON.")
    if raw.get("version") != 1:
        raise ChangeBundleError("Solo se admite change.json con version 1.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{2,80}", str(raw.get("id", ""))):
        raise ChangeBundleError("id debe usar minúsculas, números, guiones o guiones bajos.")
    if raw.get("kind") not in SUPPORTED_KINDS:
        raise ChangeBundleError("kind debe ser oracle_ddl, oracle_data, apex_page o apex_component.")
    target = raw.get("target")
    target_is_valid = isinstance(target, dict) and all(
        isinstance(target.get(key), str) and target[key] for key in ("type", "name")
    )
    if not target_is_valid:
        raise ChangeBundleError("target debe declarar type y name.")
    baseline = raw.get("baseline")
    if not isinstance(baseline, dict) or not isinstance(baseline.get("fingerprint"), str):
        raise ChangeBundleError("baseline debe declarar la fingerprint observada durante el diagnóstico.")
    if not baseline["fingerprint"].strip() or "\n" in baseline["fingerprint"] or "\r" in baseline["fingerprint"]:
        raise ChangeBundleError("baseline.fingerprint debe ser una huella no vacía de una sola línea.")
    artifacts = raw.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ChangeBundleError("artifacts debe ser un objeto.")
    missing = [phase for phase in REQUIRED_PHASES if phase not in artifacts]
    if missing:
        raise ChangeBundleError(f"Faltan artefactos requeridos: {', '.join(missing)}.")
    resolved = {phase: _inside(root, str(artifacts[phase])) for phase in REQUIRED_PHASES}
    snapshot = artifacts.get("snapshot")
    if snapshot is not None:
        resolved["snapshot"] = _inside(root, str(snapshot))
    raw["_resolved_artifacts"] = resolved
    raw["_source"] = path.resolve()
    return raw


def baseline_success_marker(bundle: dict[str, Any]) -> str:
    """Return the output marker a preflight must emit after comparing its baseline."""
    return f"__CHANGE_BASELINE_OK={bundle['baseline']['fingerprint']}"


def render_execution_sql(bundle: dict[str, Any], phases: tuple[str, ...] = ("preflight", "apply", "verify")) -> str:
    """Render selected executable phases; rollback remains explicit only.

    Preflight is deliberately run and inspected before rendering apply/verify.
    Its SQL must compare the live object to ``baseline.fingerprint`` and emit
    ``baseline_success_marker(bundle)`` only on a match.
    """
    blocks: list[str] = []
    for phase in phases:
        if phase not in {"preflight", "apply", "verify"}:
            raise ChangeBundleError(f"Fase ejecutable no admitida: {phase}.")
        source = bundle["_resolved_artifacts"][phase]
        content = source.read_text(encoding="utf-8")
        if FORBIDDEN_SQLCL_COMMAND.search(content):
            raise ChangeBundleError(f"{source.name} contiene un comando SQLcl no permitido en un bundle.")
        blocks.append(
            "\n".join(
                (
                    f"prompt CHANGE_PHASE={phase}",
                    f"begin dbms_output.put_line('__CHANGE_TIMER_{phase}_START=' || dbms_utility.get_time); end;",
                    "/",
                    content.rstrip(),
                    f"begin dbms_output.put_line('__CHANGE_TIMER_{phase}_END=' || dbms_utility.get_time); end;",
                    "/",
                    "",
                )
            )
        )
    return "\n".join(blocks)


def artifact_hashes(bundle: dict[str, Any], root: Path) -> dict[str, str]:
    """Return hashes without exposing SQL text in the audit trail."""
    return {
        phase: hashlib.sha256(path.read_bytes()).hexdigest() for phase, path in bundle["_resolved_artifacts"].items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="Ruta a change.json dentro del checkout")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Raíz del checkout")
    parser.add_argument("--render", type=Path, help="Escribe SQL de preflight/apply/verify")
    parser.add_argument(
        "--phase",
        action="append",
        choices=("preflight", "apply", "verify"),
        help="Renderiza solo esta fase; se puede repetir.",
    )
    args = parser.parse_args()
    try:
        bundle = load_bundle(args.bundle.resolve(), args.root.resolve())
        rendered = render_execution_sql(bundle, tuple(args.phase or ("preflight", "apply", "verify")))
    except ChangeBundleError as exc:
        print(f"CHANGE_BUNDLE_INVALID: {exc}")
        return 2
    if args.render:
        args.render.write_text(rendered, encoding="utf-8")
    print(f"CHANGE_BUNDLE_VALID: {bundle['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
