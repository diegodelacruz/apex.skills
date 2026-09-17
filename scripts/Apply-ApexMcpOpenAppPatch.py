#!/usr/bin/env python3
"""Apply the apex_open_app patch to managed apex-mcp.

The managed upstream only supports creating NEW applications via
apex_create_app().  This patch adds apex_open_app() which starts an
import session targeting an EXISTING application so that apex_add_page()
and all component tools work against it.

This script is the canonical, repeatable patch point; never edit the
managed checkout by hand.

Status: ACTIVE
Dependencies: managed apex-mcp checkout
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_TOOLS = ROOT / ".upstreams" / "managed" / "apex-mcp" / "apex_mcp" / "tools" / "app_tools.py"
SERVER = ROOT / ".upstreams" / "managed" / "apex-mcp" / "apex_mcp" / "server.py"
PATCH_SOURCE = ROOT / "scripts" / "patches" / "apex_open_app.py.txt"


def main() -> int:
    if not APP_TOOLS.is_file():
        raise SystemExit("Managed apex-mcp checkout is missing; initialize upstreams first.")
    if not SERVER.is_file():
        raise SystemExit("Managed apex-mcp server.py is missing; initialize upstreams first.")
    if not PATCH_SOURCE.is_file():
        raise SystemExit(f"Patch source file missing: {PATCH_SOURCE}")

    app_content = APP_TOOLS.read_text(encoding="utf-8")
    server_content = SERVER.read_text(encoding="utf-8")
    patch_function = PATCH_SOURCE.read_text(encoding="utf-8")
    changes = 0

    # ── 1. Add apex_open_app function to app_tools.py ──
    if "def apex_open_app(" not in app_content:
        anchor = "def apex_create_app("
        if anchor not in app_content:
            raise SystemExit(f"Cannot find anchor '{anchor}' in app_tools.py")
        app_content = app_content.replace(anchor, patch_function + "\n\n" + anchor)
        changes += 1

    # ── 2. Add import in server.py ──
    old_import = "from .tools.app_tools import (\n" "    apex_list_apps,\n" "    apex_create_app,"
    new_import = (
        "from .tools.app_tools import (\n" "    apex_list_apps,\n" "    apex_open_app,\n" "    apex_create_app,"
    )
    if "apex_open_app," not in server_content:
        if old_import not in server_content:
            raise SystemExit("Cannot find app_tools import block in server.py")
        server_content = server_content.replace(old_import, new_import)
        changes += 1

    # ── 3. Add tool registration in server.py ──
    old_reg = (
        'mcp.tool(description="Create a new APEX app and start an import session. '
        'Call apex_finalize_app() when done."'
    )
    new_tool_line = (
        'mcp.tool(description="Open an existing APEX app for modification '
        '(add pages/components). Call apex_finalize_app() when done.", '
        'annotations=_WRITE, tags={"app"})(apex_open_app)\n'
    )
    if "apex_open_app)" not in server_content:
        if old_reg not in server_content:
            raise SystemExit("Cannot find create_app registration in server.py")
        server_content = server_content.replace(old_reg, new_tool_line + old_reg)
        changes += 1

    # ── 4. Update instructions to mention apex_open_app ──
    old_lifecycle = (
        "1. `apex_connect()` → 2. `apex_create_app(app_id, app_name)` "
        "→ 3. add pages/regions/items → 4. `apex_finalize_app()`\n"
        "Always finalize. For existing apps: `apex_list_apps()` → "
        "`apex_get_app_details(id)` → inspect/update."
    )
    new_lifecycle = (
        "**New app:** `apex_connect()` → `apex_create_app(id, name)` "
        "→ add pages/regions/items → `apex_finalize_app()`\n"
        "**Existing app:** `apex_connect()` → `apex_open_app(id)` "
        "→ add pages/regions/items → `apex_finalize_app()`\n"
        "Always finalize. For read-only inspection: `apex_list_apps()` → "
        "`apex_get_app_details(id)`."
    )
    if "apex_open_app(id)" not in server_content:
        if old_lifecycle in server_content:
            server_content = server_content.replace(old_lifecycle, new_lifecycle)
            changes += 1

    APP_TOOLS.write_text(app_content, encoding="utf-8")
    SERVER.write_text(server_content, encoding="utf-8")

    status = "APPLIED" if changes else "PRESENT"
    print(f"APEX_MCP_OPEN_APP_PATCH_{status} changes={changes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
