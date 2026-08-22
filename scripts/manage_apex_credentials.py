#!/usr/bin/env python3
"""Store, import, and validate secure APEX environment profiles."""

import getpass
import importlib
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from cli_utils import CLIParser, exit_with_error

SERVICE = "apex-skills"
REQUIRED_FIELDS = ("db_user", "db_pass", "dsn", "workspace_id", "schema", "workspace_name")
ALLOWED_MODULES = {"keyring", "oracledb"}


def import_module_safe(name: str) -> Any:
    """Safely import a module from the allowed list.

    Args:
            name: Module name to import (must be in ALLOWED_MODULES)

    Returns:
            The imported module object

    Raises:
            SystemExit: If module not in whitelist or import fails
    """
    if name not in ALLOWED_MODULES:
        exit_with_error(f"Module '{name}' is not in the allowed list: {', '.join(ALLOWED_MODULES)}")

    try:
        return importlib.import_module(name)
    except ImportError:
        exit_with_error(f"Missing dependency: {name}. Install requirements.txt first.")


def get_profile(keyring: Any, environment: str) -> Optional[Dict[str, Any]]:
    """Get a profile from the secure keyring.

    Args:
            keyring: The keyring module
            environment: Environment name ('test' or 'production')

    Returns:
            Profile dictionary or None if not found
    """
    raw = keyring.get_password(SERVICE, environment)
    return json.loads(raw) if raw else None


def save_profile(keyring: Any, environment: str, profile: Dict[str, Any]) -> None:
    """Save a profile to the secure keyring.

    Args:
            keyring: The keyring module
            environment: Environment name
            profile: Profile dictionary

    Raises:
            SystemExit: If profile is incomplete
    """
    missing = [field for field in REQUIRED_FIELDS if not profile.get(field)]
    if missing:
        exit_with_error(f"Profile incomplete. Missing: {', '.join(missing)}")

    keyring.set_password(SERVICE, environment, json.dumps(profile))
    print(f"PROFILE_SAVED environment={environment} service={SERVICE}")


def parse_env(path: Path) -> Dict[str, str]:
    """Parse environment file.

    Args:
            path: Path to .env file

    Returns:
            Dictionary of key-value pairs
    """
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def connection_kwargs(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Build Oracle connection kwargs from profile.

    Args:
            profile: Profile dictionary

    Returns:
            Dictionary of connection parameters
    """
    kwargs = {
        "user": profile["db_user"],
        "password": profile["db_pass"],
        "dsn": profile["dsn"],
    }
    if profile.get("wallet_dir"):
        kwargs.update(
            config_dir=profile["wallet_dir"],
            wallet_location=profile["wallet_dir"],
        )
        if profile.get("wallet_pass"):
            kwargs["wallet_password"] = profile["wallet_pass"]
    return kwargs


def discover_apex_metadata(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Discover APEX metadata from database connection.

    Args:
            profile: Profile with db credentials

    Returns:
            Profile with discovered APEX metadata

    Raises:
            SystemExit: If no functional APEX workspace found
    """
    oracledb = import_module_safe("oracledb")

    with oracledb.connect(**connection_kwargs(profile)) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "select workspace_id from apex_workspace_schemas "
                "where schema = sys_context('userenv', 'current_schema') "
                "order by workspace_id"
            )
            workspace_ids = [str(row[0]) for row in cursor.fetchall()]

            if len(workspace_ids) == 1:
                cursor.execute(
                    "select workspace from apex_workspaces where workspace_id = :workspace_id",
                    [workspace_ids[0]],
                )
                workspace = cursor.fetchone()
                if workspace:
                    profile["workspace_id"] = workspace_ids[0]
                    profile["workspace_name"] = str(workspace[0])
                    cursor.execute("select sys_context('userenv', 'current_schema') from dual")
                    profile["schema"] = cursor.fetchone()[0]
                    return profile

            cursor.execute(
                "select owner, workspace, workspace_id from ("
                "  select owner, workspace, workspace_id, count(*) application_count "
                "  from apex_applications "
                "  where workspace <> 'INTERNAL' and workspace not like 'COM.ORACLE.%' "
                "  group by owner, workspace, workspace_id "
                "  order by count(*) desc, workspace"
                ") where rownum = 1"
            )
            workspace = cursor.fetchone()
            if not workspace:
                exit_with_error("No functional APEX workspace found")

    profile["schema"], profile["workspace_name"], workspace_id = workspace
    profile["workspace_id"] = str(workspace_id)
    return profile


def set_profile(keyring: Any, environment: str) -> None:
    """Interactively set a profile."""
    profile = {
        "db_user": input("Oracle user: ").strip(),
        "db_pass": getpass.getpass("Oracle password: "),
        "dsn": input("Oracle DSN: ").strip(),
    }
    save_profile(keyring, environment, discover_apex_metadata(profile))


def import_env_profile(keyring: Any, environment: str, env_file: Path) -> None:
    """Import profile from .env file."""
    values = parse_env(env_file)
    prefix = "DB_TESTING" if environment == "test" else "DB_PRODUCTION"
    needed = tuple(f"{prefix}_{field}" for field in ("USER", "PASSWORD", "HOST", "PORT", "SID"))
    missing = [name for name in needed if not values.get(name)]

    if missing:
        exit_with_error(f"Missing .env values: {', '.join(missing)}")

    profile = {
        "db_user": values[f"{prefix}_USER"],
        "db_pass": values[f"{prefix}_PASSWORD"],
        "dsn": "{}:{}/{}".format(
            values[f"{prefix}_HOST"],
            values[f"{prefix}_PORT"],
            values[f"{prefix}_SID"],
        ),
    }
    save_profile(keyring, environment, discover_apex_metadata(profile))
    print(f"PROFILE_IMPORTED environment={environment} source={env_file.name}")


def status(keyring: Any, environment: str) -> int:
    """Check profile status."""
    profile = get_profile(keyring, environment)
    if not profile:
        print(f"PROFILE_MISSING environment={environment}")
        return 1

    missing = [field for field in REQUIRED_FIELDS if not profile.get(field)]
    status_str = "READY" if not missing else "INCOMPLETE"
    print(f"PROFILE_{status_str} environment={environment}", end="")
    if missing:
        print(f" missing={','.join(missing)}")
    else:
        print()

    return int(bool(missing))


def validate(keyring: Any, environment: str) -> int:
    """Validate profile with database connection."""
    profile = get_profile(keyring, environment)
    if not profile or any(not profile.get(field) for field in REQUIRED_FIELDS):
        exit_with_error("Profile is missing or incomplete", "PROFILE_VALIDATION_FAIL")

    oracledb = import_module_safe("oracledb")
    try:
        with oracledb.connect(**connection_kwargs(profile)) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select sys_context('userenv', 'current_schema') from dual")
                cursor.fetchone()
    except Exception as error:
        print(
            f"PROFILE_VALIDATION_FAIL environment={environment} error={type(error).__name__}",
            file=sys.stderr,
        )
        return 1

    print(f"PROFILE_VALIDATION_PASS environment={environment} mode=read-only")
    return 0


def main() -> int:
    """Main entry point."""
    parser = CLIParser("Manage secure APEX environment profiles")
    parser.add_argument(
        "action",
        choices=("set", "import-env", "status", "validate"),
        help="Action to perform",
    )
    parser.add_environment_arg()
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).resolve().parent.parent / ".env",
        help="Path to .env file for import-env action",
    )

    args = parser.parse_args()
    keyring = import_module_safe("keyring")

    if args.action == "set":
        set_profile(keyring, args.environment)
        return 0
    elif args.action == "import-env":
        import_env_profile(keyring, args.environment, args.env_file)
        return 0
    elif args.action == "status":
        return status(keyring, args.environment)
    else:
        return validate(keyring, args.environment)


if __name__ == "__main__":
    sys.exit(main())
