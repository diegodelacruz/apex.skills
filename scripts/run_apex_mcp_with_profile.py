#!/usr/bin/env python3
"""Start apex-mcp with a TEST or production profile held in the OS keyring.

Retrieves credentials from the system keyring, maps them to the environment
variables apex-mcp expects, and launches the MCP server subprocess.

Status: ACTIVE
Tests: Infrastructure script (no automated tests)
Dependencies: keyring, manage_apex_credentials.py (for profile setup)
"""

import json
import os
import subprocess
import sys

from scripts.cli_utils import CLIParser, exit_with_error

SERVICE = "apex-skills"
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
    parser = CLIParser("Start apex-mcp with a secure profile from OS keyring")
    parser.add_environment_arg()
    parser.add_argument("mcp_args", nargs="*", help="Additional arguments to pass to apex-mcp")
    args = parser.parse_args()

    try:
        import keyring
    except ImportError:
        exit_with_error("Missing dependency: keyring. Install requirements.txt in the shared skills environment.")

    raw_profile = keyring.get_password(SERVICE, args.environment)
    if not raw_profile:
        exit_with_error(f"Missing secure profile: {args.environment}. Import or set it first.")
        return
    try:
        profile = json.loads(raw_profile)
    except json.JSONDecodeError:
        exit_with_error(f"Invalid secure profile: {args.environment}. Import or set it again.")

    missing = [
        environment_name for environment_name, profile_name in REQUIRED_MAPPING.items() if not profile.get(profile_name)
    ]
    if missing:
        exit_with_error("Incomplete secure profile; missing mapped values: " + ", ".join(missing))

    environment = os.environ.copy()
    for environment_name, profile_name in {**REQUIRED_MAPPING, **OPTIONAL_MAPPING}.items():
        if profile.get(profile_name):
            environment[environment_name] = str(profile[profile_name])

    # On Windows, os.execvpe can terminate the stdio process before Codex CLI
    # receives the initialize response. subprocess.run preserves MCP stdio handles.
    result = subprocess.run(
        [sys.executable, "-m", "apex_mcp", *args.mcp_args],
        env=environment,
        check=False,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
