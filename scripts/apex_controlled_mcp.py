#!/usr/bin/env python3
"""Controlled local MCP for Oracle/APEX artifacts executed through SQLcl.

The server is intentionally independent from the managed ``apex-mcp``
upstream. It never exposes APEX internal-table tools or inline write SQL.
Inline reads run in an Oracle read-only transaction; Oracle decides whether
the configured account can access the requested objects.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

if __package__ in (None, ""):
    from change_bundle import (
        ChangeBundleError,
        artifact_hashes,
        baseline_success_marker,
        load_bundle,
        render_execution_sql,
    )
    from env_credentials import parse_env
else:
    from scripts.change_bundle import (
        ChangeBundleError,
        artifact_hashes,
        baseline_success_marker,
        load_bundle,
        render_execution_sql,
    )
    from scripts.env_credentials import parse_env

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


def encode_sqlcl_input(script: str) -> str:
    """Normalize stdin for the Windows SQLcl code page without raising on Unicode."""
    return script.encode("cp1252", errors="replace").decode("cp1252")


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
        # utf-8-sig accepts the UTF-8 BOM written by Windows PowerShell 5.1.
        value = json.loads(path.read_text(encoding="utf-8-sig"))
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


def resolve_environment(environment: str | None) -> tuple[str | None, dict[str, Any] | None]:
    """Resolve an explicit environment or the .env selector, never process env."""
    values = parse_env(ROOT / ".env")
    selected = environment or values.get("DB_ENV")
    if not selected:
        return None, {
            "code": "ENVIRONMENT_REQUIRED",
            "message": "No se indicó ambiente y DB_ENV no está configurado; especifique test o production.",
        }
    normalized = {"test": "test", "testing": "test", "prod": "production", "production": "production"}
    resolved = normalized.get(selected.strip().lower())
    if resolved is None:
        return None, {
            "code": "CONFIGURATION_REQUIRED",
            "message": "Ambiente inválido; use test/testing o production.",
        }
    return resolved, None


def load_profile(environment: str | None) -> tuple[dict[str, str] | None, dict[str, Any] | None]:
    """Load the configured profile for an explicit or DB_ENV-selected environment."""
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return None, environment_error
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return None, {"code": "PROFILE_MISSING", "message": "No existe .env; no se intentó conectar."}
    values = parse_env(env_path)
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


def decode_sqlcl_stream(stream: str | bytes) -> str:
    """Decode SQLcl output without letting malformed bytes hide the process result."""
    if isinstance(stream, bytes):
        return stream.decode("utf-8", errors="replace")
    return stream.encode("cp1252", errors="surrogateescape").decode("utf-8", errors="replace")


def sqlcl_result(
    profile: dict[str, str],
    statements: str,
    working_directory: str | None = None,
    bind_variables: dict[str, int] | None = None,
    read_only_transaction: bool = False,
    continue_on_sql_error: bool = False,
) -> CommandResult:
    """Run SQLcl with credentials over stdin, never command-line arguments."""
    state = runtime_state()
    if state is None:
        return CommandResult(1, "", "RUNTIME_NOT_INSTALLED")
    java_home = state.get("java_home")
    sqlcl_path = state.get("sqlcl_path")
    if not java_home or not sqlcl_path:
        return CommandResult(1, "", "RUNTIME_INTEGRITY_FAILED: runtime state is missing java_home or sqlcl_path")
    environment = os.environ.copy()
    environment["JAVA_HOME"] = str(java_home)
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
            "set encoding utf8",
            "set echo off feedback off heading off pagesize 0 verify off",
            "set define off",
            "whenever sqlerror continue" if continue_on_sql_error else "whenever sqlerror exit sql.sqlcode rollback",
            f"connect {connection}",
            *(("set transaction read only;",) if read_only_transaction else ()),
            *bind_setup,
            statements,
            "exit",
        )
    )
    try:
        process = subprocess.run(
            [str(sqlcl_path), "-S", "/nolog"],
            capture_output=True,
            check=False,
            env=environment,
            input=encode_sqlcl_input(script),
            text=True,
            encoding="cp1252",
            errors="surrogateescape",
            timeout=120,
            cwd=working_directory,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CommandResult(1, "", f"SQLCL_RUNTIME_ERROR: {exc}")
    return CommandResult(
        process.returncode,
        decode_sqlcl_stream(process.stdout),
        decode_sqlcl_stream(process.stderr),
    )


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
    if "RUNTIME_NOT_INSTALLED" in technical:
        code = "RUNTIME_NOT_INSTALLED"
        clear = "El runtime administrado no está instalado; solicite doctor() si necesita revisar su estado."
    elif "RUNTIME_INTEGRITY_FAILED" in technical or "SQLCL_RUNTIME_ERROR" in technical:
        code = "RUNTIME_INTEGRITY_FAILED"
        clear = "SQLcl no pudo arrancar con el runtime configurado; solicite doctor() para revisar el runtime."
    elif match and match.group(1) == "01031":
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


def validate_mutation_decisions(confirmed: bool | None, backup_choice: str | None) -> dict[str, Any] | None:
    """Fail closed unless the caller supplies both explicit mutation decisions."""
    if confirmed is not True:
        return {
            "ok": False,
            "code": "USER_CONFIRMATION_REQUIRED",
            "message": "Falta la confirmación explícita del usuario para ejecutar el cambio.",
        }
    if backup_choice not in {"yes", "no"}:
        return {
            "ok": False,
            "code": "BACKUP_CHOICE_REQUIRED",
            "message": "Indique explícitamente backup_choice='yes' o backup_choice='no'.",
        }
    return None


def apex_export_page_identity(content: str) -> tuple[str, str] | None:
    """Extract application/page identity from a native page export when present."""
    app_match = re.search(r"(?i)\bp_default_application_id\s*=>\s*(\d+)", content)
    create_page = re.search(r"(?i)\.create_page\s*\(", content)
    if not app_match or not create_page:
        return None
    page_match = re.search(r"(?i)\bp_id\s*=>\s*(\d+)", content[create_page.end() :])
    if not page_match:
        return None
    return app_match.group(1), page_match.group(1)


def validate_read_only_query(statement: str) -> str:
    """Accept one single-line SELECT so SQLcl cannot parse injected client commands."""
    query = statement.strip()
    if not query or len(query) > 20000:
        raise ValueError("La consulta está vacía o excede el máximo de 20000 caracteres.")
    if any(ord(char) < 32 or 127 <= ord(char) <= 159 or char in "\u2028\u2029" for char in query):
        raise ValueError("La consulta debe estar en una sola línea y no contener caracteres de control.")
    if not re.match(r"(?is)^select\b", query):
        raise ValueError("La herramienta de consulta solo acepta una sentencia SELECT.")
    if re.search(r"--|/\*|\*/|;", query) or re.search(r"(?m)^\s*/\s*$", query):
        raise ValueError("La consulta debe ser una sola sentencia, sin comentarios ni terminadores SQLcl.")
    if re.search(r"(?i)\bfor\s+update\b", query):
        raise ValueError("La consulta no puede bloquear filas con FOR UPDATE.")
    return query + ";"


def append_audit_entry(entry: dict[str, Any]) -> str | None:
    """Durably append one JSON Lines event, returning an error without hiding it."""
    try:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return None


def begin_mutation_audit(
    environment: str,
    operation: str,
    source: Path,
    metadata: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    """Persist a write-ahead event before a controlled mutation is submitted."""
    entry = {
        **(metadata or {}),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_id": str(uuid.uuid4()),
        "event_phase": "started",
        "environment": environment,
        "operation": operation,
        "source": str(source.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "result": "STARTED",
        "exit_code": None,
    }
    error = append_audit_entry(entry)
    return (entry, None) if error is None else (None, error)


def finish_mutation_audit(
    started_event: dict[str, Any],
    result: dict[str, Any],
    timings_ms: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist the correlated outcome or return an explicit no-retry warning."""
    completed_event = {
        **started_event,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_phase": "completed",
        "result": result.get("code", "UNKNOWN"),
        "exit_code": result.get("exit_code"),
        "timings_ms": timings_ms,
        **(metadata or {}),
    }
    error = append_audit_entry(completed_event)
    if error is not None:
        operation_result = result.get("code", "UNKNOWN")
        return {
            **result,
            "ok": False,
            "code": "AUDIT_COMPLETION_FAILED",
            "operation_result": operation_result,
            "audit_event_id": started_event["event_id"],
            "message": (
                f"La operación terminó con resultado {operation_result}, pero no se pudo guardar su resultado "
                f"en la bitácora ({error}). La acción pudo haberse aplicado; no la reintente automáticamente."
            ),
        }
    return {**result, "audit_event_id": started_event["event_id"], "audit_persisted": True}


def audit_start_failure(error: str) -> dict[str, Any]:
    """Report that a mutation did not start because its write-ahead event failed."""
    return {
        "ok": False,
        "code": "AUDIT_START_FAILED",
        "message": f"No se pudo registrar el inicio en la bitácora; la operación no se ejecutó: {error}",
    }


def execute_mutation_statements(profile: dict[str, str], statements: str) -> dict[str, Any]:
    """Run one SQLcl mutation phase and convert adapter exceptions to explicit outcomes."""
    try:
        return classify_result(sqlcl_result(profile, statements))
    except Exception as exc:
        return {
            "ok": False,
            "code": "ADAPTER_EXECUTION_FAILED",
            "exit_code": None,
            "message": (
                f"El adaptador falló durante la ejecución ({type(exc).__name__}: {exc}); "
                "la acción pudo haberse aplicado y no debe repetirse automáticamente."
            ),
        }


def write_readonly_query_audit(
    environment: str,
    statement: str,
    bind_variables: dict[str, int] | None,
    result: dict[str, Any],
    timings_ms: dict[str, int] | None = None,
) -> None:
    """Record a digest of the query and binds, never their raw contents."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = json.dumps(
        {"query": statement, "binds": bind_variables or {}},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": environment,
        "operation": "oracle_readonly_query",
        "source": "inline_readonly_query",
        "source_sha256": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest(),
        "result": result["code"],
        "exit_code": result["exit_code"],
        "timings_ms": timings_ms or {},
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _batch_output(stdout: str, start_marker: str, end_marker: str) -> str | None:
    """Extract output bounded by exact, request-specific SQLcl prompt markers."""
    active = False
    lines: list[str] = []
    for line in stdout.splitlines():
        if line.strip() == start_marker:
            active = True
            lines = []
        elif line.strip() == end_marker and active:
            return "\n".join(lines).strip()
        elif active:
            lines.append(line)
    return None


def _readonly_batch_audit(
    environment: str,
    queries: list[str],
    bind_variables: dict[str, int] | None,
    results: list[dict[str, Any]],
    timings_ms: dict[str, int],
) -> None:
    """Record per-query digests and outcomes without SQL, binds, or row data."""
    digests = []
    for query in queries:
        fingerprint = json.dumps(
            {"query": query, "binds": bind_variables or {}},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        digests.append(hashlib.sha256(fingerprint.encode("utf-8")).hexdigest())
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "environment": environment,
        "operation": "oracle_readonly_batch",
        "source": "inline_readonly_batch",
        "query_sha256s": digests,
        "results": [
            {"index": result["index"], "code": result["code"], "ora_codes": result["ora_codes"]} for result in results
        ],
        "timings_ms": timings_ms,
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def execute_readonly_batch(
    queries: list[str],
    environment: str | None = None,
    bind_variables: dict[str, int] | None = None,
    include_identity: bool = True,
) -> dict[str, Any]:
    """Run bounded, validated SELECT statements in one read-only SQLcl session."""
    route_started = time.perf_counter()
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return {"ok": False, **environment_error}
    assert environment is not None
    if not isinstance(queries, list) or not queries or len(queries) > 25:
        return {
            "ok": False,
            "code": "BATCH_LIMIT_EXCEEDED",
            "message": "El lote debe contener entre 1 y 25 consultas SELECT.",
        }
    if any(not isinstance(query, str) for query in queries) or sum(map(len, queries)) > 100_000:
        return {
            "ok": False,
            "code": "BATCH_LIMIT_EXCEEDED",
            "message": "El lote excede el tamaño total máximo de 100000 caracteres.",
        }
    if bind_variables is not None and any(
        not re.fullmatch(r"[a-z][a-z0-9_]*", name) or type(value) is not int for name, value in bind_variables.items()
    ):
        return {
            "ok": False,
            "code": "INVALID_BIND_VARIABLE",
            "message": "Los binds deben tener nombres simples en minúsculas y valores enteros.",
        }
    try:
        normalized_queries = [validate_read_only_query(query) for query in queries]
    except ValueError as exc:
        return {"ok": False, "code": "READ_ONLY_QUERY_REQUIRED", "message": str(exc)}

    profile_started = time.perf_counter()
    profile, error = load_profile(environment)
    profile_load_ms = round((time.perf_counter() - profile_started) * 1000)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}

    token = str(uuid.uuid4()).replace("-", "").upper()
    statements: list[str] = []
    identity_start = f"__APEX_BATCH_{token}_IDENTITY_BEGIN__"
    identity_end = f"__APEX_BATCH_{token}_IDENTITY_END__"
    if include_identity:
        statements.extend(
            (
                f"prompt {identity_start}",
                "select sys_context('userenv','session_user') || '|' || "
                "sys_context('userenv','current_schema') || '|' || sys_context('userenv','service_name') from dual;",
                f"prompt {identity_end}",
            )
        )
    markers: list[tuple[str, str]] = []
    for index, query in enumerate(normalized_queries):
        start_marker = f"__APEX_BATCH_{token}_QUERY_{index}_BEGIN__"
        end_marker = f"__APEX_BATCH_{token}_QUERY_{index}_END__"
        markers.append((start_marker, end_marker))
        statements.extend((f"prompt {start_marker}", query, f"prompt {end_marker}"))

    sqlcl_started = time.perf_counter()
    command = sqlcl_result(
        profile,
        "\n".join(statements),
        bind_variables=bind_variables,
        read_only_transaction=True,
        continue_on_sql_error=True,
    )
    sqlcl_process_ms = round((time.perf_counter() - sqlcl_started) * 1000)
    process_result = classify_result(CommandResult(command.exit_code, command.stderr, ""))
    first_marker = identity_start if include_identity else markers[0][0]
    marker_position = command.stdout.find(first_marker)
    pre_marker_output = command.stdout if marker_position < 0 else command.stdout[:marker_position]
    pre_marker_output = "\n".join((pre_marker_output, command.stderr))
    pre_marker_ora = {code for code, _ in ORA_PATTERN.findall(pre_marker_output)}
    connection_failed = bool(pre_marker_ora)
    results: list[dict[str, Any]] = []
    for index, (start_marker, end_marker) in enumerate(markers):
        output = _batch_output(command.stdout, start_marker, end_marker)
        text = output or ""
        ora_codes = sorted({f"ORA-{code}" for code, _ in ORA_PATTERN.findall(text)})
        sqlcl_errors = re.findall(r"\bSP2-\d{4}\b", text, re.IGNORECASE)
        results.append(
            {
                "index": index,
                "code": (
                    "CONNECTION_FAILED"
                    if connection_failed
                    else (
                        process_result["code"]
                        if not process_result["ok"]
                        else (
                            "OUTPUT_INCOMPLETE"
                            if output is None
                            else ("ORACLE_ERROR" if ora_codes else "SQLCL_ERROR" if sqlcl_errors else "SUCCESS")
                        )
                    )
                ),
                "output": text,
                "ora_codes": ora_codes,
            }
        )
    identity: dict[str, str] | None = None
    if include_identity:
        identity_text = _batch_output(command.stdout, identity_start, identity_end)
        if identity_text:
            values = identity_text.splitlines()[0].split("|", 2)
            if len(values) == 3:
                identity = {"session_user": values[0], "current_schema": values[1], "service": values[2]}

    timings_ms = {
        "profile_load": profile_load_ms,
        "sqlcl_process": sqlcl_process_ms,
        "route_total": round((time.perf_counter() - route_started) * 1000),
        "query_count": len(normalized_queries),
    }
    audit_persisted = True
    try:
        _readonly_batch_audit(environment, normalized_queries, bind_variables, results, timings_ms)
    except OSError:
        audit_persisted = False
    has_query_error = any(result["code"] != "SUCCESS" for result in results)
    top_ok = (
        not connection_failed
        and process_result["ok"]
        and not has_query_error
        and (not include_identity or identity is not None)
    )
    return {
        "ok": top_ok,
        "code": (
            "CONNECTION_FAILED"
            if connection_failed
            else (
                "SUCCESS" if top_ok else process_result["code"] if not process_result["ok"] else "BATCH_PARTIAL_FAILURE"
            )
        ),
        "message": (
            "Todas las consultas terminaron correctamente."
            if top_ok
            else (
                "No se pudo establecer la conexión Oracle para el lote."
                if connection_failed
                else (
                    f"El proceso SQLcl falló con {process_result['code']}: {process_result['message']}"
                    if not process_result["ok"]
                    else "Una o más consultas o la identidad fallaron."
                )
            )
        ),
        "environment": environment,
        "source": "inline_readonly_batch",
        "identity": identity,
        "results": results,
        "timings_ms": timings_ms,
        "audit_persisted": audit_persisted,
        **({"warning": "No se pudo persistir la bitácora del lote."} if not audit_persisted else {}),
    }


def change_phase_durations(output: str) -> dict[str, int]:
    """Extract DBMS_UTILITY timer values emitted by a rendered bundle."""
    values: dict[str, int] = {}
    for phase, marker, value in re.findall(r"__CHANGE_TIMER_(\w+)_(START|END)=(-?\d+)", output):
        values[f"{phase}_{marker.lower()}"] = int(value)
    durations: dict[str, int] = {}
    for phase in ("preflight", "snapshot", "apply", "verify"):
        start = values.get(f"{phase}_start")
        end = values.get(f"{phase}_end")
        if start is not None and end is not None:
            durations[phase] = max(0, (end - start) * 10)
    return durations


def execute_artifact(
    relative_path: str,
    environment: str | None,
    operation: str,
    decision_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute one reviewed SQL artifact using the profile for an explicit environment."""
    route_started = time.perf_counter()
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return {"ok": False, **environment_error}
    assert environment is not None
    try:
        source = workspace_sql_file(relative_path)
    except ValueError as exc:
        return {"ok": False, "code": "INVALID_ARTIFACT", "message": str(exc)}
    profile_started = time.perf_counter()
    profile, error = load_profile(environment)
    profile_load_ms = round((time.perf_counter() - profile_started) * 1000)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}
    audit_start, audit_error = begin_mutation_audit(environment, operation, source, decision_metadata)
    if audit_error is not None or audit_start is None:
        return audit_start_failure(audit_error or "No se obtuvo el evento inicial.")
    sqlcl_started = time.perf_counter()
    result = execute_mutation_statements(profile, source.read_text(encoding="utf-8"))
    sqlcl_process_ms = round((time.perf_counter() - sqlcl_started) * 1000)
    timings_ms = {
        "profile_load": profile_load_ms,
        "sqlcl_process": sqlcl_process_ms,
        "route_total": round((time.perf_counter() - route_started) * 1000),
    }
    result = finish_mutation_audit(audit_start, result, timings_ms)
    return {
        **result,
        "environment": environment,
        "source": str(source.relative_to(ROOT)),
        "timings_ms": timings_ms,
    }


def execute_change_bundle_artifact(
    relative_path: str,
    environment: str | None,
    confirmed: bool | None,
    backup_choice: str | None,
) -> dict[str, Any]:
    """Run preflight, then apply/verify only after its baseline proof is observed."""
    decision_error = validate_mutation_decisions(confirmed, backup_choice)
    if decision_error is not None:
        return decision_error
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return {"ok": False, **environment_error}
    assert environment is not None
    try:
        manifest = (ROOT / relative_path).resolve()
        manifest.relative_to(ROOT)
        if manifest.suffix.lower() != ".json" or not manifest.is_file():
            raise ChangeBundleError("change.json debe existir dentro del checkout.")
        bundle = load_bundle(manifest, ROOT)
        if backup_choice == "no" and "snapshot" in bundle["artifacts"]:
            return {
                "ok": False,
                "code": "UNEXPECTED_BACKUP_ARTIFACT",
                "message": "El usuario rechazó el backup; quite snapshot del manifiesto. No se ejecutó el cambio.",
            }
        if backup_choice == "yes" and "snapshot" not in bundle["_resolved_artifacts"]:
            return {
                "ok": False,
                "code": "BACKUP_ARTIFACT_REQUIRED",
                "message": "El usuario aceptó backup, pero el bundle no declara snapshot.sql; no se ejecutó el cambio.",
            }
        preflight_statements = render_execution_sql(bundle, ("preflight",))
        snapshot_statements = render_execution_sql(bundle, ("snapshot",)) if backup_choice == "yes" else None
        apply_verify_statements = render_execution_sql(bundle, ("apply", "verify"))
    except (ValueError, ChangeBundleError) as exc:
        return {"ok": False, "code": "INVALID_CHANGE_BUNDLE", "message": str(exc)}
    profile, error = load_profile(environment)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}
    started = time.perf_counter()
    bundle_audit_metadata = {
        "bundle_id": bundle["id"],
        "kind": bundle["kind"],
        "target": bundle["target"],
        "baseline_fingerprint": bundle["baseline"]["fingerprint"],
        "artifact_sha256": artifact_hashes(bundle, ROOT),
        "backup_choice": backup_choice,
    }
    audit_start, audit_error = begin_mutation_audit(
        environment,
        "oracle_apex_change_bundle",
        manifest,
        bundle_audit_metadata,
    )
    if audit_error is not None or audit_start is None:
        return audit_start_failure(audit_error or "No se obtuvo el evento inicial.")
    preflight_result = execute_mutation_statements(profile, preflight_statements)
    expected_marker = baseline_success_marker(bundle)
    if not preflight_result["ok"] or expected_marker not in preflight_result.get("output", ""):
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        result = {
            **preflight_result,
            "ok": False,
            "backup_choice": backup_choice,
            "backup_result": "NOT_RUN",
            "code": "BASELINE_MISMATCH" if preflight_result["ok"] else preflight_result["code"],
            "message": (
                "El preflight no confirmó la fingerprint diagnosticada; apply no fue ejecutado."
                if preflight_result["ok"]
                else preflight_result["message"]
            ),
        }
        result = finish_mutation_audit(
            audit_start,
            result,
            {"elapsed_ms": elapsed_ms, "phase_durations_ms": change_phase_durations(result.get("output", ""))},
            {"backup_choice": backup_choice, "backup_result": "NOT_RUN"},
        )
        return {
            **result,
            "environment": environment,
            "source": str(manifest.relative_to(ROOT)),
            "bundle_id": bundle["id"],
            "elapsed_ms": elapsed_ms,
            "phase_durations_ms": change_phase_durations(result.get("output", "")),
            "backup_choice": backup_choice,
        }
    backup_result = None
    if snapshot_statements is not None:
        backup_result = execute_mutation_statements(profile, snapshot_statements)
        if not backup_result["ok"]:
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            failed = {
                **backup_result,
                "ok": False,
                "code": "BACKUP_FAILED",
                "message": "El snapshot falló; apply no fue ejecutado.",
                "backup_choice": backup_choice,
                "backup_result": backup_result["code"],
            }
            failed = finish_mutation_audit(
                audit_start,
                failed,
                {"elapsed_ms": elapsed_ms, "phase_durations_ms": change_phase_durations(failed.get("output", ""))},
                {"backup_choice": backup_choice, "backup_result": backup_result["code"]},
            )
            return {
                **failed,
                "environment": environment,
                "source": str(manifest.relative_to(ROOT)),
                "bundle_id": bundle["id"],
                "elapsed_ms": elapsed_ms,
                "phase_durations_ms": change_phase_durations(failed.get("output", "")),
            }
    result = execute_mutation_statements(profile, apply_verify_statements)
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    result["backup_choice"] = backup_choice
    result["backup_result"] = backup_result["code"] if backup_result else "NOT_REQUESTED"
    result = finish_mutation_audit(
        audit_start,
        result,
        {"elapsed_ms": elapsed_ms, "phase_durations_ms": change_phase_durations(result.get("output", ""))},
        {"backup_choice": backup_choice, "backup_result": result["backup_result"]},
    )
    return {
        **result,
        "environment": environment,
        "source": str(manifest.relative_to(ROOT)),
        "bundle_id": bundle["id"],
        "elapsed_ms": elapsed_ms,
        "phase_durations_ms": change_phase_durations(result.get("output", "")),
        "backup_choice": backup_choice,
        "backup_result": result["backup_result"],
    }


mcp = FastMCP(
    "apex-controlled-mcp",
    instructions=(
        "The user's request defines the operation, scope, and environment. Select that environment's configured "
        "credential; effective Oracle/APEX privileges granted to that credential determine which operations succeed. "
        "Treat review/show-data/specification requests as read-only: make one minimal destination check only when "
        "needed, then query immediately. Use execute_readonly_batch for a related page review so identity and "
        "validated SELECT statements share one read-only SQLcl session. Do not run routine inventories, privilege "
        "scans, workspace checks, QA, or "
        "preliminary row counts. Before a mutation, the agent asks once to confirm the exact environment/object/action "
        "and whether the user wants a backup; do not create a backup when declined. Use execute_readonly_query for "
        "one SELECT when a batch is unnecessary; it starts an Oracle read-only "
        "transaction and records only a hash. Use execute_sql_file for a confirmed one-off DML/DDL/PLSQL operation. "
        "Use execute_change_bundle only when a fingerprint preflight or coordinated object change materially needs it. "
        "Do not hardcode a user or environment permission matrix. "
        "Report observed errors accurately."
    ),
)


mcp.tool(
    description=(
        "Ejecuta hasta 25 consultas SELECT de una línea en una sola sesión SQLcl y una transacción Oracle "
        "de solo lectura. Rechaza el lote completo antes de conectar si alguna consulta es inválida o si el "
        "tamaño total supera 100000 caracteres. Admite binds enteros compartidos e incluye identidad por defecto. "
        "Los errores Oracle se informan por consulta y no cancelan las siguientes."
    ),
    annotations={"readOnlyHint": True},
)(execute_readonly_batch)


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
def inspect_oracle_session(environment: str | None = None) -> dict[str, Any]:
    """Connect read-only and return the observed Oracle identity."""
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return {"ok": False, **environment_error}
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
def inspect_environment(environment: str | None = None) -> dict[str, Any]:
    """Return dynamic environment readiness; it informs but never blocks later operations."""
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return {"ok": False, **environment_error}
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
def inspect_apex_context(application_id: int, environment: str | None = None) -> dict[str, Any]:
    """Verify the Oracle session, APEX application, workspace and parsing-schema mapping."""
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return {"ok": False, **environment_error}
    if not isinstance(application_id, int) or application_id <= 0:
        return {"ok": False, "code": "INVALID_APPLICATION", "message": "application_id debe ser un entero positivo."}
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
    context: dict[str, Any] = {
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
    session_schema_associated = session_user.upper() in {schema.upper() for schema in schemas}
    context["session_schema_associated"] = session_schema_associated
    message = (
        "La cuenta SQLcl pertenece a un esquema del workspace."
        if session_schema_associated
        else (
            "La cuenta SQLcl no es un esquema del workspace; la asociación es informativa y no bloquea "
            "consultas de metadata."
        )
    )
    return {"ok": True, "code": "SUCCESS", "message": message, **context}


@mcp.tool(
    description="Prueba mediante una exportación temporal de solo lectura si SQLcl puede operar una aplicación APEX.",
    annotations={"readOnlyHint": True},
)
def probe_native_apex_context(application_id: int, environment: str | None = None) -> dict[str, Any]:
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
def inspect_oracle_privileges(environment: str | None = None) -> dict[str, Any]:
    """Return observed session privileges without inferring grants from configuration."""
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return {"ok": False, **environment_error}
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
    description=(
        "Ejecuta un archivo SQL del repositorio. Requiere confirmed=true y backup_choice='yes' o 'no'. "
        "Si backup_choice='yes', backup_sql_path es obligatorio y se ejecuta antes del cambio; si falla, el cambio "
        "se detiene. La elección declarada es una señal del cliente, no una prueba criptográfica de identidad humana."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": True},
)
def execute_sql_file(
    path: str,
    confirmed: bool | None = None,
    backup_choice: str | None = None,
    backup_sql_path: str | None = None,
    environment: str | None = None,
) -> dict[str, Any]:
    """Execute a SQL artifact directly using the connected account's effective privileges."""
    decision_error = validate_mutation_decisions(confirmed, backup_choice)
    if decision_error is not None:
        return decision_error
    if backup_choice == "yes":
        if not backup_sql_path:
            return {
                "ok": False,
                "code": "BACKUP_ARTIFACT_REQUIRED",
                "message": "El usuario aceptó backup; indique backup_sql_path. No se ejecutó el cambio.",
            }
        try:
            backup_source = workspace_sql_file(backup_sql_path)
            change_source = workspace_sql_file(path)
        except ValueError as exc:
            return {"ok": False, "code": "INVALID_ARTIFACT", "message": str(exc)}
        if backup_source == change_source:
            return {
                "ok": False,
                "code": "INVALID_BACKUP_ARTIFACT",
                "message": "El archivo de backup debe ser distinto del archivo del cambio.",
            }
        decision_metadata = {"confirmed": True, "backup_choice": "yes"}
        backup_result = execute_artifact(backup_sql_path, environment, "oracle_sql_backup", decision_metadata)
        if not backup_result["ok"]:
            return {
                **backup_result,
                "ok": False,
                "code": "BACKUP_FAILED",
                "message": "El SQL de backup falló; el cambio no fue ejecutado.",
                "backup_result": backup_result["code"],
            }
    else:
        if backup_sql_path is not None:
            return {
                "ok": False,
                "code": "UNEXPECTED_BACKUP_ARTIFACT",
                "message": "No proporcione backup_sql_path cuando backup_choice='no'.",
            }
        backup_result = None
        decision_metadata = {"confirmed": True, "backup_choice": "no"}
    result = execute_artifact(path, environment, "oracle_sql_file", decision_metadata)
    result["backup_choice"] = backup_choice
    result["backup_result"] = backup_result["code"] if backup_result else "NOT_REQUESTED"
    if backup_result is not None:
        result["backup_source"] = backup_sql_path
    return result


@mcp.tool(
    description=(
        "Requiere confirmed=true y backup_choice='yes' o 'no'. Valida change.json y preflight. Si se acepta backup, "
        "exige y ejecuta snapshot.sql antes de apply; si falla, no aplica el cambio. "
        "Registra huellas y tiempos sin secretos."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": True},
)
def execute_change_bundle(
    path: str,
    confirmed: bool | None = None,
    backup_choice: str | None = None,
    environment: str | None = None,
) -> dict[str, Any]:
    """Execute a prepared, bounded live-change bundle."""
    return execute_change_bundle_artifact(path, environment, confirmed, backup_choice)


@mcp.tool(
    description=(
        "Ejecuta una sola consulta SELECT en una línea física y en una transacción Oracle de solo lectura; "
        "admite binds enteros y no requiere un archivo SQL del repositorio. Úsala para "
        "consultas de metadata conocidas; no es un sandbox para funciones definidas por usuarios."
    ),
)
def execute_readonly_query(
    query: str,
    environment: str | None = None,
    bind_variables: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Run one single-line SELECT through SQLcl without requiring a file artifact."""
    route_started = time.perf_counter()
    environment, environment_error = resolve_environment(environment)
    if environment_error is not None:
        return {"ok": False, **environment_error}
    assert environment is not None
    try:
        normalized_query = validate_read_only_query(query)
    except ValueError as exc:
        return {"ok": False, "code": "READ_ONLY_QUERY_REQUIRED", "message": str(exc)}
    if bind_variables is not None and any(
        not re.fullmatch(r"[a-z][a-z0-9_]*", name) or type(value) is not int for name, value in bind_variables.items()
    ):
        return {
            "ok": False,
            "code": "INVALID_BIND_VARIABLE",
            "message": "Los binds deben tener nombres simples en minúsculas y valores enteros.",
        }
    profile_started = time.perf_counter()
    profile, error = load_profile(environment)
    profile_load_ms = round((time.perf_counter() - profile_started) * 1000)
    if error is not None:
        return {"ok": False, **error}
    if profile is None:
        return {"ok": False, "code": "PROFILE_MISSING", "message": "No se encontró un perfil utilizable."}
    sqlcl_started = time.perf_counter()
    command = sqlcl_result(
        profile,
        normalized_query,
        bind_variables=bind_variables,
        read_only_transaction=True,
    )
    sqlcl_process_ms = round((time.perf_counter() - sqlcl_started) * 1000)
    result = classify_result(command)
    timings_ms = {
        "profile_load": profile_load_ms,
        "sqlcl_process": sqlcl_process_ms,
        "route_total": round((time.perf_counter() - route_started) * 1000),
    }
    write_readonly_query_audit(environment, query, bind_variables, result, timings_ms)
    return {
        **result,
        "environment": environment,
        "source": "inline_readonly_query",
        "timings_ms": timings_ms,
    }


@mcp.tool(
    description=(
        "Importa un export nativo APEX. Requiere confirmed=true y backup_choice='yes' o 'no'. "
        "Si se acepta backup, requiere backup_path con un export previo de la página; el adaptador valida el archivo "
        "pero no puede comprobar que corresponda al estado vivo exacto."
    ),
    annotations={"readOnlyHint": False, "destructiveHint": True},
)
def deploy_apex_page(
    path: str,
    confirmed: bool | None = None,
    backup_choice: str | None = None,
    backup_path: str | None = None,
    environment: str | None = None,
) -> dict[str, Any]:
    """Submit a native APEX export using the selected Oracle profile's privileges."""
    decision_error = validate_mutation_decisions(confirmed, backup_choice)
    if decision_error is not None:
        return decision_error
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
    if backup_choice == "yes":
        if not backup_path:
            return {
                "ok": False,
                "code": "BACKUP_ARTIFACT_REQUIRED",
                "message": (
                    "El usuario aceptó backup; indique el export previo en backup_path. " "No se ejecutó el cambio."
                ),
            }
        try:
            backup_source = workspace_sql_file(backup_path)
        except ValueError as exc:
            return {"ok": False, "code": "INVALID_BACKUP_ARTIFACT", "message": str(exc)}
        backup_content = backup_source.read_text(encoding="utf-8").lower()
        if not all(token in backup_content for token in required):
            return {
                "ok": False,
                "code": "INVALID_BACKUP_ARTIFACT",
                "message": "backup_path no contiene un export APEX nativo reconocible.",
            }
        deployment_identity = apex_export_page_identity(content)
        backup_identity = apex_export_page_identity(backup_content)
        if deployment_identity is None or backup_identity != deployment_identity:
            return {
                "ok": False,
                "code": "BACKUP_SCOPE_MISMATCH",
                "message": (
                    "No se pudo verificar que backup_path y el export a desplegar correspondan "
                    "a la misma aplicación y página."
                ),
            }
        if backup_source == source:
            return {
                "ok": False,
                "code": "INVALID_BACKUP_ARTIFACT",
                "message": "El export de backup debe ser distinto del export a desplegar.",
            }
        decision_metadata = {
            "confirmed": True,
            "backup_choice": "yes",
            "backup_source": str(backup_source.relative_to(ROOT)),
            "backup_source_sha256": hashlib.sha256(backup_source.read_bytes()).hexdigest(),
        }
    else:
        if backup_path is not None:
            return {
                "ok": False,
                "code": "UNEXPECTED_BACKUP_ARTIFACT",
                "message": "No proporcione backup_path cuando backup_choice='no'.",
            }
        decision_metadata = {"confirmed": True, "backup_choice": "no"}
    return execute_artifact(path, environment, "apex_native_import", decision_metadata)


def main() -> None:
    """Start the local STDIO MCP server."""
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
