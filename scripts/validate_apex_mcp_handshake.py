#!/usr/bin/env python3
"""Validate that the profile wrapper returns an MCP initialize response.

Sends an MCP initialize JSON-RPC request to the profile wrapper subprocess
and verifies the server responds with a valid initialize result.

Status: ACTIVE
Tests: Infrastructure script (requires Oracle connection)
Dependencies: run_apex_mcp_with_profile.py, keyring
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--environment", choices=("test", "production"), default="test")
args = parser.parse_args()

root = Path(__file__).resolve().parent.parent
wrapper = root / "scripts" / "run_apex_mcp_with_profile.py"
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "apex-skills-validation", "version": "1.0"},
    },
}

process = subprocess.Popen(
    [sys.executable, str(wrapper), "--environment", args.environment],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
try:
    stdout, stderr = process.communicate(json.dumps(request) + "\n", timeout=20)
except subprocess.TimeoutExpired:
    process.kill()
    process.communicate()
    raise SystemExit("APEX_MCP_HANDSHAKE_FAIL: initialize timed out")

try:
    response = json.loads(stdout.splitlines()[0])
    server_name = response["result"]["serverInfo"]["name"]
except (IndexError, KeyError, TypeError, json.JSONDecodeError):
    raise SystemExit(
        "APEX_MCP_HANDSHAKE_FAIL: server returned no valid initialize response "
        f"(exit={process.returncode}; stderr={stderr[:200]!r})"
    )

if server_name != "apex-mcp":
    raise SystemExit("APEX_MCP_HANDSHAKE_FAIL: unexpected server identity")

print(f"APEX_MCP_HANDSHAKE_PASS environment={args.environment}")
