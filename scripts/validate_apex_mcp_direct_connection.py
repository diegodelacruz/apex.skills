#!/usr/bin/env python3
"""Validate the patched apex-mcp direct connection without mutations."""

import argparse
import json
import os
import sys
from pathlib import Path

import keyring

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / ".upstreams" / "apex-mcp"))

from apex_mcp.db import db  # noqa: E402
from apex_mcp.tools.sql_tools import apex_connect  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--environment", choices=("test", "production"), default="test")
args = parser.parse_args()

raw_profile = keyring.get_password("apex-skills", args.environment)
if not raw_profile:
    raise SystemExit(f"{args.environment} profile is missing. Import it first.")
profile = json.loads(raw_profile)
mapping = {
    "ORACLE_DB_USER": "db_user",
    "ORACLE_DB_PASS": "db_pass",  # pragma: allowlist secret
    "ORACLE_DSN": "dsn",
    "APEX_WORKSPACE_ID": "workspace_id",
    "APEX_SCHEMA": "schema",
    "APEX_WORKSPACE_NAME": "workspace_name",
}
for environment_name, profile_name in mapping.items():
    os.environ[environment_name] = str(profile[profile_name])

result = json.loads(apex_connect())
if result.get("status") != "ok":
    raise SystemExit("APEX_MCP_DIRECT_CONNECTION_FAIL")
rows = db.execute_safe("select sys_context('userenv', 'current_schema') as current_schema from dual", max_rows=1)
db._conn.close()
db._conn = None
if not rows:
    raise SystemExit("APEX_MCP_DIRECT_CONNECTION_FAIL")
print(f"APEX_MCP_DIRECT_CONNECTION_PASS environment={args.environment} mode=read-only")
