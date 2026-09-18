#!/usr/bin/env python3
"""Validate SQL/PL-SQL files against Oracle coding style conventions.

Usage:
    python scripts/validate_sql_style.py <file.sql> [--strict]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def validate_sql_style(path: str, strict: bool = False) -> list[str]:
    """Check a SQL file for style violations. Returns a list of issues."""
    fp = Path(path)
    if not fp.exists():
        return [f"File not found: {path}"]

    content = fp.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    issues: list[str] = []

    for i, line in enumerate(lines, 1):
        if line.rstrip() != line:
            issues.append(f"Line {i}: trailing whitespace")
        if "\t" in line:
            issues.append(f"Line {i}: tab character (use spaces)")
        if len(line) > 200:
            issues.append(f"Line {i}: line exceeds 200 characters ({len(line)})")

    if re.search(r"\bSELECT\s+\*\s+FROM\b", content, re.IGNORECASE) and strict:
        issues.append("SELECT * found (use explicit column lists in production code)")

    if re.search(r"\bEXECUTE\s+IMMEDIATE\b", content, re.IGNORECASE):
        issues.append("EXECUTE IMMEDIATE found (review for SQL injection risk)")

    if re.search(r"--.*(?:password|secret|token|key)\s*[:=]", content, re.IGNORECASE):
        issues.append("Possible credential in comment")

    if not content.strip().endswith(("/", ";")):
        issues.append("File does not end with / or ; terminator")

    return issues


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.sql> [--strict]")
        sys.exit(1)

    strict = "--strict" in sys.argv
    issues = validate_sql_style(sys.argv[1], strict=strict)

    if issues:
        print(f"Issues ({len(issues)}):")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("[OK] No style issues found")
        sys.exit(0)


if __name__ == "__main__":
    main()
