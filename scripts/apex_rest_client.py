#!/usr/bin/env python3
"""Retired compatibility facade for a non-operational APEX REST adapter."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ApexRestClient:
    """Keep the legacy import path while failing closed on APEX operations.

    The old username/password constructor parameters remain accepted for
    compatibility, but they are deliberately not retained or used.
    """

    def __init__(
        self,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @staticmethod
    def _unavailable(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(
            "ADAPTER_INCOMPATIBLE: this compatibility adapter is retired; "
            "use the supported APEX page automation workflow."
        )

    create_application = _unavailable
    get_application = _unavailable
    update_application = _unavailable
    delete_application = _unavailable
    export_application = _unavailable
    import_application = _unavailable
    deploy_to_environment = _unavailable
    sync_between_environments = _unavailable
    validate_app_status = _unavailable

    @staticmethod
    def _retry_with_backoff(action: Callable[[], Any]) -> Any:
        """Retain the generic helper without enabling adapter operations."""
        return action()

    @staticmethod
    def get_audit_log() -> list[str]:
        """Return no operations because this adapter performs none."""
        return []

    @staticmethod
    def clear_audit_log() -> None:
        """No-op compatibility method; the adapter has no operations to clear."""

    def __repr__(self) -> str:
        return f"ApexRestClient(url={self.base_url}, retired=True)"
