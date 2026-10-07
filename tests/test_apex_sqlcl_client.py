"""Regression tests for the retired SQLcl compatibility client."""

import pytest

from scripts.apex_sqlcl_client import ApexSQLclClient


@pytest.mark.unit
def test_legacy_constructor_does_not_retain_connection_string():
    client = ApexSQLclClient(
        db_connection_string="testuser/test_password@testdb",
        apex_instance_url="https://apex.example.com",
        timeout=30,
    )

    assert client.apex_instance_url == "https://apex.example.com"
    assert client.timeout == 30
    assert not hasattr(client, "db_connection_string")
    assert client.get_audit_log() == []


@pytest.mark.unit
@pytest.mark.parametrize(
    "operation,args",
    [
        ("_execute_sqlcl", ("select 1 from dual",)),
        ("export_application", (100, "app.zip")),
        ("import_application", ("app.zip",)),
        ("deploy_to_environment", (100, "test")),
        ("sync_between_environments", (100, "test", "production")),
        ("validate_app_status", (100,)),
    ],
)
def test_legacy_operations_fail_closed(operation, args):
    client = ApexSQLclClient()

    with pytest.raises(RuntimeError, match="ADAPTER_INCOMPATIBLE"):
        getattr(client, operation)(*args)

    assert client.get_audit_log() == []


@pytest.mark.unit
def test_legacy_audit_api_cannot_record_operations():
    client = ApexSQLclClient()

    with pytest.raises(RuntimeError, match="ADAPTER_INCOMPATIBLE"):
        client._log_operation("deploy", "SUCCESS")

    client.clear_audit_log()
    assert client.get_audit_log() == []
