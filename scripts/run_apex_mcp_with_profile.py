#!/usr/bin/env python3
"""Start the managed APEX MCP with credentials read from the repository .env."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from cli_utils import CLIParser, configured_environment, exit_with_error
from manage_apex_credentials import discover_apex_metadata, get_profile, oracle_error_code

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_MAPPING = {
    "ORACLE_DB_USER": "db_user",
    "ORACLE_DB_PASS": "db_pass",  # pragma: allowlist secret
    "ORACLE_DSN": "dsn",
    "APEX_WORKSPACE_ID": "workspace_id",
    "APEX_SCHEMA": "schema",
    "APEX_WORKSPACE_NAME": "workspace_name",
}
OPTIONAL_MAPPING = {
    "ORACLE_WALLET_DIR": "wallet_dir",
    "ORACLE_WALLET_PASSWORD": "wallet_pass",  # pragma: allowlist secret
}


def main() -> None:
    parser = CLIParser("Start apex-mcp with credentials from the repository .env")
    parser.add_environment_arg(default=configured_environment())
    parser.add_argument("mcp_args", nargs="*", help="Additional arguments to pass to apex-mcp")
    args = parser.parse_args()
    if args.environment is None:
        exit_with_error(
            "No target environment selected; set DB_ENV in .env or pass --environment.", "ENVIRONMENT_REQUIRED"
        )

    profile = get_profile(args.environment)
    if not profile:
        exit_with_error(f"Incomplete .env Oracle profile for {args.environment}.", "ENV_PROFILE_INCOMPLETE")
    metadata_fields = ("workspace_id", "schema", "workspace_name")
    if not all(profile.get(field) for field in metadata_fields):
        try:
            profile = discover_apex_metadata(profile)
        except Exception as error:
            code = oracle_error_code(error)
            suffix = f" error=ORA-{code}" if code else f" error={type(error).__name__}"
            exit_with_error(
                f"Cannot prepare the .env profile for the selected APEX workspace:{suffix}", "ENV_PROFILE_INVALID"
            )

    missing = [name for name, profile_name in REQUIRED_MAPPING.items() if not profile.get(profile_name)]
    if missing:
        exit_with_error("Incomplete .env profile; missing workspace metadata: " + ", ".join(missing))

    environment = os.environ.copy()
    for name in (*REQUIRED_MAPPING, *OPTIONAL_MAPPING):
        environment.pop(name, None)
    for environment_name, profile_name in {**REQUIRED_MAPPING, **OPTIONAL_MAPPING}.items():
        if profile.get(profile_name):
            environment[environment_name] = str(profile[profile_name])

    result = subprocess.run(
        [sys.executable, "-m", "apex_mcp", *args.mcp_args],
        env=environment,
        check=False,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
