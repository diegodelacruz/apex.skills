#!/usr/bin/env python3
"""Read and update the repository's ignored .env credential source."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Mapping

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPOSITORY_ROOT / ".env"


def parse_env(path: Path = ENV_FILE) -> dict[str, str]:
    """Read simple KEY=VALUE entries without consulting process credentials."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            quote = value[0]
            value = value[1:-1]
            value = value.replace("\\\\", "\\")
            value = value.replace(f"\\{quote}", quote)
        else:
            value = value.split(" #", 1)[0].rstrip()
        if key:
            values[key] = value
    return values


def selected_environment(environment: str | None, values: Mapping[str, str]) -> str | None:
    """Resolve an explicit or .env-only environment selector."""
    selected = (environment or values.get("DB_ENV", "")).strip().lower()
    return {"test": "test", "testing": "test", "prod": "production", "production": "production"}.get(selected)


def load_database_profile(environment: str, path: Path = ENV_FILE) -> tuple[dict[str, str] | None, list[str]]:
    """Build an Oracle profile from DB_TESTING_* or DB_PRODUCTION_* in .env."""
    values = parse_env(path)
    normalized = selected_environment(environment, {})
    if normalized is None:
        return None, ["environment"]
    prefix = "DB_TESTING" if normalized == "test" else "DB_PRODUCTION"
    required = ("USER", "PASSWORD", "HOST", "PORT", "SID")
    missing = [f"{prefix}_{name}" for name in required if not values.get(f"{prefix}_{name}")]
    if missing:
        return None, missing
    host = values[f"{prefix}_HOST"]
    port = values[f"{prefix}_PORT"]
    service = values[f"{prefix}_SID"]
    profile = {
        "db_user": values[f"{prefix}_USER"],
        "db_pass": values[f"{prefix}_PASSWORD"],
        "dsn": f"{host}:{port}/{service}",
        "host": host,
        "port": port,
        "service": service,
        "wallet_dir": values.get(f"{prefix}_WALLET_DIR", ""),
        "wallet_pass": values.get(f"{prefix}_WALLET_PASSWORD", ""),
        "workspace_id": values.get(f"{prefix}_WORKSPACE_ID", ""),
        "schema": values.get(f"{prefix}_SCHEMA", ""),
        "workspace_name": values.get(f"{prefix}_WORKSPACE_NAME", ""),
    }
    return profile, []


def load_apex_profile(environment: str, path: Path = ENV_FILE) -> tuple[dict[str, str] | None, list[str]]:
    """Build an App Builder profile from APEX_TESTING_* or APEX_PRODUCTION_* in .env."""
    values = parse_env(path)
    normalized = selected_environment(environment, {})
    if normalized is None:
        return None, ["environment"]
    prefix = "APEX_TESTING" if normalized == "test" else "APEX_PRODUCTION"
    suffixes = ("BASE_URL", "WORKSPACE", "USER", "PASSWORD")
    missing = [f"{prefix}_{name}" for name in suffixes if not values.get(f"{prefix}_{name}")]
    if missing:
        return None, missing
    return {
        "base_url": values[f"{prefix}_BASE_URL"].rstrip("/"),
        "workspace": values[f"{prefix}_WORKSPACE"],
        "apex_user": values[f"{prefix}_USER"],
        "apex_pass": values[f"{prefix}_PASSWORD"],
    }, []


def update_env(values: Mapping[str, str], path: Path = ENV_FILE) -> None:
    """Update selected .env keys while retaining comments and unrelated entries."""
    existing = path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
    pending = dict(values)
    output: list[str] = []
    for line in existing:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in values:
                output.append(f"{key}={_format_env_value(values[key])}")
                pending.pop(key, None)
                continue
        output.append(line)
    output.extend(f"{key}={_format_env_value(value)}" for key, value in pending.items())
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(output) + "\n"
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_name = temp_file.name
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def _format_env_value(value: str) -> str:
    """Quote values that could otherwise be parsed ambiguously."""
    if "\n" in value or "\r" in value:
        raise ValueError(".env values cannot contain line breaks")
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
