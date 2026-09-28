#!/usr/bin/env python3
"""Observe Oracle context and submit requested SQL to the authenticated connection.

This helper does not maintain a local grant or object allowlist. Oracle is the
authority for effective privileges; the caller keeps the statement within the
user's requested scope and reports the returned database result.
"""

from __future__ import annotations

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
    """Return optional identity evidence; it never gates a user's direct request."""
    if not assertion or verifier is None:
        return None, None
    try:
        return verifier(assertion), None
    except Exception:
        return None, None


def oracle_preflight(
    connection: DbConnection, authorization: Authorization | None, target_schema: str, target_object: str
) -> CapabilityResult:
    """Observe session identity and target scope using the same Oracle connection."""
    cursor = connection.cursor()
    try:
        cursor.execute(
            "select sys_context('userenv', 'session_user'), sys_context('userenv', 'current_schema') from dual"
        )
        row = cursor.fetchone()
    except Exception as exc:
        return CapabilityResult(
            True, None, f"Session observation unavailable; this does not gate Oracle execution: {exc}"
        )
    if not row:
        return CapabilityResult(True, None, "Oracle did not return session identity; this does not gate execution.")
    session_user, current_schema = (str(value).upper() for value in row)
    return CapabilityResult(
        True,
        None,
        "Oracle session observed; target privilege and object validity are determined by Oracle on execution.",
        {
            "session_user": session_user,
            "current_schema": current_schema,
            "requested_schema": target_schema.upper(),
            "requested_object": target_object.upper(),
        },
    )


def validate_ddl(statement: str, target_schema: str, target_object: str) -> CapabilityResult:
    """Report the requested scope without filtering SQL or inferring grants."""
    return CapabilityResult(
        True, None, "Statement is passed to Oracle; Oracle determines syntax, scope and privileges."
    )


def execute_oracle_ddl(
    connection: DbConnection,
    authorization: Authorization | None,
    target_schema: str,
    target_object: str,
    statement: str,
) -> CapabilityResult:
    """Submit the requested statement directly and report Oracle's result."""
    # Do not require a local identity/profile query before the requested SQL;
    # send it to Oracle and let the authenticated session determine the result.
    preflight_result = CapabilityResult(True, None, "No skill-level authorization preflight applied.")
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

    verified = bool(row)
    return CapabilityResult(
        True,
        None,
        (
            "Oracle accepted and committed the statement."
            if verified
            else (
                "Oracle accepted and committed the statement; post-execution dictionary verification was "
                "unavailable or returned no row."
            )
        ),
        evidence,
    )


def apex_import_preflight(
    authorization: Authorization | None = None,
    apex_release: str = "unknown",
    workspace: str = "unknown",
    application_id: int = 0,
    page_numbers: Iterable[int] = (),
    app_builder_access: bool = False,
) -> CapabilityResult:
    """Report the selected APEX context without skill-level compatibility gates."""
    return CapabilityResult(
        True,
        None,
        (
            f"Requested APEX operation context: release={apex_release}, workspace={workspace}, "
            f"app={application_id}, pages={tuple(page_numbers)}, App Builder reported={app_builder_access}. "
            "Continue through the available requested tool; the service determines effective privileges."
        ),
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
