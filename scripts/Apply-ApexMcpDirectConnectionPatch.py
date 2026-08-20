#!/usr/bin/env python3
"""Patch the managed apex-mcp checkout for direct Oracle connections."""

import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / ".upstreams" / "apex-mcp" / "apex_mcp"


def replace_once(path, old, new):
	"""Replace code pattern once, with error handling and logging.

	Args:
			path: Path to file to patch
			old: Pattern to find
			new: Replacement pattern

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
		err_msg = f"Unsupported upstream revision: expected code not found in {path}"
		logging.error(err_msg)
		raise RuntimeError(err_msg)

	try:
		path.write_text(content.replace(old, new, 1), encoding="utf-8")
	except (OSError, UnicodeEncodeError) as err:
		logging.error(f"Failed to write {path}: {err}")
		raise SystemExit(1) from err

	return True


def main():
	db_file = PACKAGE / "db.py"
	config_file = PACKAGE / "config.py"
	sql_tools_file = PACKAGE / "tools" / "sql_tools.py"
	if not all(path.is_file() for path in (db_file, config_file, sql_tools_file)):
		err_msg = (
			"Managed apex-mcp upstream is missing. Run Initialize-ApexSkillUpstreams-V2.ps1 first."
		)
		logging.error(err_msg)
		raise SystemExit(err_msg)

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


if __name__ == "__main__":
	main()
