#!/usr/bin/env python3
"""Validate the patched apex-mcp direct TEST connection without mutations."""

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / ".upstreams" / "apex-mcp"))

import keyring


raw_profile = keyring.get_password("apex-skills", "test")
if not raw_profile:
	raise SystemExit("TEST profile is missing. Run manage_apex_credentials.py import-env first.")
profile = json.loads(raw_profile)
mapping = {
	"ORACLE_DB_USER": "db_user",
	"ORACLE_DB_PASS": "db_pass",
	"ORACLE_DSN": "dsn",
	"APEX_WORKSPACE_ID": "workspace_id",
	"APEX_SCHEMA": "schema",
	"APEX_WORKSPACE_NAME": "workspace_name",
}
for environment_name, profile_name in mapping.items():
	os.environ[environment_name] = str(profile[profile_name])

from apex_mcp.tools.sql_tools import apex_connect
from apex_mcp.db import db

result = json.loads(apex_connect())
if result.get("status") != "ok":
	raise SystemExit("APEX_MCP_DIRECT_CONNECTION_FAIL")
rows = db.execute_safe("select sys_context('userenv', 'current_schema') as current_schema from dual", max_rows=1)
db._conn.close()
db._conn = None
if not rows:
	raise SystemExit("APEX_MCP_DIRECT_CONNECTION_FAIL")
print("APEX_MCP_DIRECT_CONNECTION_PASS mode=read-only")
