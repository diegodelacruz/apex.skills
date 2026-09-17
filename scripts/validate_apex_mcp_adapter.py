#!/usr/bin/env python3
"""Read-only contract and surface check for the managed Oracle MCP upstream.

This checker never imports ``apex_mcp``, starts a server, opens a database
connection, or changes the managed upstream. A ready connection contract does
not make the full MCP surface safe to register.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER = ROOT / ".upstreams" / "managed" / "apex-mcp" / "apex_mcp"
REQUIRED_FILES = ("__init__.py", "db.py", "tools/sql_tools.py")
UNSAFE_SURFACE_PATTERNS = (
    r"\bupdate\s+apex_240100\.",
    r"\bdelete\s+from\s+apex_240100\.",
    r"\bwwv_flow_page_dev\.delete_page\b",
)


@dataclass(frozen=True)
class ValidationResult:
    """Statuses established solely by local source inspection."""

    adapter_status: str
    surface_status: str
    reason: str


def _read_required(adapter_root: Path) -> tuple[dict[str, str] | None, ValidationResult | None]:
    """Read required source files or report why the contract is unverifiable."""
    if not adapter_root.is_dir():
        return None, ValidationResult("MCP_ADAPTER_UNVERIFIED", "MCP_SURFACE_NOT_EVALUATED", "managed_adapter_missing")
    paths = {relative: adapter_root / relative for relative in REQUIRED_FILES}
    missing = [relative for relative, path in paths.items() if not path.is_file()]
    if missing:
        return None, ValidationResult(
            "MCP_ADAPTER_INCOMPATIBLE",
            "MCP_SURFACE_NOT_EVALUATED",
            "required_files_missing=" + ",".join(missing),
        )
    try:
        return {relative: path.read_text(encoding="utf-8") for relative, path in paths.items()}, None
    except OSError:
        return None, ValidationResult("MCP_ADAPTER_UNVERIFIED", "MCP_SURFACE_NOT_EVALUATED", "required_file_unreadable")


def _surface_status(adapter_root: Path) -> tuple[str, str]:
    """Inspect tools as text; lack of a match is not a safety certification."""
    tools_dir = adapter_root / "tools"
    if not tools_dir.is_dir():
        return "MCP_SURFACE_NOT_EVALUATED", "tools_directory_missing"
    try:
        sources = [path.read_text(encoding="utf-8") for path in tools_dir.rglob("*.py")]
    except OSError:
        return "MCP_SURFACE_NOT_EVALUATED", "tools_source_unreadable"
    if any(
        re.search(pattern, source, flags=re.IGNORECASE) for pattern in UNSAFE_SURFACE_PATTERNS for source in sources
    ):
        return "MCP_SURFACE_UNSAFE", "internal_apex_dml_or_api_detected"
    return "MCP_SURFACE_NOT_EVALUATED", "no_allowlist_or_exposure_inventory"


def validate_adapter(adapter_root: Path = ADAPTER) -> ValidationResult:
    """Validate the direct-connect source contract without executing upstream code."""
    sources, error = _read_required(adapter_root)
    if error is not None:
        return error
    assert sources is not None
    db_source = sources["db.py"]
    missing_patterns = []
    if not re.search(r"\bconnect_kwargs\s*=\s*\{", db_source):
        missing_patterns.append("connect_kwargs")
    if not re.search(r"\boracledb\.connect\(\*\*connect_kwargs\)", db_source):
        missing_patterns.append("oracledb.connect_kwargs")
    if not re.search(r"\bif\s+wallet_dir\s*:", db_source):
        missing_patterns.append("conditional_wallet")
    surface_status, surface_reason = _surface_status(adapter_root)
    if missing_patterns:
        return ValidationResult(
            "MCP_ADAPTER_INCOMPATIBLE",
            surface_status,
            "direct_connection_contract_missing=" + ",".join(missing_patterns),
        )
    return ValidationResult("MCP_ADAPTER_READY", surface_status, surface_reason)


def main() -> int:
    """Print unambiguous local inspection statuses."""
    result = validate_adapter()
    print(f"{result.adapter_status} mode=read-only-source-contract reason={result.reason}")
    print(f"{result.surface_status} mode=read-only-source-inspection")
    return int(result.adapter_status != "MCP_ADAPTER_READY")


if __name__ == "__main__":
    raise SystemExit(main())
