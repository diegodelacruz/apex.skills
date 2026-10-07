#!/usr/bin/env python3
"""Manage Oracle and App Builder profiles stored only in the repository .env."""

from __future__ import annotations

import getpass
import importlib
import re
import sys
import time
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_utils import CLIParser, configured_environment, exit_with_error
from scripts.env_credentials import ENV_FILE, load_apex_profile, load_database_profile, update_env

REQUIRED_FIELDS = ("db_user", "db_pass", "dsn")
APEX_REQUIRED_FIELDS = ("base_url", "workspace", "apex_user", "apex_pass")
ALLOWED_MODULES = {"oracledb"}


def import_module_safe(name: str) -> Any:
    """Import only the database driver used by direct .env connections."""
    if name not in ALLOWED_MODULES:
        exit_with_error(f"Module '{name}' is not in the allowed list: {', '.join(ALLOWED_MODULES)}")
    try:
        return importlib.import_module(name)
    except ImportError:
        exit_with_error("Missing dependency: oracledb. Install requirements.txt first.")


def get_profile(environment: str, env_file: Path = ENV_FILE) -> dict[str, str] | None:
    """Read the selected Oracle profile from .env."""
    profile, missing = load_database_profile(environment, env_file)
    return profile if not missing else None


def read_profile(service: str, environment: str, env_file: Path = ENV_FILE) -> tuple[dict[str, str] | None, str]:
    """Read an Oracle or App Builder profile from .env only."""
    if service == "apex-skills":
        profile, missing = load_database_profile(environment, env_file)
    elif service == "apex-skills-apex":
        profile, missing = load_apex_profile(environment, env_file)
    else:
        return None, "missing"
    if missing:
        return None, "incomplete" if env_file.is_file() else "missing"
    return profile, "ready"


def get_apex_profile(environment: str, env_file: Path = ENV_FILE) -> dict[str, str] | None:
    """Read the separate App Builder profile from .env."""
    profile, missing = load_apex_profile(environment, env_file)
    return profile if not missing else None


def _profile_env_prefix(environment: str, prefix: str) -> str:
    normalized = environment.strip().lower()
    if normalized in {"test", "testing"}:
        return f"{prefix}_TESTING"
    if normalized in {"production", "prod"}:
        return f"{prefix}_PRODUCTION"
    exit_with_error("Environment must be test or production.", "ENVIRONMENT_INVALID")


def save_profile(environment: str, profile: dict[str, str], env_file: Path = ENV_FILE) -> None:
    """Persist Oracle credential fields to the sole .env source of truth."""
    prefix = _profile_env_prefix(environment, "DB")
    required = ("db_user", "db_pass", "host", "port", "service")
    missing = [field for field in required if not profile.get(field)]
    if missing:
        exit_with_error(f"Profile incomplete. Missing: {', '.join(missing)}", "PROFILE_INCOMPLETE")
    values = {
        f"{prefix}_USER": profile["db_user"],
        f"{prefix}_PASSWORD": profile["db_pass"],
        f"{prefix}_HOST": profile["host"],
        f"{prefix}_PORT": profile["port"],
        f"{prefix}_SID": profile["service"],
    }
    for source, suffix in (("wallet_dir", "WALLET_DIR"), ("wallet_pass", "WALLET_PASSWORD")):
        if source in profile:
            values[f"{prefix}_{suffix}"] = profile[source]
    update_env(values, env_file)
    print(f"ENV_PROFILE_SAVED environment={environment} source={env_file.name}")


def save_apex_profile(environment: str, profile: dict[str, str], env_file: Path = ENV_FILE) -> None:
    """Persist App Builder credentials to the same .env source of truth."""
    prefix = _profile_env_prefix(environment, "APEX")
    missing = [field for field in APEX_REQUIRED_FIELDS if not profile.get(field)]
    if missing:
        exit_with_error(f"APEX profile incomplete. Missing: {', '.join(missing)}", "PROFILE_INCOMPLETE")
    update_env(
        {
            f"{prefix}_BASE_URL": profile["base_url"].rstrip("/"),
            f"{prefix}_WORKSPACE": profile["workspace"],
            f"{prefix}_USER": profile["apex_user"],
            f"{prefix}_PASSWORD": profile["apex_pass"],
        },
        env_file,
    )
    print(f"APEX_ENV_PROFILE_SAVED environment={environment} source={env_file.name}")


def apex_status(environment: str, env_file: Path = ENV_FILE) -> int:
    """Report App Builder profile readiness without printing secret values."""
    _, state = read_profile("apex-skills-apex", environment, env_file)
    print(f"APEX_PROFILE_{'READY' if state == 'ready' else state.upper()} environment={environment}")
    return 0 if state == "ready" else 1


def set_apex_profile(environment: str) -> None:
    """Prompt locally and write App Builder values to .env."""
    profile = {
        "base_url": input("APEX base URL: ").strip(),
        "workspace": input("APEX workspace: ").strip(),
        "apex_user": input("APEX user: ").strip(),
        "apex_pass": getpass.getpass("APEX password: "),
    }
    save_apex_profile(environment, profile)


def connection_kwargs(profile: dict[str, str]) -> dict[str, str]:
    """Build python-oracledb connection arguments from .env profile fields."""
    kwargs = {"user": profile["db_user"], "password": profile["db_pass"], "dsn": profile["dsn"]}
    if profile.get("wallet_dir"):
        kwargs["config_dir"] = profile["wallet_dir"]
        kwargs["wallet_location"] = profile["wallet_dir"]
        if profile.get("wallet_pass"):
            kwargs["wallet_password"] = profile["wallet_pass"]
    return kwargs


def connect_with_retry(oracledb: Any, profile: dict[str, str], retries: int = 1, delay: float = 3.0) -> Any:
    """Connect to Oracle with one retry for transient network errors."""
    last_error: Exception = RuntimeError("no attempt")
    for attempt in range(1 + retries):
        try:
            return oracledb.connect(**connection_kwargs(profile))
        except Exception as exc:
            last_error = exc
            message = str(exc).lower()
            transient = any(value in message for value in ("getaddrinfo", "timed out", "temporarily unavailable"))
            if attempt < retries and transient:
                time.sleep(delay)
            else:
                raise
    raise last_error


def discover_apex_metadata(profile: dict[str, str]) -> dict[str, str]:
    """Discover workspace/schema metadata using the supplied .env credentials."""
    oracledb = import_module_safe("oracledb")
    with connect_with_retry(oracledb, profile) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "select workspace_id from apex_workspace_schemas "
                "where schema = sys_context('userenv', 'current_schema') order by workspace_id"
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
                    profile["schema"] = str(cursor.fetchone()[0])
                    return profile
            cursor.execute(
                "select owner, workspace, workspace_id from ("
                "select owner, workspace, workspace_id, count(*) application_count "
                "from apex_applications where workspace <> 'INTERNAL' "
                "and workspace not like 'COM.ORACLE.%' group by owner, workspace, workspace_id "
                "order by count(*) desc, workspace) where rownum = 1"
            )
            workspace = cursor.fetchone()
            if not workspace:
                exit_with_error("No functional APEX workspace found", "WORKSPACE_NOT_FOUND")
            profile["schema"], profile["workspace_name"], workspace_id = map(str, workspace)
            profile["workspace_id"] = str(workspace_id)
    return profile


def set_profile(environment: str) -> None:
    """Prompt locally and write Oracle credentials to .env."""
    profile = {
        "db_user": input("Oracle user: ").strip(),
        "db_pass": getpass.getpass("Oracle password: "),
        "host": input("Oracle host: ").strip(),
        "port": input("Oracle port [1521]: ").strip() or "1521",
        "service": input("Oracle service/SID: ").strip(),
    }
    save_profile(environment, profile)


def import_env_profile(environment: str, env_file: Path = ENV_FILE) -> None:
    """Validate the selected .env profile; credentials are not copied elsewhere."""
    profile, missing = load_database_profile(environment, env_file)
    if missing or profile is None:
        exit_with_error(f"Missing .env values: {', '.join(missing)}", "ENV_PROFILE_INCOMPLETE")
    print(f"ENV_PROFILE_READY environment={environment} source={env_file.name}")


def status(environment: str, env_file: Path = ENV_FILE) -> int:
    """Report required Oracle values in .env without attempting a connection."""
    profile, state = read_profile("apex-skills", environment, env_file)
    print(f"ORACLE_PROFILE_{'READY' if state == 'ready' and profile else state.upper()} environment={environment}")
    return 0 if state == "ready" else 1


def validate(environment: str) -> int:
    """Validate .env credentials with a read-only identity query."""
    profile = get_profile(environment)
    if not profile:
        print(f"PROFILE_VALIDATION_FAIL environment={environment} reason=env_profile_missing", file=sys.stderr)
        return 1
    oracledb = import_module_safe("oracledb")
    try:
        with connect_with_retry(oracledb, profile) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select sys_context('userenv', 'current_schema') from dual")
                cursor.fetchone()
    except Exception as error:
        code = oracle_error_code(error)
        suffix = f" error=ORA-{code}" if code else f" error={type(error).__name__}"
        print(f"PROFILE_VALIDATION_FAIL environment={environment}{suffix}", file=sys.stderr)
        return 1
    print(f"PROFILE_VALIDATION_PASS environment={environment} mode=read-only source=.env")
    return 0


def oracle_error_code(error: BaseException) -> str | None:
    """Extract an Oracle error code without exposing the driver message."""
    match = re.search(r"\bORA-(\d{5})\b", str(error), flags=re.IGNORECASE)
    return match.group(1) if match else None


def classify_connection_error(error: BaseException) -> str:
    code = oracle_error_code(error)
    if code in {"01017", "28000", "28001"}:
        return "ORACLE_AUTH_FAIL"
    if code in {"12154", "12514", "12541"}:
        return "ORACLE_CONNECTION_FAIL"
    return "ORACLE_PROBE_FAIL"


def probe(environment: str) -> int:
    """Read session identity with the Oracle credentials currently in .env."""
    profile = get_profile(environment)
    if not profile:
        print(f"ORACLE_PROFILE_INCOMPLETE environment={environment} source=.env")
        return 1
    try:
        oracledb = import_module_safe("oracledb")
        connection = connect_with_retry(oracledb, profile)
    except Exception as error:
        code = oracle_error_code(error)
        suffix = f" error=ORA-{code}" if code else f" error={type(error).__name__}"
        print(f"{classify_connection_error(error)} environment={environment}{suffix}")
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
        code = oracle_error_code(error)
        suffix = f" error=ORA-{code}" if code else f" error={type(error).__name__}"
        print(f"ORACLE_PROBE_FAIL environment={environment}{suffix}")
        return 1
    print(f"ORACLE_CONNECTION_PASS environment={environment} user={session_user} schema={schema} source=.env")
    return 0


def sqlcl_conn(environment: str) -> int:
    """Print an internal SQLcl connect string sourced from .env."""
    profile = get_profile(environment)
    if not profile:
        print(f"SQLCL_CONN_FAIL environment={environment} reason=env_profile_incomplete")
        return 1
    print(f"{profile['db_user']}/{profile['db_pass']}@{profile['dsn']}")
    return 0


def main() -> int:
    parser = CLIParser("Manage Oracle and App Builder profiles stored in .env")
    parser.add_argument(
        "action",
        choices=("set", "set-apex", "import-env", "status", "apex-status", "validate", "probe", "sqlcl-conn"),
        help="Manage, inspect, or validate the repository .env profile",
    )
    parser.add_environment_arg()
    args = parser.parse_args()
    if args.environment is None:
        args.environment = configured_environment()
    if args.environment is None:
        exit_with_error(
            "No target environment selected; set DB_ENV in the repository .env or pass --environment.",
            "ENVIRONMENT_REQUIRED",
        )
    if args.action == "set":
        set_profile(args.environment)
        return 0
    elif args.action == "set-apex":
        set_apex_profile(args.environment)
        return 0
    elif args.action == "import-env":
        import_env_profile(args.environment)
        return 0
    elif args.action == "status":
        return status(args.environment)
    elif args.action == "apex-status":
        return apex_status(args.environment)
    elif args.action == "probe":
        return probe(args.environment)
    elif args.action == "sqlcl-conn":
        return sqlcl_conn(args.environment)
    return validate(args.environment)


if __name__ == "__main__":
    raise SystemExit(main())
