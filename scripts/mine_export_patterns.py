#!/usr/bin/env python3
"""Mine patterns from APEX export files for reuse and consistency analysis.

Usage:
    python scripts/mine_export_patterns.py <export.zip> [--output patterns.json]
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path


def mine_patterns(path: str) -> dict:
    """Extract reusable patterns from an APEX export ZIP."""
    zp = Path(path)
    if not zp.exists():
        return {"error": f"File not found: {path}"}

    patterns: dict = {
        "file": zp.name,
        "templates_used": Counter(),
        "region_types": Counter(),
        "item_types": Counter(),
        "process_types": Counter(),
        "dynamic_action_events": Counter(),
    }

    with zipfile.ZipFile(zp, "r") as zf:
        for name in zf.namelist():
            if not name.endswith(".sql"):
                continue
            content = zf.read(name).decode("utf-8", errors="replace")

            for match in re.findall(r"p_template\s*=>\s*'([^']+)'", content, re.IGNORECASE):
                patterns["templates_used"][match] += 1
            for match in re.findall(r"p_plug_source_type\s*=>\s*'([^']+)'", content, re.IGNORECASE):
                patterns["region_types"][match] += 1
            for match in re.findall(r"p_display_as\s*=>\s*'([^']+)'", content, re.IGNORECASE):
                patterns["item_types"][match] += 1
            for match in re.findall(r"p_process_type\s*=>\s*'([^']+)'", content, re.IGNORECASE):
                patterns["process_types"][match] += 1
            for match in re.findall(r"p_event_id\s*=>\s*'([^']+)'", content, re.IGNORECASE):
                patterns["dynamic_action_events"][match] += 1

    serializable = {k: dict(v) if isinstance(v, Counter) else v for k, v in patterns.items()}
    return serializable


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <export.zip> [--output patterns.json]")
        sys.exit(1)

    result = mine_patterns(sys.argv[1])

    output_file = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    output = json.dumps(result, indent=2)
    if output_file:
        Path(output_file).write_text(output, encoding="utf-8")
        print(f"Patterns written to {output_file}")
    else:
        print(output)


if __name__ == "__main__":
    main()
