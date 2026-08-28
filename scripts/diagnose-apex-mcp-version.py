#!/usr/bin/env python3
"""Diagnose apex-mcp version and show what patterns are present."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / ".upstreams" / "managed" / "apex-mcp" / "apex_mcp"


def diagnose():
    db_file = PACKAGE / "db.py"
    if not db_file.exists():
        print(f"ERROR: {db_file} not found")
        return

    content = db_file.read_text(encoding="utf-8")
    print("=== APEX-MCP DIAGNOSIS ===")
    print(f"File: {db_file}")
    print(f"Size: {len(content)} bytes")
    print()

    # Look for connection patterns
    patterns = [
        ("oracledb.connect(", "Direct oracledb.connect call"),
        ("self._conn = ", "Connection assignment"),
        ("connect_kwargs", "Keyword arguments pattern"),
        ("wallet_location", "Wallet support"),
        ("wallet_password", "Wallet password support"),
    ]

    print("=== PATTERNS FOUND ===")
    for pattern, desc in patterns:
        if pattern in content:
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if pattern in line:
                    print(f"✓ Line {i}: {desc}")
                    print(f"  {line.strip()[:80]}")
                    break

    # Find the actual connect method
    print()
    print("=== CONNECT METHOD SIGNATURE ===")
    match = re.search(r"def.*connect.*\(.*?\):", content, re.MULTILINE | re.DOTALL)
    if match:
        print("Found method signature:")
        lines = match.group(0).split("\n")
        for line in lines[:5]:
            print(f"  {line}")

    # Show oracledb.connect call(s)
    print()
    print("=== ORACLEDB.CONNECT CALLS ===")
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if "oracledb.connect" in line:
            start = max(0, i - 3)
            end = min(len(lines), i + 8)
            print(f"Found at line {i}:")
            for j in range(start, end):
                marker = ">>>" if j == i - 1 else "   "
                print(f"{marker} {j+1:3d}: {lines[j]}")
            print()


if __name__ == "__main__":
    diagnose()
