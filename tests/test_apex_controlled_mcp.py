"""Tests for the controlled local SQLcl MCP without Oracle connectivity."""

import json
from pathlib import Path

import scripts.apex_controlled_mcp as mcp


def test_doctor_reports_missing_runtime(monkeypatch, tmp_path):
    monkeypatch.setenv(mcp.RUNTIME_ENV, str(tmp_path))

    result = mcp.doctor_report()

    assert result["ready"] is False
    assert result["code"] == "RUNTIME_NOT_INSTALLED"


def test_doctor_reports_registered_missing_binary(monkeypatch, tmp_path):
    state = {"java_home": str(tmp_path / "java"), "sqlcl_path": str(tmp_path / "sql.exe")}
    (tmp_path / "runtime-state.json").write_text(json.dumps(state), encoding="utf-8")
    monkeypatch.setenv(mcp.RUNTIME_ENV, str(tmp_path))

    result = mcp.doctor_report()

    assert result["code"] == "RUNTIME_INTEGRITY_FAILED"


def test_profile_missing_does_not_expose_or_connect(monkeypatch, tmp_path):
    monkeypatch.setattr(mcp, "ROOT", Path(tmp_path))

    profile, error = mcp.load_profile("test")

    assert profile is None
    assert error is not None
    assert error["code"] == "PROFILE_MISSING"


def test_classify_permission_denied_is_clear():
    result = mcp.classify_result(mcp.CommandResult(1031, "ORA-01031: insufficient privileges", ""))

    assert result["ok"] is False
    assert result["code"] == "AUTHORIZATION_DENIED"
    assert "privilegio" in result["message"]
    assert result["technical"].startswith("ORA-01031")


def test_classify_apex_security_group_as_context_error():
    result = mcp.classify_result(mcp.CommandResult(20987, "ORA-20987: APEX - Security Group ID is invalid", ""))

    assert result["code"] == "APEX_CONTEXT_INVALID"
    assert "SQLcl" in result["message"]


def test_workspace_sql_file_rejects_escape(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    outside = tmp_path.parent / "outside.sql"
    outside.write_text("select 1 from dual;", encoding="utf-8")

    try:
        mcp.workspace_sql_file("../outside.sql")
    except ValueError as exc:
        assert "repositorio" in str(exc)
    else:
        raise AssertionError("Expected a path escape to be rejected")


def test_validate_read_only_query_rejects_mutations_and_multiple_statements():
    assert mcp.validate_read_only_query("SELECT page_id FROM apex_application_pages") == (
        "SELECT page_id FROM apex_application_pages;"
    )
    for query in (
        "CREATE TABLE data.t (id NUMBER)",
        "SELECT 1 FROM dual; DELETE FROM data.t",
        "SELECT 1 FROM dual -- comment",
        "SELECT * FROM data.t FOR UPDATE",
        "SELECT 1 FROM dual\nHOST whoami",
        "SELECT 1 FROM dual\r! whoami",
    ):
        try:
            mcp.validate_read_only_query(query)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected read-only validation to reject: {query}")


def test_execute_readonly_query_bypasses_context_helper_and_audits_hash(monkeypatch, tmp_path):
    captured = {}
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "configured"}, None))

    def reject_context_helper(*args, **kwargs):
        raise AssertionError("direct public metadata query must not depend on APEX context helper")

    def fake_sqlcl(profile, statements, **kwargs):
        captured.update(kwargs)
        captured["statements"] = statements
        return mcp.CommandResult(0, "130|100|Página de prueba", "")

    monkeypatch.setattr(mcp, "inspect_apex_context", reject_context_helper)
    monkeypatch.setattr(mcp, "sqlcl_result", fake_sqlcl)

    query = (
        "SELECT application_id, page_id, page_name FROM apex_application_pages "
        "WHERE application_id = :app AND page_id = :page"
    )
    result = mcp.execute_readonly_query(
        query,
        "production",
        {"app": 130, "page": 100},
    )

    assert result["ok"] is True
    assert captured["read_only_transaction"] is True
    assert captured["bind_variables"] == {"app": 130, "page": 100}
    audit = json.loads((tmp_path / "audit.jsonl").read_text(encoding="utf-8"))
    assert audit["source"] == "inline_readonly_query"
    assert audit["source_sha256"]
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert '"app":' not in audit_text
    assert '"page":' not in audit_text
    assert query not in audit_text

    second_audit = tmp_path / "second-audit.jsonl"
    monkeypatch.setattr(mcp, "AUDIT_PATH", second_audit)
    mcp.write_readonly_query_audit(
        "production",
        query,
        {"app": 130, "page": 101},
        {"code": "SUCCESS", "exit_code": 0},
    )
    assert json.loads(second_audit.read_text(encoding="utf-8"))["source_sha256"] != audit["source_sha256"]


def test_sqlcl_read_only_transaction_starts_after_connect(monkeypatch):
    captured = {}
    monkeypatch.setattr(mcp, "runtime_state", lambda: {"java_home": "java", "sqlcl_path": "sql"})

    def fake_run(args, **kwargs):
        captured["script"] = kwargs["input"]
        return type("Process", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(mcp.subprocess, "run", fake_run)
    mcp.sqlcl_result(
        {
            "user": "user",
            "password": "unit_test_value",  # pragma: allowlist secret
            "host": "db",
            "port": "1521",
            "service": "prod",
        },
        "select 1 from dual;",
        read_only_transaction=True,
    )
    script = captured["script"]
    assert script.index("connect user/") < script.index("set transaction read only")
    assert script.index("set transaction read only") < script.index("select 1 from dual")


def test_execute_artifact_preserves_oracle_authority(monkeypatch, tmp_path):
    artifact = tmp_path / "change.sql"
    artifact.write_text("create table data.tmp_test (id number);", encoding="utf-8")
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(mcp, "sqlcl_result", lambda profile, statements: mcp.CommandResult(0, "", ""))

    result = mcp.execute_artifact("change.sql", "test", "oracle_sql_file")

    assert result["ok"] is True
    assert result["code"] == "SUCCESS"
    audit = json.loads((tmp_path / "audit.jsonl").read_text(encoding="utf-8"))
    assert audit["source"] == "change.sql"
    assert "tmp_test" not in (tmp_path / "audit.jsonl").read_text(encoding="utf-8")


def test_inspect_privileges_returns_observed_groups(monkeypatch):
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(
        mcp,
        "sqlcl_result",
        lambda profile, statements, **kwargs: mcp.CommandResult(
            0,
            "system_privilege=CREATE ANY TABLE\nrole=RESOURCE\nobject_privilege=DATA.T_TEST:SELECT\n",
            "",
        ),
    )

    result = mcp.inspect_oracle_privileges("test")

    assert result["system_privileges"] == ["CREATE ANY TABLE"]
    assert result["roles"] == ["RESOURCE"]
    assert result["object_privileges"] == ["DATA.T_TEST:SELECT"]


def test_inspect_apex_context_reports_session_schema_mismatch_without_blocking(monkeypatch):
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(
        mcp,
        "sqlcl_result",
        lambda profile, statements, **kwargs: mcp.CommandResult(
            0,
            "session_user=DDELACRUZ|database_name=ZAITEST|container_name=ZAITESTPDB\n"
            "application=109|workspace=DE|owner=DATA\n"
            "workspace_schema=DATA\nworkspace_schema=DP\nanchor_page=1\n",
            "",
        ),
    )

    result = mcp.inspect_apex_context(109, "test")

    assert result["ok"] is True
    assert result["code"] == "SUCCESS"
    assert result["session_schema_associated"] is False
    assert result["parsing_schema"] == "DATA"
    assert result["session_user"] == "DDELACRUZ"
    assert result["database_name"] == "ZAITEST"
    assert result["container_name"] == "ZAITESTPDB"


def test_apex_context_query_uses_application_bind_variable():
    query = mcp._apex_context_query()

    assert "application_id = :application_id" in query
    assert "{application_id}" not in query


def test_sqlcl_result_binds_integer_values_without_inline_query_interpolation(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        mcp,
        "runtime_state",
        lambda: {"java_home": "java", "sqlcl_path": "sql"},
    )

    def fake_run(args, **kwargs):
        captured["script"] = kwargs["input"]
        return type("Process", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(mcp.subprocess, "run", fake_run)

    result = mcp.sqlcl_result(
        {
            "user": "user",
            "password": "secret",  # pragma: allowlist secret
            "host": "db",
            "port": "1521",
            "service": "test",
        },
        "select * from apex_applications where application_id = :application_id;",
        bind_variables={"application_id": 109},
    )

    assert result.exit_code == 0
    assert "variable application_id number" in captured["script"]
    assert ":application_id := 109;" in captured["script"]
    assert "where application_id = :application_id" in captured["script"]


def test_native_apex_probe_uses_temporary_export_directory(monkeypatch):
    observed = {}
    monkeypatch.setattr(
        mcp,
        "inspect_apex_context",
        lambda application_id, environment: {"ok": True, "anchor_page": "1"},
    )
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))

    def fake_sqlcl_result(profile, statements, working_directory=None):
        observed["working_directory"] = working_directory
        return mcp.CommandResult(0, "", "")

    monkeypatch.setattr(mcp, "sqlcl_result", fake_sqlcl_result)

    result = mcp.probe_native_apex_context(109, "test")

    assert result["code"] == "SUCCESS"
    assert observed["working_directory"] is not None
    assert not Path(observed["working_directory"]).exists()


def test_inspect_environment_discovers_schemas_without_hard_coding(monkeypatch):
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(
        mcp,
        "sqlcl_result",
        lambda profile, statements: mcp.CommandResult(
            0,
            "session_user=DDELACRUZ|database_name=ZAITEST|container_name=ZAITEST\n"
            "workspace_schema=DE|DDELACRUZ\nworkspace_schema=OTRO|NUEVO_SCHEMA\n"
            "workspace_applications=DE|52\nworkspace_applications=OTRO|3\n",
            "",
        ),
    )

    result = mcp.inspect_environment("test")

    assert result["code"] == "ENVIRONMENT_READY"
    assert {"workspace": "OTRO", "schema": "NUEVO_SCHEMA"} in result["workspace_schemas"]
