#!/usr/bin/env python3
"""Validate an APEX export for completeness and structural integrity.

Usage:
    python scripts/validate_export.py <export.zip>
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


def validate(path: str) -> dict:
    """Validate the APEX export ZIP structure."""
    zp = Path(path)
    if not zp.exists():
        return {"valid": False, "error": f"File not found: {path}"}
    if zp.suffix != ".zip":
        return {"valid": False, "error": f"Not a ZIP file: {path}"}

    issues: list[str] = []
    info: dict = {"file": zp.name, "valid": True, "issues": issues, "sql_files": 0, "has_install": False}

    with zipfile.ZipFile(zp, "r") as zf:
        names = zf.namelist()
        sql_files = [n for n in names if n.endswith(".sql")]
        info["sql_files"] = len(sql_files)

        install_candidates = [n for n in names if "install" in n.lower() and n.endswith(".sql")]
        info["has_install"] = len(install_candidates) > 0

        if not sql_files:
            issues.append("No SQL files found in export")

        for sql_name in sql_files:
            content = zf.read(sql_name).decode("utf-8", errors="replace")
            if "wwv_flow" not in content.lower() and "apex_" not in content.lower():
                issues.append(f"{sql_name}: no APEX API references found")

    info["valid"] = len(issues) == 0
    return info


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <export.zip>")
        sys.exit(1)
    result = validate(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
