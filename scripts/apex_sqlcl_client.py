#!/usr/bin/env python3
"""Retired SQLcl client kept only as a fail-closed compatibility import."""

from __future__ import annotations

from typing import Any


class ApexSQLclClient:
    """Legacy SQLcl facade; supported operations live in governed workflows.

    Constructor parameters remain accepted for import compatibility. In
    particular, ``db_connection_string`` is never retained, logged, or used.
    """

    def __init__(
        self,
        sqlcl_path: str | None = None,
        db_connection_string: str | None = None,
        apex_instance_url: str | None = None,
        timeout: int = 300,
    ) -> None:
        self.sqlcl_path = sqlcl_path
        self.apex_instance_url = apex_instance_url
        self.timeout = timeout
        self.operations_log: list[str] = []

    @staticmethod
    def _unavailable(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(
            "ADAPTER_INCOMPATIBLE: this compatibility client is retired; "
            "use the repository's supported APEX page automation workflow."
        )

    _execute_sqlcl = _unavailable
    export_application = _unavailable
    import_application = _unavailable
    deploy_to_environment = _unavailable
    sync_between_environments = _unavailable
    validate_app_status = _unavailable

    @staticmethod
    def _find_sqlcl() -> None:
        """The retired client does not locate or launch SQLcl."""
        return None

    @staticmethod
    def get_audit_log() -> list[str]:
        """Return no entries because this client performs no operations."""
        return []

    @staticmethod
    def clear_audit_log() -> None:
        """No-op compatibility method."""

    def _log_operation(self, command: str, status: str, details: str | None = None) -> None:
        """Reject synthetic audit entries for an inactive client."""
        self._unavailable(command, status, details)

    def __repr__(self) -> str:
        return f"ApexSQLclClient(apex={self.apex_instance_url or 'unset'}, retired=True)"
