#!/usr/bin/env python3
"""Patch the managed apex-mcp checkout for direct Oracle connections.

Replaces the default wallet-only oracledb.connect() call with a keyword-based
pattern that works with direct TCP connections (no wallet required).

Status: ACTIVE
Tests: Infrastructure script (no automated tests)
Dependencies: managed apex-mcp checkout via Initialize-ApexSkillUpstreams-V2.ps1
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / ".upstreams" / "managed" / "apex-mcp" / "apex_mcp"


def replace_once(path: Path, old: str, new: str, normalized: bool = False) -> bool:
    """Replace code pattern once, with error handling and logging.

    Args:
        path: Path to file to patch
        old: Pattern to find
        new: Replacement pattern
        normalized: If True, normalize whitespace before matching

    Returns:
        True if replacement was made, False if new pattern already present

    Raises:
        RuntimeError: If old pattern not found (unsupported upstream revision)
    """
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as err:
        logging.error(f"Failed to read {path}: {err}")
        raise SystemExit(1) from err

    if new in content:
        return False

    if old not in content:
        if normalized:
            old_norm = " ".join(old.split())
            content_norm = " ".join(content.split())
            if old_norm not in content_norm:
                err_msg = f"Unsupported upstream revision: expected code not found in {path}"
                logging.error(err_msg)
                raise RuntimeError(err_msg)
            content = content_norm
        else:
            err_msg = f"Unsupported upstream revision: expected code not found in {path}"
            logging.error(err_msg)
            raise RuntimeError(err_msg)

    try:
        result = content.replace(old, new, 1)
        path.write_text(result, encoding="utf-8")
    except (OSError, UnicodeEncodeError) as err:
        logging.error(f"Failed to write {path}: {err}")
        raise SystemExit(1) from err

    return True


def main() -> int:
    db_file = PACKAGE / "db.py"
    config_file = PACKAGE / "config.py"
    sql_tools_file = PACKAGE / "tools" / "sql_tools.py"
    if not all(path.is_file() for path in (db_file, config_file, sql_tools_file)):
        err_msg = "Managed apex-mcp upstream is missing. Run Initialize-ApexSkillUpstreams-V2.ps1 first."
        logging.error(err_msg)
        raise SystemExit(err_msg)

    try:
        db_content = db_file.read_text(encoding="utf-8")

        # Check if already patched
        if "connect_kwargs = {" in db_content and "oracledb.connect(**connect_kwargs)" in db_content:
            print("APEX_MCP_DIRECT_CONNECTION_PATCH_PRESENT")
            return 0

        if "self._conn = oracledb.connect" not in db_content:
            logging.error("ERROR: apex-mcp version is not compatible")
            logging.error("       db.py does not contain expected oracledb.connect() pattern")
            raise RuntimeError("Unsupported apex-mcp version")

    except Exception as err:
        if isinstance(err, RuntimeError):
            raise
        logging.exception("Failed to check db.py status")
        raise SystemExit(1) from err

    try:
        changes = []
        changes.append(
            replace_once(
                db_file,
                """            self._conn = oracledb.connect(
				user=user,
				password=password,
				dsn=dsn,
				config_dir=wallet_dir,
				wallet_location=wallet_dir,
				wallet_password=wallet_pass,
			)""",
                """            connect_kwargs = {
				"user": user,
				"password": password,
				"dsn": dsn,
			}
			if wallet_dir:
				connect_kwargs["config_dir"] = wallet_dir
				connect_kwargs["wallet_location"] = wallet_dir
				if wallet_pass:
					connect_kwargs["wallet_password"] = wallet_pass
			self._conn = oracledb.connect(**connect_kwargs)""",
            )
        )
        changes.append(
            replace_once(
                config_file,
                """    "ORACLE_DB_PASS": DB_PASS,
	    "ORACLE_DSN": DB_DSN,
	    "ORACLE_WALLET_DIR": WALLET_DIR,
	    "APEX_WORKSPACE_ID": _ws_id_str,""",
                """    "ORACLE_DB_PASS": DB_PASS,
	    "ORACLE_DSN": DB_DSN,
	    "APEX_WORKSPACE_ID": _ws_id_str,""",
            )
        )
        changes.append(
            replace_once(
                sql_tools_file,
                """        ("dsn / ORACLE_DSN", dsn),
	        ("wallet_dir / ORACLE_WALLET_DIR", wallet_dir),
	        ("wallet_password / ORACLE_WALLET_PASSWORD", wallet_password),
	    ] if not val]""",
                """        ("dsn / ORACLE_DSN", dsn),
	    ] if not val]""",
            )
        )
        changes.append(
            replace_once(
                sql_tools_file,
                """        # Auto-discover template IDs from the live workspace (#11)
	        try:
	            from .. import templates as _tmpl
	            _tmpl.discover_template_ids(db)
	        except Exception:
	            pass""",
                """        # Template discovery targets apex-mcp 24.2 metadata and is skipped
	        # for the direct APEX 24.1.3 compatibility profile.""",
            )
        )
        state = "APPLIED" if any(changes) else "PRESENT"
        print(f"APEX_MCP_DIRECT_CONNECTION_PATCH_{state}")
    except RuntimeError as err:
        logging.error(f"Patch operation failed: {err}")
        raise SystemExit(1) from err
    except Exception as err:
        logging.exception(f"Unexpected error during patch: {err}")
        raise SystemExit(1) from err

    return 0


if __name__ == "__main__":
    main()
