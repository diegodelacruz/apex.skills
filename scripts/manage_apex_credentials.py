#!/usr/bin/env python3
"""Store, import, and validate secure APEX environment profiles."""

import getpass
import importlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_utils import CLIParser, exit_with_error

SERVICE = "apex-skills"
APEX_SERVICE = "apex-skills-apex"
REQUIRED_FIELDS = ("db_user", "db_pass", "dsn", "workspace_id", "schema", "workspace_name")
APEX_REQUIRED_FIELDS = ("base_url", "workspace", "apex_user", "apex_pass")
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
    profile, _ = read_profile(keyring, SERVICE, environment)
    return profile


def read_profile(keyring: Any, service: str, environment: str) -> tuple[Optional[Dict[str, Any]], str]:
    """Read a keyring profile without leaking keyring or JSON errors.

    The state is deliberately separate from the public compatibility helpers so
    callers can distinguish a missing profile from an unreadable or malformed
    one without printing credential material.
    """
    try:
        raw = keyring.get_password(service, environment)
    except Exception:
        return None, "invalid"
    if not raw:
        return None, "missing"
    try:
        profile = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return None, "invalid"
    if not isinstance(profile, dict):
        return None, "invalid"
    return profile, "ready"


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


def get_apex_profile(keyring: Any, environment: str) -> Optional[Dict[str, Any]]:
    """Return the separately stored App Builder profile without printing it."""
    profile, _ = read_profile(keyring, APEX_SERVICE, environment)
    return profile


def save_apex_profile(keyring: Any, environment: str, profile: Dict[str, Any]) -> None:
    """Store an App Builder credential independently from Oracle credentials."""
    missing = [field for field in APEX_REQUIRED_FIELDS if not profile.get(field)]
    if missing:
        exit_with_error(f"APEX profile incomplete. Missing: {', '.join(missing)}")
    keyring.set_password(APEX_SERVICE, environment, json.dumps(profile))
    print(f"APEX_PROFILE_SAVED environment={environment} service={APEX_SERVICE}")


def apex_status(keyring: Any, environment: str) -> int:
    """Report only profile readiness; usernames, URLs, and passwords stay private."""
    profile, profile_state = read_profile(keyring, APEX_SERVICE, environment)
    if profile_state == "invalid":
        print(f"APEX_PROFILE_INVALID environment={environment}")
        return 1
    if not profile:
        print(f"APEX_PROFILE_MISSING environment={environment}")
        return 1
    missing = [field for field in APEX_REQUIRED_FIELDS if not profile.get(field)]
    print(f"APEX_PROFILE_{'INCOMPLETE' if missing else 'READY'} environment={environment}")
    return int(bool(missing))


def set_apex_profile(keyring: Any, environment: str) -> None:
    """Prompt locally and persist an App Builder credential only in the keyring."""
    profile = {
        "base_url": input("APEX App Builder URL: ").strip().rstrip("/"),
        "workspace": input("APEX workspace: ").strip(),
        "apex_user": input("APEX user: ").strip(),
        "apex_pass": getpass.getpass("APEX password: "),
    }
    save_apex_profile(keyring, environment, profile)


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


def connect_with_retry(oracledb: Any, profile: Dict[str, Any], retries: int = 1, delay: float = 3.0) -> Any:
    """Connect to Oracle with a single retry on transient network errors."""
    kwargs = connection_kwargs(profile)
    last_error: Exception = RuntimeError("no attempt")
    for attempt in range(1 + retries):
        try:
            return oracledb.connect(**kwargs)
        except Exception as exc:
            last_error = exc
            if attempt < retries and _is_transient(exc):
                time.sleep(delay)
            else:
                raise
    raise last_error


def _is_transient(exc: BaseException) -> bool:
    """True for DNS/network errors worth retrying once."""
    msg = str(exc).lower()
    return "getaddrinfo" in msg or "timed out" in msg or "temporarily unavailable" in msg


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

    with connect_with_retry(oracledb, profile) as connection:
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
    """Import Oracle DB and (if present) APEX App Builder profiles from .env."""
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

    apex_prefix = "APEX_TESTING" if environment == "test" else "APEX_PRODUCTION"
    apex_fields = {
        "base_url": values.get(f"{apex_prefix}_BASE_URL", ""),
        "workspace": values.get(f"{apex_prefix}_WORKSPACE", ""),
        "apex_user": values.get(f"{apex_prefix}_USER", ""),
        "apex_pass": values.get(f"{apex_prefix}_PASSWORD", ""),
    }
    if all(apex_fields.values()):
        apex_fields["base_url"] = apex_fields["base_url"].rstrip("/")
        save_apex_profile(keyring, environment, apex_fields)
        print(f"APEX_PROFILE_IMPORTED environment={environment} source={env_file.name}")
    else:
        present = [k for k, v in apex_fields.items() if v]
        if present:
            print(f"APEX_PROFILE_SKIPPED environment={environment} reason=incomplete")


def status(keyring: Any, environment: str) -> int:
    """Check profile status."""
    profile, profile_state = read_profile(keyring, SERVICE, environment)
    if profile_state == "invalid":
        print(f"ORACLE_PROFILE_INVALID environment={environment}")
        return 1
    if not profile:
        print(f"ORACLE_PROFILE_MISSING environment={environment}")
        return 1

    missing = [field for field in REQUIRED_FIELDS if not profile.get(field)]
    status_str = "READY" if not missing else "INCOMPLETE"
    print(f"ORACLE_PROFILE_{status_str} environment={environment}", end="")
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
        with connect_with_retry(oracledb, profile) as connection:
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


def oracle_error_code(error: BaseException) -> Optional[str]:
    """Extract only an Oracle code, never its potentially sensitive message."""
    match = re.search(r"\bORA-(\d{5})\b", str(error), flags=re.IGNORECASE)
    return match.group(1) if match else None


def classify_connection_error(error: BaseException) -> str:
    """Classify connection-opening errors from evidence available locally."""
    code = oracle_error_code(error)
    if code in {"01017", "28000", "28001"}:
        return "ORACLE_AUTH_FAIL"
    if code in {"12154", "12514", "12541"}:
        return "ORACLE_CONNECTION_FAIL"
    return "ORACLE_PROBE_FAIL"


def _print_probe_error(status_name: str, environment: str, error: BaseException) -> None:
    """Emit a classification and, where known, only the Oracle error code."""
    code = oracle_error_code(error)
    suffix = f" error=ORA-{code}" if code else ""
    print(f"{status_name} environment={environment}{suffix}")


def probe(keyring: Any, environment: str) -> int:
    """Read safe Oracle session metadata with the configured credential."""
    profile, profile_state = read_profile(keyring, SERVICE, environment)
    if profile_state == "invalid":
        print(f"ORACLE_PROFILE_INVALID environment={environment}")
        return 1
    if profile_state == "missing":
        print(f"ORACLE_PROFILE_MISSING environment={environment}")
        return 1
    if any(not profile.get(field) for field in REQUIRED_FIELDS):
        print(f"ORACLE_PROFILE_INCOMPLETE environment={environment}")
        return 1
    try:
        oracledb = import_module_safe("oracledb")
        connection = connect_with_retry(oracledb, profile)
    except Exception as error:
        _print_probe_error(classify_connection_error(error), environment, error)
        return 1
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select sys_context('userenv', 'session_user'), "
                    "sys_context('userenv', 'current_schema') from dual"
                )
                session_user, schema = cursor.fetchone()
    except Exception as error:
        _print_probe_error("ORACLE_PROBE_FAIL", environment, error)
        return 1
    print(f"ORACLE_CONNECTION_PASS environment={environment} user={session_user} schema={schema}")
    return 0


def sqlcl_conn(keyring: Any, environment: str) -> int:
    """Emit the SQLcl connection string for use by execution scripts."""
    profile, profile_state = read_profile(keyring, SERVICE, environment)
    if profile_state != "ready" or not profile:
        print(f"SQLCL_CONN_FAIL environment={environment} reason=profile_{profile_state or 'missing'}")
        return 1
    user = profile.get("db_user", "")
    password = profile.get("db_pass", "")
    dsn = profile.get("dsn", "")
    if not user or not password or not dsn:
        print(f"SQLCL_CONN_FAIL environment={environment} reason=incomplete_credentials")
        return 1
    print(f"{user}/{password}@{dsn}")
    return 0


def main() -> int:
    """Main entry point."""
    parser = CLIParser("Manage secure APEX environment profiles")
    parser.add_argument(
        "action",
        choices=("set", "set-apex", "import-env", "status", "apex-status", "validate", "probe", "sqlcl-conn"),
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
    elif args.action == "set-apex":
        set_apex_profile(keyring, args.environment)
        return 0
    elif args.action == "import-env":
        import_env_profile(keyring, args.environment, args.env_file)
        return 0
    elif args.action == "status":
        return status(keyring, args.environment)
    elif args.action == "apex-status":
        return apex_status(keyring, args.environment)
    elif args.action == "probe":
        return probe(keyring, args.environment)
    elif args.action == "sqlcl-conn":
        return sqlcl_conn(keyring, args.environment)
    else:
        return validate(keyring, args.environment)


if __name__ == "__main__":
    sys.exit(main())
