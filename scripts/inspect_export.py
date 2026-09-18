#!/usr/bin/env python3
"""Inspect an APEX export ZIP and report its contents.

Usage:
    python scripts/inspect_export.py <export.zip>
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path


def inspect(path: str) -> dict:
    """Return a summary of the APEX export ZIP contents."""
    zp = Path(path)
    if not zp.exists() or not zp.suffix == ".zip":
        return {"error": f"Not a valid ZIP: {path}"}

    result: dict = {"file": zp.name, "pages": [], "components": [], "files": []}
    with zipfile.ZipFile(zp, "r") as zf:
        for name in sorted(zf.namelist()):
            result["files"].append(name)
            if "page_" in name.lower() and name.endswith(".sql"):
                result["pages"].append(name)
            elif name.endswith(".sql"):
                result["components"].append(name)

    result["total_files"] = len(result["files"])
    result["total_pages"] = len(result["pages"])
    return result


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <export.zip>")
        sys.exit(1)
    summary = inspect(sys.argv[1])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
