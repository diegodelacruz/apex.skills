#!/usr/bin/env python3
"""Oracle capability checks bound to the authenticated Oracle connection."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Protocol


class CapabilityErrorCode(str, Enum):
    """Observed failure classes; never infer authorization from a generic error."""

    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    APEX_CONTEXT_INVALID = "APEX_CONTEXT_INVALID"
    ADAPTER_INCOMPATIBLE = "ADAPTER_INCOMPATIBLE"
    OBJECT_CONFLICT = "OBJECT_CONFLICT"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    EXTERNAL_DEPENDENCY_BLOCKED = "EXTERNAL_DEPENDENCY_BLOCKED"
    CONFIGURATION_REQUIRED = "CONFIGURATION_REQUIRED"


@dataclass(frozen=True)
class CapabilityResult:
    available: bool
    code: CapabilityErrorCode | None
    reason: str
    evidence: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Authorization:
    """Authorization asserted by a trusted identity integration, not a profile."""

    subject: str
    environment: str
    operations: frozenset[str]
    workspace: str | None = None
    application_id: int | None = None
    pages: frozenset[int] = frozenset()
    schema: str | None = None
    objects: frozenset[str] = frozenset()
    evidence_id: str | None = None


class IdentityVerifier(Protocol):
    def __call__(self, assertion: str) -> Authorization: ...


class DbCursor(Protocol):
    def execute(self, statement: str, parameters: Mapping[str, object] | None = None) -> object: ...

    def fetchone(self) -> tuple[object, ...] | None: ...


class DbConnection(Protocol):
    def cursor(self) -> DbCursor: ...

    def commit(self) -> object: ...


def verify_authorization(
    assertion: str | None, verifier: IdentityVerifier | None, environment: str, operation: str
) -> tuple[Authorization | None, CapabilityResult | None]:
    """Verify the real human authorization before even attempting a connection."""
    if not assertion or verifier is None:
        return None, CapabilityResult(
            False,
            CapabilityErrorCode.EXTERNAL_DEPENDENCY_BLOCKED,
            "A trusted human-identity assertion and verifier are required; a technical profile is not authorization.",
        )
    try:
        authorization = verifier(assertion)
    except Exception as exc:  # integration failure is not a privilege finding
        return None, CapabilityResult(False, CapabilityErrorCode.EXTERNAL_DEPENDENCY_BLOCKED, str(exc))
    if authorization.environment != environment or operation not in authorization.operations:
        return None, CapabilityResult(
            False,
            CapabilityErrorCode.AUTHORIZATION_DENIED,
            "The verified authorization does not allow this operation in the requested environment.",
            {"authorization_evidence": authorization.evidence_id or "absent"},
        )
    return authorization, None


def oracle_preflight(
    connection: DbConnection, authorization: Authorization, target_schema: str, target_object: str
) -> CapabilityResult:
    """Observe session identity and target scope using the same Oracle connection."""
    cursor = connection.cursor()
    try:
        cursor.execute(
            "select sys_context('userenv', 'session_user'), sys_context('userenv', 'current_schema') from dual"
        )
        row = cursor.fetchone()
    except Exception as exc:
        return CapabilityResult(False, CapabilityErrorCode.EXECUTION_ERROR, str(exc))
    if not row:
        return CapabilityResult(False, CapabilityErrorCode.EXECUTION_ERROR, "Oracle did not return session identity.")
    session_user, current_schema = (str(value).upper() for value in row)
    if authorization.schema != target_schema.upper() or target_object.upper() not in authorization.objects:
        return CapabilityResult(
            False, CapabilityErrorCode.AUTHORIZATION_DENIED, "Schema or object is outside the verified allowlist."
        )
    if current_schema != target_schema.upper():
        return CapabilityResult(
            False,
            CapabilityErrorCode.APEX_CONTEXT_INVALID,
            "The current Oracle schema differs from the explicitly authorized target schema.",
            {"session_user": session_user, "current_schema": current_schema},
        )
    return CapabilityResult(
        True,
        None,
        "Oracle session and object scope observed.",
        {"session_user": session_user, "current_schema": current_schema},
    )


def validate_ddl(statement: str, target_schema: str, target_object: str) -> CapabilityResult:
    """Validate a narrow table-DDL grammar; it never authorizes execution."""
    normalized = " ".join(statement.upper().split())
    expected = re.escape(f"{target_schema.upper()}.{target_object.upper()}")
    forbidden = r"\b(RENAME| AS SELECT| SELECT | FROM |;|@)\b"
    allowed = (
        rf"CREATE TABLE {expected} \([^;]+\)$",
        rf"ALTER TABLE {expected} ADD \([^;]+\)$",
        rf"DROP TABLE {expected}$",
    )
    if re.search(forbidden, normalized) or not any(re.fullmatch(pattern, normalized) for pattern in allowed):
        return CapabilityResult(
            False,
            CapabilityErrorCode.ADAPTER_INCOMPATIBLE,
            "DDL is outside the strict supported grammar or could affect another object.",
        )
    return CapabilityResult(
        True, None, "DDL is syntactically scoped; execution remains disabled pending real preflight."
    )


def execute_oracle_ddl(
    connection: DbConnection, authorization: Authorization, target_schema: str, target_object: str, statement: str
) -> CapabilityResult:
    """Execute a single DDL statement after preflight and validation pass."""
    preflight_result = oracle_preflight(connection, authorization, target_schema, target_object)
    if not preflight_result.available:
        return preflight_result

    ddl_result = validate_ddl(statement, target_schema, target_object)
    if not ddl_result.available:
        return ddl_result

    cursor = connection.cursor()
    try:
        cursor.execute(statement)
        connection.commit()
    except Exception as exc:
        return CapabilityResult(False, CapabilityErrorCode.EXECUTION_ERROR, str(exc))

    cursor_verify = connection.cursor()
    try:
        cursor_verify.execute(
            "SELECT object_name, object_type, status FROM all_objects " "WHERE owner = :schema AND object_name = :obj",
            {"schema": target_schema.upper(), "obj": target_object.upper()},
        )
        row = cursor_verify.fetchone()
    except Exception:
        row = None

    evidence = dict(preflight_result.evidence)
    if row:
        evidence["object_name"] = str(row[0])
        evidence["object_type"] = str(row[1])
        evidence["status"] = str(row[2])

    return CapabilityResult(True, None, "DDL executed and verified.", evidence)


def apex_import_preflight(
    authorization: Authorization,
    apex_release: str,
    workspace: str,
    application_id: int,
    page_numbers: Iterable[int],
    app_builder_access: bool,
) -> CapabilityResult:
    """Authorize official export/import only; it never writes APEX internal tables."""
    if apex_release != "24.1.3":
        return CapabilityResult(
            False,
            CapabilityErrorCode.ADAPTER_INCOMPATIBLE,
            f"APEX release {apex_release!r} is not the supported 24.1.3 contract.",
        )
    if not app_builder_access or authorization.workspace != workspace:
        return CapabilityResult(
            False,
            CapabilityErrorCode.APEX_CONTEXT_INVALID,
            "Verified App Builder access and matching workspace are required.",
        )
    if authorization.application_id != application_id:
        return CapabilityResult(
            False, CapabilityErrorCode.AUTHORIZATION_DENIED, "Application is outside the verified authorization."
        )
    requested_pages = frozenset(page_numbers)
    if requested_pages and not requested_pages.issubset(authorization.pages):
        return CapabilityResult(
            False, CapabilityErrorCode.AUTHORIZATION_DENIED, "One or more pages are outside the verified authorization."
        )
    return CapabilityResult(
        True,
        None,
        "Use authenticated App Builder or a native APEX export/import artifact; " "no internal APEX tables are used.",
    )


def capability_matrix(
    identity: CapabilityResult,
    apex: CapabilityResult,
    oracle_read: CapabilityResult,
    oracle_write: CapabilityResult,
) -> dict[str, dict[str, str | bool | None]]:
    """Return effective capabilities without converting a missing check into a grant.

    The caller supplies results from the same verified context.  This keeps the
    report intentionally unable to infer access from a profile, workspace ID, or
    static configuration file.
    """
    results = {
        "identity": identity,
        "apex": apex,
        "oracle_read": oracle_read,
        "oracle_create_modify_delete": oracle_write,
    }
    return {
        name: {
            "available": result.available,
            "code": result.code.value if result.code else None,
            "reason": result.reason,
        }
        for name, result in results.items()
    }
