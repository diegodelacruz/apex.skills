#!/usr/bin/env python3
"""Validate the local controlled MCP handshake without connecting to Oracle."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "scripts" / "apex_controlled_mcp.py"
REQUEST = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "apex-skills-validation", "version": "1.0"},
    },
}


def main() -> int:
    """Start the server and require its declared identity in initialize output."""
    process = subprocess.Popen(
        [sys.executable, str(SERVER)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = process.communicate(json.dumps(REQUEST) + "\n", timeout=20)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        print("APEX_CONTROLLED_MCP_HANDSHAKE_FAIL: initialize timed out", file=sys.stderr)
        return 1
    try:
        response = json.loads(stdout.splitlines()[0])
        server_name = response["result"]["serverInfo"]["name"]
    except (IndexError, KeyError, TypeError, json.JSONDecodeError):
        print(
            "APEX_CONTROLLED_MCP_HANDSHAKE_FAIL: server returned no valid initialize response "
            f"(exit={process.returncode}; stderr={stderr[:200]!r})",
            file=sys.stderr,
        )
        return 1
    if server_name != "apex-controlled-mcp":
        print("APEX_CONTROLLED_MCP_HANDSHAKE_FAIL: unexpected server identity", file=sys.stderr)
        return 1
    print("APEX_CONTROLLED_MCP_HANDSHAKE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
