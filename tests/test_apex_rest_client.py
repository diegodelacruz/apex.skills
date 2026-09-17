"""Tests proving that the former simulated APEX REST client fails closed."""

import pytest

from scripts.apex_rest_client import ApexRestClient


@pytest.mark.unit
def test_legacy_client_preserves_non_secret_configuration():
    client = ApexRestClient("https://apex.example.com/", "admin", "password")
    assert client.base_url == "https://apex.example.com"
    assert client.timeout == 30


@pytest.mark.unit
@pytest.mark.parametrize(
    "operation,args",
    [
        ("create_application", ({"name": "Test"},)),
        ("get_application", ("100",)),
        ("update_application", ("100", {"name": "Test"})),
        ("delete_application", ("100",)),
        ("export_application", ("100",)),
        ("import_application", (b"PK\\x03\\x04",)),
        ("deploy_to_environment", ("100", "test")),
        ("sync_between_environments", ("100", "development", "test")),
        ("validate_app_status", ("100",)),
    ],
)
def test_legacy_operations_are_explicitly_non_operational(operation, args):
    client = ApexRestClient("https://apex.example.com", "admin", "password")
    with pytest.raises(RuntimeError, match="ADAPTER_INCOMPATIBLE"):
        getattr(client, operation)(*args)
    assert client.get_audit_log() == []


@pytest.mark.unit
def test_retry_helper_remains_generic_and_does_not_authorize_operations():
    client = ApexRestClient("https://apex.example.com", "admin", "password")
    assert client._retry_with_backoff(lambda: "ok") == "ok"
