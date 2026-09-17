#!/usr/bin/env python3
"""Official APEX App Builder integration boundary.

App Builder uses a distinct authenticated APEX account.  This adapter never
falls back to the Oracle profile or fabricates a browser session.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scripts.manage_apex_credentials import APEX_REQUIRED_FIELDS, get_apex_profile


@dataclass(frozen=True)
class ApexOperationResult:
    available: bool
    code: str | None
    reason: str
    environment: str


def preflight(keyring: Any, environment: str) -> ApexOperationResult:
    """Check secure App Builder profile readiness without exposing values."""
    profile = get_apex_profile(keyring, environment)
    if not profile or any(not profile.get(field) for field in APEX_REQUIRED_FIELDS):
        return ApexOperationResult(
            False,
            "CONFIGURATION_REQUIRED",
            "Configure the separate APEX App Builder profile with set-apex; Oracle credentials are not used.",
            environment,
        )
    return ApexOperationResult(
        False,
        "CONFIGURATION_REQUIRED",
        "Configure an authenticated App Builder browser runner before page operations; "
        "no browser session is available.",
        environment,
    )
