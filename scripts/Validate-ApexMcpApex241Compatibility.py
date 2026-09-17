#!/usr/bin/env python3
"""Static contract checks for the managed APEX 24.1.3 compatibility patch.

Verifies that the patched apex-mcp uses qualified APEX_240100 table references
and does not contain unqualified DML against internal metadata tables.

Status: ACTIVE
Tests: Infrastructure script (no automated tests)
Dependencies: managed apex-mcp checkout, Apply-ApexMcpApex241CompatibilityPatch.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_ROOT = ROOT / ".upstreams" / "managed" / "apex-mcp" / "apex_mcp"
INSPECT = MCP_ROOT / "tools" / "inspect_tools.py"
SETUP = MCP_ROOT / "tools" / "setup_tools.py"


def main() -> int:
    raise SystemExit(
        "ADAPTER_INCOMPATIBLE: retired validator. Qualified access to WWV_FLOW_* "
        "does not make it an approved APEX CRUD route."
    )
    if not INSPECT.is_file() or not SETUP.is_file():
        raise SystemExit("Managed apex-mcp checkout is missing; initialize upstreams first.")

    inspect = INSPECT.read_text(encoding="utf-8")
    setup = SETUP.read_text(encoding="utf-8")

    required = {
        "qualified plugs": "APEX_240100.wwv_flow_page_plugs",
        "qualified items": "APEX_240100.wwv_flow_step_items",
        "qualified steps": "APEX_240100.wwv_flow_steps",
        "region name mapping": "region_name = :new_name",
        "region sequence mapping": "plug_display_sequence = :new_sequence",
        "item required mapping": "is_required = :new_is_required",
        "page CSS compatibility": "NULL AS css_inline",
        "parent region compatibility": "parent_region_name AS parent_region",
    }
    missing = [name for name, fragment in required.items() if fragment not in inspect]

    forbidden = [
        "FROM wwv_flow_page_plugs",
        "FROM wwv_flow_step_items",
        "FROM wwv_flow_steps",
        "UPDATE wwv_flow_page_plugs",
        "UPDATE wwv_flow_step_items",
        "UPDATE wwv_flow_steps",
        "DELETE FROM wwv_flow_page_plugs",
        "DELETE FROM wwv_flow_step_items",
        "DELETE FROM wwv_flow_steps",
    ]
    unqualified = [fragment for fragment in forbidden if fragment in inspect]
    if "APEX_240100.wwv_flow_page_plugs" not in setup:
        missing.append("qualified setup permission probe")
    if "APEX_240100.WWV_FLOW_PAGE_PLUGS" not in setup:
        missing.append("qualified setup grant script")

    if missing or unqualified:
        if missing:
            print("MISSING=" + ",".join(missing))
        if unqualified:
            print("UNQUALIFIED=" + ",".join(unqualified))
        return 1

    print("APEX_MCP_APEX241_COMPATIBILITY_STATIC_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
