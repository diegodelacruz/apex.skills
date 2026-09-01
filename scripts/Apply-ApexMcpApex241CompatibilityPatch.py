#!/usr/bin/env python3
"""Apply the APEX 24.1.3 metadata compatibility patch to managed apex-mcp.

The managed upstream targets APEX 24.2 by default.  APEX 24.1.3 keeps the
public APEX_APPLICATION_* views compatible, but several internal metadata
tables are owned by APEX_240100 and use different column names.  This script
is the canonical, repeatable patch point; never edit the managed checkout by
hand.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / ".upstreams" / "managed" / "apex-mcp" / "apex_mcp" / "tools" / "inspect_tools.py"
SETUP_TARGET = ROOT / ".upstreams" / "managed" / "apex-mcp" / "apex_mcp" / "tools" / "setup_tools.py"


def replace_all(text: str, old: str, new: str) -> tuple[str, int]:
    """Replace every exact upstream fragment and report the change count."""
    if new in text:
        # The patch is idempotent.  If a fragment remains beside an already
        # patched one, replace the remaining occurrences as well.
        changed_text = text.replace(old, new)
        return changed_text, changed_text.count(new) - text.count(new)
    if old not in text:
        raise RuntimeError(f"Unsupported apex-mcp revision; pattern not found: {old[:80]!r}")
    return text.replace(old, new), text.count(old)


def main() -> int:
    if not TARGET.is_file():
        raise SystemExit("Managed apex-mcp checkout is missing; initialize upstreams first.")
    if not SETUP_TARGET.is_file():
        raise SystemExit("Managed apex-mcp setup tools are missing; initialize upstreams first.")

    content = TARGET.read_text(encoding="utf-8")
    changes = 0

    replacements = [
        ("                   css_inline,\n", "                   NULL AS css_inline,\n"),
        ("                   template_options,\n", "                   region_template_options AS template_options,\n"),
        ("                   parent_region\n", "                   parent_region_name AS parent_region\n"),
        (
            "            SELECT id, name, plug_source\n"
            "              FROM wwv_flow_page_plugs\n"
            "             WHERE flow_id = :app_id\n"
            "               AND page_id = :page_id\n"
            "               AND UPPER(name) = UPPER(:region_name)",
            "            SELECT id, region_name AS name, plug_source\n"
            "              FROM APEX_240100.wwv_flow_page_plugs\n"
            "             WHERE flow_id = :app_id\n"
            "               AND page_id = :page_id\n"
            "               AND UPPER(region_name) = UPPER(:region_name)",
        ),
        ("            UPDATE wwv_flow_page_plugs\n", "            UPDATE APEX_240100.wwv_flow_page_plugs\n"),
        ("            UPDATE wwv_flow_step_items\n", "            UPDATE APEX_240100.wwv_flow_step_items\n"),
        ("UPDATE wwv_flow_steps\n", "UPDATE APEX_240100.wwv_flow_steps\n"),
        ("              FROM wwv_flow_page_plugs\n", "              FROM APEX_240100.wwv_flow_page_plugs\n"),
        ("              FROM wwv_flow_step_items\n", "              FROM APEX_240100.wwv_flow_step_items\n"),
        ("              FROM wwv_flow_steps\n", "              FROM APEX_240100.wwv_flow_steps\n"),
        ("              FROM wwv_flow_step_buttons\n", "              FROM APEX_240100.wwv_flow_step_buttons\n"),
        ("  DELETE FROM wwv_flow_step_items\n", "  DELETE FROM APEX_240100.wwv_flow_step_items\n"),
        ("  DELETE FROM wwv_flow_step_processing\n", "  DELETE FROM APEX_240100.wwv_flow_step_processing\n"),
        ("  DELETE FROM wwv_flow_step_buttons\n", "  DELETE FROM APEX_240100.wwv_flow_step_buttons\n"),
        ("  DELETE FROM wwv_flow_step_da_actions\n", "  DELETE FROM APEX_240100.wwv_flow_step_da_actions\n"),
        ("  DELETE FROM wwv_flow_step_da_events\n", "  DELETE FROM APEX_240100.wwv_flow_step_da_events\n"),
        ("  DELETE FROM wwv_flow_page_plugs\n", "  DELETE FROM APEX_240100.wwv_flow_page_plugs\n"),
        ("  DELETE FROM wwv_flow_page_computations\n", "  DELETE FROM APEX_240100.wwv_flow_page_computations\n"),
        ("  DELETE FROM wwv_flow_step_validations\n", "  DELETE FROM APEX_240100.wwv_flow_step_validations\n"),
        ("  DELETE FROM wwv_flow_steps\n", "  DELETE FROM APEX_240100.wwv_flow_steps\n"),
        ("DELETE FROM wwv_flow_step_items\n", "DELETE FROM APEX_240100.wwv_flow_step_items\n"),
        ("DELETE FROM wwv_flow_step_buttons\n", "DELETE FROM APEX_240100.wwv_flow_step_buttons\n"),
        (
            '            set_clauses.append("name = :new_name")',
            '            set_clauses.append("region_name = :new_name")',
        ),
        (
            '            set_clauses.append("display_sequence = :new_sequence")',
            '            set_clauses.append("plug_display_sequence = :new_sequence")',
        ),
        (
            '            set_clauses.append("field_required = :new_is_required")',
            '            set_clauses.append("is_required = :new_is_required")',
        ),
        (
            "    if not any([new_name, new_title, new_auth_scheme is not None, new_page_mode]):\n",
            "    if new_auth_scheme is not None:\n"
            '        return _json({"status": "error", "error": '
            '"APEX 24.1.3 stores page authorization outside WWV_FLOW_STEPS; '
            'use the supported export/import path for this field."})\n\n'
            "    if not any([new_name, new_title, new_page_mode]):\n",
        ),
        (
            '               AND UPPER(name) = UPPER(:region_name)\n        """',
            '               AND UPPER(region_name) = UPPER(:region_name)\n        """',
        ),
    ]

    for old, new in replacements:
        content, changed = replace_all(content, old, new)
        changes += changed

    TARGET.write_text(content, encoding="utf-8")
    setup_content = SETUP_TARGET.read_text(encoding="utf-8")
    setup_replacements = [
        (
            "SELECT 1 FROM wwv_flow_page_plugs WHERE rownum = 1",
            "SELECT 1 FROM APEX_240100.wwv_flow_page_plugs WHERE rownum = 1",
        ),
        ("        ok_sel = check_select(table)\n", '        ok_sel = check_select(f"APEX_240100.{table}")\n'),
        ("SELECT, UPDATE ON WWV_FLOW_PAGE_PLUGS", "SELECT, UPDATE ON APEX_240100.WWV_FLOW_PAGE_PLUGS"),
        ("UPDATE on WWV_FLOW_PAGE_PLUGS", "UPDATE on APEX_240100.WWV_FLOW_PAGE_PLUGS"),
        ("UPDATE on WWV_FLOW_STEP_ITEMS", "UPDATE on APEX_240100.WWV_FLOW_STEP_ITEMS"),
        ("DELETE on WWV_FLOW_STEPS", "DELETE on APEX_240100.WWV_FLOW_STEPS"),
        (
            "GRANT UPDATE ON WWV_FLOW_PAGE_PLUGS TO MY_SCHEMA",
            "GRANT UPDATE ON APEX_240100.WWV_FLOW_PAGE_PLUGS TO MY_SCHEMA",
        ),
        (
            "GRANT UPDATE ON WWV_FLOW_STEP_ITEMS TO MY_SCHEMA",
            "GRANT UPDATE ON APEX_240100.WWV_FLOW_STEP_ITEMS TO MY_SCHEMA",
        ),
        ("SELECT, UPDATE, DELETE ON WWV_FLOW_PAGE_PLUGS", "SELECT, UPDATE, DELETE ON APEX_240100.WWV_FLOW_PAGE_PLUGS"),
        ("SELECT, UPDATE, DELETE ON WWV_FLOW_STEP_ITEMS", "SELECT, UPDATE, DELETE ON APEX_240100.WWV_FLOW_STEP_ITEMS"),
        ("SELECT, DELETE ON WWV_FLOW_STEPS", "SELECT, DELETE ON APEX_240100.WWV_FLOW_STEPS"),
        ("ON WWV_FLOW_PAGE_PLUGS TO {current_user}", "ON APEX_240100.WWV_FLOW_PAGE_PLUGS TO {current_user}"),
        ("ON WWV_FLOW_STEP_ITEMS TO {current_user}", "ON APEX_240100.WWV_FLOW_STEP_ITEMS TO {current_user}"),
        ("ON WWV_FLOW_STEPS TO {current_user}", "ON APEX_240100.WWV_FLOW_STEPS TO {current_user}"),
    ]
    setup_changes = 0
    for old, new in setup_replacements:
        setup_content, changed = replace_all(setup_content, old, new)
        setup_changes += changed
    SETUP_TARGET.write_text(setup_content, encoding="utf-8")
    total_changes = changes + setup_changes
    print(f"APEX_MCP_APEX241_COMPATIBILITY_PATCH_{'APPLIED' if total_changes else 'PRESENT'} changes={total_changes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
