#!/usr/bin/env python3
"""Controlled local MCP for Oracle/APEX artifacts executed through SQLcl.

The server is intentionally independent from the managed ``apex-mcp``
upstream.  It never exposes APEX internal-table tools or accepts inline SQL.
Oracle decides whether an artifact is authorized for the connected account.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_ENV = "APEX_SQLCL_RUNTIME_ROOT"
AUDIT_PATH = ROOT / "control-proyecto" / ".bitacora.json"
ORA_PATTERN = re.compile(r"ORA-(\d{5}):\s*(.+)", re.IGNORECASE)
PRIVILEGE_QUERY = """
select 'system_privilege=' || privilege from session_privs order by privilege;
select 'role=' || role from session_roles order by role;
select 'object_privilege=' || owner || '.' || table_name || ':' || privilege
from user_tab_privs
order by owner, table_name, privilege;
"""


@dataclass(frozen=True)
class CommandResult:
    """Sanitized SQLcl process result."""

    exit_code: int
    stdout: str
    stderr: str


def runtime_root() -> Path:
    """Return the per-user runtime root without creating it."""
    configured = os.environ.get(RUNTIME_ENV)
    if configured:
        return Path(configured)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "ApexSkills" / "runtimes"
    return ROOT / ".apex-runtime"


def runtime_state() -> dict[str, Any] | None:
    """Read the installer state without treating it as proof of Oracle access."""
    path = runtime_root() / "runtime-state.json"
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def doctor_report() -> dict[str, Any]:
    """Report local runtime readiness without opening an Oracle connection."""
    state = runtime_state()
    if state is None:
        return {
            "ready": False,
            "code": "RUNTIME_NOT_INSTALLED",
            "message": "El runtime administrado no está instalado. Ejecute Install-ApexControlledRuntime.ps1.",
        }
    java_home = Path(str(state.get("java_home", "")))
    sqlcl_path = Path(str(state.get("sqlcl_path", "")))
    java_exe = java_home / "bin" / "java.exe"
    if not java_exe.is_file() or not sqlcl_path.is_file():
        return {
            "ready": False,
            "code": "RUNTIME_INTEGRITY_FAILED",
            "message": "Falta Java o SQLcl en el runtime registrado. Reinstale el runtime administrado.",
        }
    environment = os.environ.copy()
    environment["JAVA_HOME"] = str(java_home)
    try:
        process = subprocess.run(
            [str(sqlcl_path), "-version"],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ready": False, "code": "RUNTIME_INTEGRITY_FAILED", "message": str(exc)}
    if process.returncode != 0:
        return {
            "ready": False,
            "code": "RUNTIME_INTEGRITY_FAILED",
            "message": "SQLcl no pudo iniciar con el Java administrado.",
        }
    return {
        "ready": True,
        "code": "READY",
        "message": "Runtime local listo; aún no se ha conectado a Oracle.",
        "sqlcl_version": state.get("sqlcl_version"),
        "java_version": state.get("java_version"),
    }


def load_profile(environment: str) -> tuple[dict[str, str] | None, dict[str, Any] | None]:
    """Load a local TEST/production profile and return only sanitized errors."""
    if environment not in {"test", "production"}:
        return None, {"code": "CONFIGURATION_REQUIRED", "message": "Ambiente inválido; use test o production."}
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return None, {"code": "PROFILE_MISSING", "message": "No existe .env; no se intentó conectar."}
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#") and "=" in cleaned:
            key, value = cleaned.split("=", 1)
            values[key.strip()] = value.strip()
    prefix = "DB_PRODUCTION" if environment == "production" else "DB_TESTING"
    required = ("USER", "PASSWORD", "HOST", "SID")
    missing = [field for field in required if not values.get(f"{prefix}_{field}")]
    if missing:
        return None, {
            "code": "PROFILE_MISSING",
            "message": "El perfil está incompleto; no se intentó conectar.",
            "missing_fields": missing,
        }
    return {
        "user": values[f"{prefix}_USER"],
        "password": values[f"{prefix}_PASSWORD"],
        "host": values[f"{prefix}_HOST"],
        "port": values.get(f"{prefix}_PORT", "1521"),
        "service": values[f"{prefix}_SID"],
    }, None


def sqlcl_result(
    profile: dict[str, str],
    statements: str,
    working_directory: str | None = None,
    bind_variables: dict[str, int] | None = None,
) -> CommandResult:
    """Run SQLcl with credentials over stdin, never command-line arguments."""
    state = runtime_state()
    if state is None:
        return CommandResult(1, "", "RUNTIME_NOT_INSTALLED")
    environment = os.environ.copy()
    environment["JAVA_HOME"] = str(state["java_home"])
    connection = "{user}/{password}@{host}:{port}/{service}".format(**profile)
    bind_setup: list[str] = []
    for name, value in (bind_variables or {}).items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name) or type(value) is not int:
            return CommandResult(1, "", "INVALID_BIND_VARIABLE")
        bind_setup.extend(
            (
                f"variable {name} number",
                "begin",
                f"    :{name} := {value};",
                "end;",
                "/",
            )
        )
    script = "\n".join(
        (
            "set echo off feedback off heading off pagesize 0 verify off",
            "whenever sqlerror exit sql.sqlcode rollback",
            f"connect {connection}",
            *bind_setup,
            statements,
            "exit",
        )
    )
    try:
        process = subprocess.run(
            [str(state["sqlcl_path"]), "-S", "/nolog"],
            capture_output=True,
            check=False,
            env=environment,
            input=script,
            text=True,
            timeout=120,
            cwd=working_directory,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CommandResult(1, "", f"SQLCL_RUNTIME_ERROR: {exc}")
    return CommandResult(process.returncode, process.stdout, process.stderr)


def classify_result(result: CommandResult) -> dict[str, Any]:
    """Map observed Oracle output to concise technical and user-facing states."""
    combined = "\n".join((result.stdout, result.stderr))
    match = ORA_PATTERN.search(combined)
    if result.exit_code == 0 and match is None:
        return {
            "ok": True,
            "code": "SUCCESS",
            "message": "Oracle completó la operación.",
            "exit_code": 0,
            "output": result.stdout.strip()[:2000],
        }
    technical = match.group(0) if match else combined.strip()[:500] or "SQLcl terminó con error sin detalle Oracle."
    code = "EXECUTION_ERROR"
    clear = "Oracle rechazó o no pudo completar la operación; no se declara éxito."
    if match and match.group(1) == "01031":
        code = "AUTHORIZATION_DENIED"
        clear = "La cuenta conectada no tiene el privilegio requerido para esta operación."
    elif match and match.group(1) in {"00942", "04043"}:
        code = "OBJECT_NOT_FOUND_OR_NOT_AUTHORIZED"
        clear = "El objeto no existe o la cuenta no puede verlo; Oracle no permite distinguir ambos casos."
    elif match and match.group(1) in {"12154", "12514", "12541"}:
        code = "CONNECTION_FAILED"
        clear = "No se pudo resolver o alcanzar el servicio Oracle configurado."
    elif (
        match
        and match.group(1) in {"20987", "20001"}
        and ("security group" in technical.lower() or "g_security_group_id" in technical.lower())
    ):
        code = "APEX_CONTEXT_INVALID"
        clear = "La sesión SQLcl no tiene un contexto APEX válido; no se intentó cambiar APEX."
    return {"ok": False, "code": code, "message": clear, "technical": technical, "exit_code": result.exit_code}


def workspace_sql_file(relative_path: str) -> Path:
    """Resolve a SQL artifact strictly inside this checkout."""
    candidate = (ROOT / relative_path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("El archivo SQL debe pertenecer al repositorio actual.") from exc
    if candidate.suffix.lower() != ".sql" or not candidate.is_file():
        raise ValueError("El artefacto debe ser un archivo .sql existente.")
    return candidate


def write_audit_event(environment: str, operation: str, source: Path, result: dict[str, Any]) -> None:
    """Append non-secret execution evidence for a versioned SQL artifact."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": environment,
        "operation": operation,
        "source": str(source.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "result": result["code"],
        "exit_code": result["exit_code"],
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def execute_artifact(relative_path: str, environment: str, operation: str) -> dict[str, Any]:
    """Execute one reviewed SQL artifact using the profile for an explicit environment."""
    readiness = doctor_report()
    if not readiness["ready"]:
        return readiness
    try:
        source = workspace_sql_file(relative_path)
    except ValueError as exc:
        return {"ok": False, "code": "INVALID_ARTIFACT", "message": str(exc)}
    profile, error = load_profile(environment)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}
    result = classify_result(sqlcl_result(profile, source.read_text(encoding="utf-8")))
    write_audit_event(environment, operation, source, result)
    return {**result, "environment": environment, "source": str(source.relative_to(ROOT))}


mcp = FastMCP(
    "apex-controlled-mcp",
    instructions=(
        "Use inspect_environment once when starting work in an environment to report its capabilities. "
        "Execute only reviewed SQL artifacts in the workspace. "
        "Oracle privileges are authoritative; report observed ORA errors without inventing authorization. "
        "Do not run per-operation APEX capability probes; execute the requested artifact "
        "and report Oracle/APEX results. "
        "Use native APEX export imports, never DML against APEX_240100.WWV_FLOW_* or internal APEX packages."
    ),
)


@mcp.tool(
    description="Verifica Java y SQLcl administrados sin conectarse a Oracle.",
    annotations={"readOnlyHint": True},
)
def doctor() -> dict[str, Any]:
    """Return local runtime readiness."""
    return doctor_report()


@mcp.tool(
    description="Comprueba identidad de la sesión Oracle con una consulta de solo lectura.",
    annotations={"readOnlyHint": True},
)
def inspect_oracle_session(environment: str = "test") -> dict[str, Any]:
    """Connect read-only and return the observed Oracle identity."""
    readiness = doctor_report()
    if not readiness["ready"]:
        return readiness
    profile, error = load_profile(environment)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}
    query = "select sys_context('userenv','session_user') || '|' || sys_context('userenv','current_schema') from dual;"
    result = classify_result(sqlcl_result(profile, query))
    if not result["ok"]:
        return {**result, "environment": environment}
    identity = next((line.strip() for line in result.get("output", "").splitlines() if "|" in line), None)
    return {**result, "environment": environment, "identity": identity}


def _environment_query() -> str:
    """Describe the connected APEX environments without hard-coded schemas."""
    return """
select record
from (
    select 1 as sequence_no,
           'session_user=' || sys_context('userenv', 'session_user') ||
           '|database_name=' || sys_context('userenv', 'db_name') ||
           '|container_name=' || sys_context('userenv', 'con_name') as record
    from dual
    union all
    select 2,
           'workspace_schema=' || workspace_name || '|' || schema
    from apex_workspace_schemas
    where workspace_name <> 'INTERNAL'
      and workspace_name not like 'COM.ORACLE.%'
    union all
    select 3,
           'workspace_applications=' || workspace || '|' || count(*)
    from apex_applications
    where workspace <> 'INTERNAL'
      and workspace not like 'COM.ORACLE.%'
    group by workspace
)
order by sequence_no, record;
"""


@mcp.tool(
    description="Informa al inicio las asociaciones APEX y aplicaciones disponibles del ambiente, sin modificar nada.",
    annotations={"readOnlyHint": True},
)
def inspect_environment(environment: str = "test") -> dict[str, Any]:
    """Return dynamic environment readiness; it informs but never blocks later operations."""
    readiness = doctor_report()
    if not readiness["ready"]:
        return readiness
    profile, error = load_profile(environment)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}
    result = classify_result(sqlcl_result(profile, _environment_query()))
    if not result["ok"]:
        return {**result, "environment": environment}
    identity: dict[str, str] = {}
    mappings: list[dict[str, str]] = []
    application_counts: list[dict[str, str]] = []
    for line in result.get("output", "").splitlines():
        value = line.strip()
        if value.startswith("workspace_schema="):
            workspace, _, schema = value.removeprefix("workspace_schema=").partition("|")
            mappings.append({"workspace": workspace, "schema": schema})
        elif value.startswith("workspace_applications="):
            workspace, _, count = value.removeprefix("workspace_applications=").partition("|")
            application_counts.append({"workspace": workspace, "applications": count})
        elif "=" in value:
            for item in value.split("|"):
                key, _, item_value = item.partition("=")
                if key and item_value:
                    identity[key] = item_value
    return {
        "ok": True,
        "code": "ENVIRONMENT_READY",
        "message": "Capacidades descubiertas; cada operación será decidida por Oracle/APEX al ejecutarse.",
        "environment": environment,
        "session_user": identity.get("session_user"),
        "database_name": identity.get("database_name"),
        "container_name": identity.get("container_name"),
        "workspace_schemas": mappings,
        "workspace_application_counts": application_counts,
    }


def _apex_context_query() -> str:
    """Return a metadata probe that uses a SQLcl bind for the application ID."""
    return """
select record
from (
    select 1 as sequence_no,
           'session_user=' || sys_context('userenv', 'session_user') ||
           '|database_name=' || sys_context('userenv', 'db_name') ||
           '|container_name=' || sys_context('userenv', 'con_name') as record
    from dual
    union all
    select 2,
           'application=' || application_id || '|workspace=' || workspace || '|owner=' || owner
    from apex_applications
    where application_id = :application_id
    union all
    select 3,
           'workspace_schema=' || schema
    from apex_workspace_schemas
    where workspace_name = (select workspace from apex_applications where application_id = :application_id)
    union all
    select 4,
           'anchor_page=' || min(case when page_id > 0 then page_id end)
    from apex_application_pages
    where application_id = :application_id
)
order by sequence_no;
"""


@mcp.tool(
    description="Verifica en solo lectura la asociación entre sesión SQLcl, aplicación, workspace y esquema APEX.",
    annotations={"readOnlyHint": True},
)
def inspect_apex_context(application_id: int, environment: str = "test") -> dict[str, Any]:
    """Verify the Oracle session, APEX application, workspace and parsing-schema mapping."""
    if not isinstance(application_id, int) or application_id <= 0:
        return {"ok": False, "code": "INVALID_APPLICATION", "message": "application_id debe ser un entero positivo."}
    readiness = doctor_report()
    if not readiness["ready"]:
        return readiness
    profile, error = load_profile(environment)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}
    result = classify_result(
        sqlcl_result(profile, _apex_context_query(), bind_variables={"application_id": application_id})
    )
    if not result["ok"]:
        return {**result, "environment": environment, "application_id": application_id}
    values: dict[str, str] = {}
    schemas: list[str] = []
    for line in result.get("output", "").splitlines():
        cleaned = line.strip()
        if cleaned.startswith("workspace_schema="):
            schemas.append(cleaned.removeprefix("workspace_schema="))
        elif "=" in cleaned:
            for item in cleaned.split("|"):
                key, _, value = item.partition("=")
                if key and value:
                    values[key] = value
    session_user = values.get("session_user", "")
    if "application" not in values:
        return {
            "ok": False,
            "code": "OBJECT_NOT_FOUND_OR_NOT_AUTHORIZED",
            "message": "La aplicación indicada no existe o la sesión no puede leer su metadata.",
            "environment": environment,
            "application_id": application_id,
        }
    context = {
        "environment": environment,
        "application_id": application_id,
        "workspace": values.get("workspace"),
        "parsing_schema": values.get("owner"),
        "session_user": session_user,
        "database_name": values.get("database_name"),
        "container_name": values.get("container_name"),
        "workspace_schemas": schemas,
        "anchor_page": values.get("anchor_page"),
    }
    if session_user.upper() not in {schema.upper() for schema in schemas}:
        return {
            "ok": False,
            "code": "APEX_CONTEXT_INVALID",
            "message": "La cuenta Oracle de SQLcl no está asociada al workspace de la aplicación.",
            **context,
        }
    return {"ok": True, "code": "SUCCESS", "message": "Contexto APEX asociado a la sesión SQLcl.", **context}


@mcp.tool(
    description="Prueba mediante una exportación temporal de solo lectura si SQLcl puede operar una aplicación APEX.",
    annotations={"readOnlyHint": True},
)
def probe_native_apex_context(application_id: int, environment: str = "test") -> dict[str, Any]:
    """Run a disposable SQLcl native export of one existing page before APEX deployment."""
    context = inspect_apex_context(application_id, environment)
    if not context.get("ok"):
        return context
    anchor_page = context.get("anchor_page")
    if not anchor_page or not str(anchor_page).isdigit():
        return {
            "ok": False,
            "code": "APEX_CONTEXT_INVALID",
            "message": "No hay página ancla para validar SQLcl.",
            **context,
        }
    profile, error = load_profile(environment)
    if error is not None or profile is None:
        return {"ok": False, **(error or {"code": "PROFILE_MISSING", "message": "Perfil no disponible."})}
    command = (
        f"apex export-components -applicationid {application_id} "
        f'-expcomponents "PAGE:{anchor_page}" -skipexportdate -overwrite-files'
    )
    with tempfile.TemporaryDirectory(prefix="apex-controlled-probe-") as temporary_directory:
        result = classify_result(sqlcl_result(profile, command, temporary_directory))
    if not result["ok"]:
        return {**result, **context}
    return {"ok": True, "code": "SUCCESS", "message": "SQLcl confirmó el contexto nativo APEX.", **context}


@mcp.tool(
    description="Informa privilegios Oracle efectivos y roles en TEST/producción sin alterar objetos.",
    annotations={"readOnlyHint": True},
)
def inspect_oracle_privileges(environment: str = "test") -> dict[str, Any]:
    """Return observed session privileges without inferring grants from configuration."""
    readiness = doctor_report()
    if not readiness["ready"]:
        return readiness
    profile, error = load_profile(environment)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}
    command = sqlcl_result(profile, PRIVILEGE_QUERY)
    result = classify_result(command)
    if not result["ok"]:
        return {**result, "environment": environment}
    groups: dict[str, list[str]] = {"system_privileges": [], "roles": [], "object_privileges": []}
    for line in command.stdout.splitlines():
        cleaned = line.strip()
        if cleaned.startswith("system_privilege="):
            groups["system_privileges"].append(cleaned.removeprefix("system_privilege="))
        elif cleaned.startswith("role="):
            groups["roles"].append(cleaned.removeprefix("role="))
        elif cleaned.startswith("object_privilege="):
            groups["object_privileges"].append(cleaned.removeprefix("object_privilege="))
    return {"ok": True, "code": "SUCCESS", "environment": environment, **groups}


@mcp.tool(
    description="Ejecuta un archivo SQL revisado dentro del repositorio usando el ambiente indicado.",
    annotations={"readOnlyHint": False, "destructiveHint": True},
)
def execute_sql_file(path: str, environment: str = "test") -> dict[str, Any]:
    """Execute any versioned database SQL permitted to the connected account."""
    return execute_artifact(path, environment, "oracle_sql_file")


@mcp.tool(
    description="Importa un export nativo de página APEX desde un archivo SQL del repositorio.",
    annotations={"readOnlyHint": False, "destructiveHint": True},
)
def deploy_apex_page(path: str, environment: str = "test") -> dict[str, Any]:
    """Deploy a native APEX export; the artifact must carry the approved page definition."""
    try:
        source = workspace_sql_file(path)
    except ValueError as exc:
        return {"ok": False, "code": "INVALID_ARTIFACT", "message": str(exc)}
    content = source.read_text(encoding="utf-8").lower()
    required = ("wwv_flow_imp.import_begin", "wwv_flow_imp.import_end")
    if not all(token in content for token in required):
        return {
            "ok": False,
            "code": "INVALID_APEX_EXPORT",
            "message": "El archivo no contiene un export APEX nativo completo.",
        }
    return execute_artifact(path, environment, "apex_native_import")


def main() -> None:
    """Start the local STDIO MCP server."""
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
