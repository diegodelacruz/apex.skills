"""Tests for the controlled local SQLcl MCP without Oracle connectivity."""

import json
import subprocess
import sys
from pathlib import Path

import scripts.apex_controlled_mcp as mcp


def test_doctor_reports_missing_runtime(monkeypatch, tmp_path):
    monkeypatch.setenv(mcp.RUNTIME_ENV, str(tmp_path))

    result = mcp.doctor_report()

    assert result["ready"] is False
    assert result["code"] == "RUNTIME_NOT_INSTALLED"


def test_runtime_state_reads_utf8_bom(monkeypatch, tmp_path):
    state = {"java_home": "java", "sqlcl_path": "sqlcl"}
    (tmp_path / "runtime-state.json").write_bytes(b"\xef\xbb\xbf" + json.dumps(state).encode("utf-8"))
    monkeypatch.setenv(mcp.RUNTIME_ENV, str(tmp_path))

    assert mcp.runtime_state() == state


def test_runtime_state_reads_utf8_without_bom(monkeypatch, tmp_path):
    state = {"java_home": "java", "sqlcl_path": "sqlcl"}
    (tmp_path / "runtime-state.json").write_bytes(json.dumps(state).encode("utf-8"))
    monkeypatch.setenv(mcp.RUNTIME_ENV, str(tmp_path))

    assert mcp.runtime_state() == state


def test_doctor_does_not_report_missing_runtime_for_utf8_bom(monkeypatch, tmp_path):
    java_home = tmp_path / "java"
    java_exe = java_home / "bin" / "java.exe"
    sqlcl_path = tmp_path / "sqlcl.exe"
    java_exe.parent.mkdir(parents=True)
    java_exe.write_text("", encoding="utf-8")
    sqlcl_path.write_text("", encoding="utf-8")
    state = {"java_home": str(java_home), "sqlcl_path": str(sqlcl_path)}
    (tmp_path / "runtime-state.json").write_bytes(b"\xef\xbb\xbf" + json.dumps(state).encode("utf-8"))
    monkeypatch.setenv(mcp.RUNTIME_ENV, str(tmp_path))
    monkeypatch.setattr(
        mcp.subprocess,
        "run",
        lambda *args, **kwargs: type("Process", (), {"returncode": 0, "stdout": "SQLcl", "stderr": ""})(),
    )

    assert mcp.doctor_report()["code"] != "RUNTIME_NOT_INSTALLED"


def test_doctor_reports_registered_missing_binary(monkeypatch, tmp_path):
    state = {"java_home": str(tmp_path / "java"), "sqlcl_path": str(tmp_path / "sql.exe")}
    (tmp_path / "runtime-state.json").write_text(json.dumps(state), encoding="utf-8")
    monkeypatch.setenv(mcp.RUNTIME_ENV, str(tmp_path))

    result = mcp.doctor_report()

    assert result["code"] == "RUNTIME_INTEGRITY_FAILED"


def test_explicit_doctor_probes_sqlcl_version(monkeypatch, tmp_path):
    java_home = tmp_path / "java"
    java_exe = java_home / "bin" / "java.exe"
    sqlcl_path = tmp_path / "sqlcl.exe"
    java_exe.parent.mkdir(parents=True)
    java_exe.write_text("", encoding="utf-8")
    sqlcl_path.write_text("", encoding="utf-8")
    (tmp_path / "runtime-state.json").write_text(
        json.dumps({"java_home": str(java_home), "sqlcl_path": str(sqlcl_path)}), encoding="utf-8"
    )
    monkeypatch.setenv(mcp.RUNTIME_ENV, str(tmp_path))
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured.update(kwargs)
        return type("Process", (), {"returncode": 0, "stdout": "SQLcl: Release 24", "stderr": ""})()

    monkeypatch.setattr(mcp.subprocess, "run", fake_run)

    result = mcp.doctor_report()

    assert result["ready"] is True
    assert captured["args"] == [str(sqlcl_path), "-version"]
    assert captured["timeout"] == 30


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
    monkeypatch.setattr(
        mcp,
        "doctor_report",
        lambda: (_ for _ in ()).throw(AssertionError("read-only query must not run the runtime doctor")),
    )
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
    assert set(result["timings_ms"]) == {"profile_load", "sqlcl_process", "route_total"}
    assert all(isinstance(value, int) and value >= 0 for value in result["timings_ms"].values())
    assert captured["read_only_transaction"] is True
    assert captured["bind_variables"] == {"app": 130, "page": 100}
    audit = json.loads((tmp_path / "audit.jsonl").read_text(encoding="utf-8"))
    assert audit["source"] == "inline_readonly_query"
    assert audit["source_sha256"]
    assert audit["timings_ms"] == result["timings_ms"]
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
    assert "set transaction read only;\n" in script
    assert script.index("set transaction read only") < script.index("select 1 from dual")


def test_sqlcl_result_uses_tolerant_utf8_for_accented_input_and_output(monkeypatch):
    captured = {}
    monkeypatch.setattr(mcp, "runtime_state", lambda: {"java_home": "java", "sqlcl_path": "sql"})

    def fake_run(args, **kwargs):
        captured.update(kwargs)
        return type(
            "Process", (), {"returncode": 0, "stdout": b"\xc3\xb3\xc3\x81\xc3\x91\xc3\xbc\x81", "stderr": b""}
        )()

    monkeypatch.setattr(mcp.subprocess, "run", fake_run)

    result = mcp.sqlcl_result(
        {"user": "u", "password": "p", "host": "db", "port": "1521", "service": "test"},
        "select 'Histórico → ñ' from dual;",
        read_only_transaction=True,
        strict_input=False,
    )

    assert result.stdout == "óÁÑü�"
    assert "Histórico ? ñ" in captured["input"]
    assert captured["input"].splitlines()[0] == "set encoding utf8"
    assert captured["encoding"] == "cp1252"
    assert captured["errors"] == "surrogateescape"


def test_decode_sqlcl_stream_decodes_real_cp1252_surrogateescaped_utf8_output():
    process = subprocess.run(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'\\xc3\\xb3\\xc3\\xb1')"],
        capture_output=True,
        check=True,
        text=True,
        encoding="cp1252",
        errors="surrogateescape",
    )

    assert mcp.decode_sqlcl_stream(process.stdout) == "óñ"


def test_cp1252_input_reaches_a_real_child_as_its_original_bytes():
    process = subprocess.run(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"],
        capture_output=True,
        check=True,
        input=mcp.encode_sqlcl_input("óñ"),
        text=True,
        encoding="cp1252",
        errors="surrogateescape",
    )

    assert process.stdout.encode("cp1252") == b"\xf3\xf1"


def test_sqlcl_result_fails_closed_before_starting_process_for_unrepresentable_input(monkeypatch):
    monkeypatch.setattr(mcp, "runtime_state", lambda: {"java_home": "java", "sqlcl_path": "sql"})
    monkeypatch.setattr(
        mcp.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("SQLcl must not start")),
    )

    result = mcp.classify_result(
        mcp.sqlcl_result(
            {"user": "u", "password": "p", "host": "db", "port": "1521", "service": "test"},
            "comment on table data.t is 'a→b';",
        )
    )

    assert result["code"] == "UNREPRESENTABLE_CHARACTERS"
    assert "CP1252" in result["message"]


def test_write_routes_reject_unrepresentable_artifacts_before_starting_sqlcl(monkeypatch, tmp_path):
    change = tmp_path / "change.sql"
    change.write_text("comment on table data.t is 'a→b';", encoding="utf-8")
    preflight = tmp_path / "preflight.sql"
    preflight.write_text("select 'a→b' from dual;", encoding="utf-8")
    apply = tmp_path / "apply.sql"
    apply.write_text("comment on table data.t is 'safe';", encoding="utf-8")
    verify = tmp_path / "verify.sql"
    verify.write_text("select 1 from dual;", encoding="utf-8")
    (tmp_path / "change.json").write_text(
        json.dumps(
            {
                "version": 1,
                "id": "cp1252-closed",
                "kind": "oracle_data",
                "target": {"type": "table", "name": "DATA.T"},
                "baseline": {"fingerprint": "sha256:observed"},
                "artifacts": {"preflight": "preflight.sql", "apply": "apply.sql", "verify": "verify.sql"},
            }
        ),
        encoding="utf-8",
    )
    page = tmp_path / "f109_p131.sql"
    page.write_text("begin\nwwv_flow_imp.import_begin;\n-- a→b\nwwv_flow_imp.import_end;\nend;\n/", encoding="utf-8")
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(
        mcp,
        "load_profile",
        lambda environment: ({"user": "u", "password": "p", "host": "db", "port": "1521", "service": "test"}, None),
    )
    monkeypatch.setattr(mcp, "runtime_state", lambda: {"java_home": "java", "sqlcl_path": "sql"})
    monkeypatch.setattr(
        mcp.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("SQLcl must not start")),
    )

    sql_file = mcp.execute_sql_file("change.sql", confirmed=True, backup_choice="no", environment="test")
    bundle = mcp.execute_change_bundle("change.json", confirmed=True, backup_choice="no", environment="test")
    deployment = mcp.deploy_apex_page("f109_p131.sql", confirmed=True, backup_choice="no", environment="test")

    assert sql_file["code"] == "UNREPRESENTABLE_CHARACTERS"
    assert bundle["code"] == "UNREPRESENTABLE_CHARACTERS"
    assert deployment["code"] == "UNREPRESENTABLE_CHARACTERS"


def test_sqlcl_runtime_failure_is_reported_without_preflight(monkeypatch):
    monkeypatch.setattr(mcp, "runtime_state", lambda: None)

    result = mcp.classify_result(
        mcp.sqlcl_result(
            {"user": "u", "password": "p", "host": "db", "port": "1521", "service": "test"},
            "select 1 from dual;",
        )
    )

    assert result["code"] == "RUNTIME_NOT_INSTALLED"
    assert "doctor()" in result["message"]


def test_sqlcl_runtime_state_failure_is_reported_without_starting_process(monkeypatch):
    monkeypatch.setattr(mcp, "runtime_state", lambda: {"sqlcl_path": "sqlcl.exe"})
    monkeypatch.setattr(
        mcp.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("SQLcl should not start without JAVA_HOME")),
    )

    result = mcp.classify_result(
        mcp.sqlcl_result(
            {"user": "u", "password": "p", "host": "db", "port": "1521", "service": "test"},
            "select 1 from dual;",
        )
    )

    assert result["code"] == "RUNTIME_INTEGRITY_FAILED"
    assert "doctor()" in result["message"]


def test_doctor_report_is_only_called_by_explicit_doctor_tool():
    import ast

    tree = ast.parse(Path(mcp.__file__).read_text(encoding="utf-8"))
    doctor_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "doctor_report"
    ]

    assert len(doctor_calls) == 1


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
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    events = [json.loads(line) for line in audit_text.splitlines()]
    assert [event["event_phase"] for event in events] == ["started", "completed"]
    assert events[0]["event_id"] == events[1]["event_id"] == result["audit_event_id"]
    assert events[0]["source"] == "change.sql"
    assert events[1]["timings_ms"]["sqlcl_process"] >= 0
    assert result["timings_ms"] == events[1]["timings_ms"]
    assert "tmp_test" not in audit_text


def test_execute_artifact_fails_closed_when_start_event_cannot_be_saved(monkeypatch, tmp_path):
    artifact = tmp_path / "change.sql"
    artifact.write_text("delete from data.t;", encoding="utf-8")
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(mcp, "append_audit_entry", lambda entry: "OSError: disk unavailable")
    monkeypatch.setattr(mcp, "sqlcl_result", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("SQL ran")))

    result = mcp.execute_artifact("change.sql", "test", "oracle_sql_file")

    assert result["code"] == "AUDIT_START_FAILED"
    assert "no se ejecutó" in result["message"]


def test_execute_artifact_warns_not_to_retry_when_completion_event_fails(monkeypatch, tmp_path):
    artifact = tmp_path / "change.sql"
    artifact.write_text("delete from data.t;", encoding="utf-8")
    appended = []

    def append(entry):
        appended.append(entry)
        return None if len(appended) == 1 else "OSError: disk unavailable"

    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(mcp, "append_audit_entry", append)
    monkeypatch.setattr(mcp, "sqlcl_result", lambda *args, **kwargs: mcp.CommandResult(0, "", ""))

    result = mcp.execute_artifact("change.sql", "test", "oracle_sql_file")

    assert result["code"] == "AUDIT_COMPLETION_FAILED"
    assert result["operation_result"] == "SUCCESS"
    assert "no la reintente automáticamente" in result["message"]
    assert appended[0]["event_id"] == appended[1]["event_id"]
    assert appended[0]["event_phase"] == "started"
    assert appended[1]["event_phase"] == "completed"


def test_execute_artifact_closes_audit_when_adapter_raises(monkeypatch, tmp_path):
    artifact = tmp_path / "change.sql"
    artifact.write_text("delete from data.t;", encoding="utf-8")
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(
        mcp,
        "sqlcl_result",
        lambda *args, **kwargs: (_ for _ in ()).throw(TimeoutError("connection ended unexpectedly")),
    )

    result = mcp.execute_artifact("change.sql", "test", "oracle_sql_file")
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]

    assert result["code"] == "ADAPTER_EXECUTION_FAILED"
    assert "no debe repetirse automáticamente" in result["message"]
    assert [event["event_phase"] for event in events] == ["started", "completed"]
    assert events[0]["event_id"] == events[1]["event_id"]
    assert events[1]["result"] == "ADAPTER_EXECUTION_FAILED"


def test_execute_change_bundle_requires_valid_preflight_artifacts(monkeypatch, tmp_path):
    manifest = tmp_path / "change.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "no")

    assert result["ok"] is False
    assert result["code"] == "INVALID_CHANGE_BUNDLE"


def test_execute_change_bundle_records_hashes_and_phase_timings(monkeypatch, tmp_path):
    artifacts = {}
    for phase in ("preflight", "apply", "verify", "rollback"):
        source = tmp_path / f"{phase}.sql"
        source.write_text(f"prompt {phase}\n", encoding="utf-8")
        artifacts[phase] = source.name
    manifest = tmp_path / "change.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "id": "fix-live-change",
                "kind": "oracle_ddl",
                "target": {"type": "view", "name": "data.v_example"},
                "baseline": {"fingerprint": "sha256:observed"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))

    def sqlcl_result(profile, statements):
        if "CHANGE_PHASE=preflight" in statements:
            return mcp.CommandResult(
                0,
                "__CHANGE_BASELINE_OK=sha256:observed\n"
                "__CHANGE_TIMER_preflight_START=1\n__CHANGE_TIMER_preflight_END=2\n",  # pragma: allowlist secret
                "",
            )
        return mcp.CommandResult(
            0,
            "__CHANGE_TIMER_apply_START=3\n__CHANGE_TIMER_apply_END=5\n"
            "__CHANGE_TIMER_verify_START=6\n__CHANGE_TIMER_verify_END=7\n",
            "",
        )

    monkeypatch.setattr(mcp, "sqlcl_result", sqlcl_result)

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "no")

    assert result["ok"] is True
    assert result["phase_durations_ms"] == {"apply": 20, "verify": 10}
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    events = [json.loads(line) for line in audit_text.splitlines()]
    assert [event["event_phase"] for event in events] == ["started", "completed"]
    assert events[0]["event_id"] == events[1]["event_id"]
    assert events[0]["bundle_id"] == "fix-live-change"
    assert events[1]["artifact_sha256"]["apply"]
    assert "prompt apply" not in audit_text


def test_execute_change_bundle_does_not_apply_when_baseline_marker_is_missing(monkeypatch, tmp_path):
    artifacts = {}
    for phase in ("preflight", "apply", "verify", "rollback"):
        source = tmp_path / f"{phase}.sql"
        source.write_text(f"prompt {phase}\n", encoding="utf-8")
        artifacts[phase] = source.name
    (tmp_path / "change.json").write_text(
        json.dumps(
            {
                "version": 1,
                "id": "refuse-baseline-mismatch",
                "kind": "oracle_ddl",
                "target": {"type": "view", "name": "data.v_example"},
                "baseline": {"fingerprint": "sha256:expected"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    calls = []
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(
        mcp,
        "sqlcl_result",
        lambda profile, statements: calls.append(statements) or mcp.CommandResult(0, "SELECT completed", ""),
    )

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "no")

    assert result["ok"] is False
    assert result["code"] == "BASELINE_MISMATCH"
    assert len(calls) == 1
    assert "CHANGE_PHASE=apply" not in calls[0]


def _create_audited_bundle(tmp_path):
    artifacts = {}
    for phase in ("preflight", "apply", "verify"):
        source = tmp_path / f"{phase}.sql"
        source.write_text(f"prompt {phase}\n", encoding="utf-8")
        artifacts[phase] = source.name
    manifest = tmp_path / "change.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "id": "audit-failure-bundle",
                "kind": "oracle_ddl",
                "target": {"type": "view", "name": "data.v_example"},
                "baseline": {"fingerprint": "sha256:observed"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    return manifest


def test_change_bundle_fails_closed_when_start_audit_cannot_be_saved(monkeypatch, tmp_path):
    _create_audited_bundle(tmp_path)
    calls = []
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(mcp, "append_audit_entry", lambda entry: "OSError: disk unavailable")
    monkeypatch.setattr(mcp, "sqlcl_result", lambda *args: calls.append(args))

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "no")

    assert result["code"] == "AUDIT_START_FAILED"
    assert calls == []


def test_change_bundle_warns_not_to_retry_when_completion_audit_fails(monkeypatch, tmp_path):
    _create_audited_bundle(tmp_path)
    appended = []

    def append(entry):
        appended.append(entry)
        return None if len(appended) == 1 else "OSError: disk unavailable"

    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))
    monkeypatch.setattr(mcp, "append_audit_entry", append)
    monkeypatch.setattr(
        mcp,
        "sqlcl_result",
        lambda profile, statements: mcp.CommandResult(
            0,
            "__CHANGE_BASELINE_OK=sha256:observed\n" if "CHANGE_PHASE=preflight" in statements else "",
            "",
        ),
    )

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "no")

    assert result["code"] == "AUDIT_COMPLETION_FAILED"
    assert result["operation_result"] == "SUCCESS"
    assert "no la reintente automáticamente" in result["message"]
    assert [event["event_phase"] for event in appended] == ["started", "completed"]
    assert appended[0]["event_id"] == appended[1]["event_id"]


def test_mutation_tools_require_explicit_action_and_backup_answers():
    missing_action = mcp.execute_sql_file("change.sql", backup_choice="no")
    missing_backup = mcp.execute_change_bundle("change.json", confirmed=True)
    missing_both = mcp.deploy_apex_page("page.sql")

    assert missing_action["code"] == "USER_CONFIRMATION_REQUIRED"
    assert missing_backup["code"] == "BACKUP_CHOICE_REQUIRED"
    assert missing_both["code"] == "USER_CONFIRMATION_REQUIRED"


def test_execute_sql_file_runs_requested_backup_before_change(monkeypatch, tmp_path):
    (tmp_path / "backup.sql").write_text("create table backup_data as select * from data.t;", encoding="utf-8")
    (tmp_path / "change.sql").write_text("delete from data.t;", encoding="utf-8")
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    calls = []

    def execute_artifact(path, environment, operation, decision_metadata=None):
        calls.append((path, operation, decision_metadata))
        return {"ok": True, "code": "SUCCESS", "source": path}

    monkeypatch.setattr(mcp, "execute_artifact", execute_artifact)

    result = mcp.execute_sql_file(
        "change.sql",
        confirmed=True,
        backup_choice="yes",
        backup_sql_path="backup.sql",
        environment="test",
    )

    assert [call[0] for call in calls] == ["backup.sql", "change.sql"]
    assert result["backup_choice"] == "yes"
    assert result["backup_result"] == "SUCCESS"


def test_execute_sql_file_stops_when_requested_backup_fails(monkeypatch, tmp_path):
    (tmp_path / "backup.sql").write_text("create table backup_data as select * from data.t;", encoding="utf-8")
    (tmp_path / "change.sql").write_text("delete from data.t;", encoding="utf-8")
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    calls = []

    def execute_artifact(path, environment, operation, decision_metadata=None):
        calls.append(path)
        return {"ok": False, "code": "EXECUTION_ERROR", "message": "backup failed"}

    monkeypatch.setattr(mcp, "execute_artifact", execute_artifact)

    result = mcp.execute_sql_file(
        "change.sql",
        confirmed=True,
        backup_choice="yes",
        backup_sql_path="backup.sql",
        environment="test",
    )

    assert calls == ["backup.sql"]
    assert result["code"] == "BACKUP_FAILED"


def test_execute_sql_file_does_not_accept_backup_artifact_when_declined():
    result = mcp.execute_sql_file("change.sql", confirmed=True, backup_choice="no", backup_sql_path="backup.sql")

    assert result["code"] == "UNEXPECTED_BACKUP_ARTIFACT"


def test_execute_change_bundle_requires_snapshot_when_backup_accepted(monkeypatch, tmp_path):
    artifacts = {}
    for phase in ("preflight", "apply", "verify", "rollback"):
        (tmp_path / f"{phase}.sql").write_text("select 1 from dual;", encoding="utf-8")
        artifacts[phase] = f"{phase}.sql"
    manifest = tmp_path / "change.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "id": "require-backup",
                "kind": "oracle_data",
                "target": {"type": "table", "name": "DATA.T"},
                "baseline": {"fingerprint": "sha256:observed"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "yes")

    assert result["code"] == "BACKUP_ARTIFACT_REQUIRED"


def test_execute_change_bundle_rejects_snapshot_when_backup_declined(monkeypatch, tmp_path):
    artifacts = {}
    for phase in ("preflight", "apply", "verify", "snapshot"):
        (tmp_path / f"{phase}.sql").write_text("select 1 from dual;", encoding="utf-8")
        artifacts[phase] = f"{phase}.sql"
    manifest = tmp_path / "change.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "id": "declined-backup",
                "kind": "oracle_data",
                "target": {"type": "table", "name": "DATA.T"},
                "baseline": {"fingerprint": "sha256:observed"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    calls = []
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "doctor_report", lambda: calls.append("doctor") or {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "sqlcl_result", lambda *args: calls.append(args))

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "no")

    assert result["code"] == "UNEXPECTED_BACKUP_ARTIFACT"
    assert calls == []


def test_execute_change_bundle_runs_accepted_snapshot_before_apply(monkeypatch, tmp_path):
    artifacts = {}
    for phase in ("preflight", "snapshot", "apply", "verify", "rollback"):
        (tmp_path / f"{phase}.sql").write_text(f"prompt {phase}\n", encoding="utf-8")
        artifacts[phase] = f"{phase}.sql"
    (tmp_path / "change.json").write_text(
        json.dumps(
            {
                "version": 1,
                "id": "backup-before-change",
                "kind": "oracle_data",
                "target": {"type": "table", "name": "DATA.T"},
                "baseline": {"fingerprint": "sha256:observed"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    calls = []
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))

    def sqlcl_result(profile, statements):
        calls.append(statements)
        if "CHANGE_PHASE=preflight" in statements:
            return mcp.CommandResult(0, "__CHANGE_BASELINE_OK=sha256:observed\n", "")
        return mcp.CommandResult(0, "completed", "")

    monkeypatch.setattr(mcp, "sqlcl_result", sqlcl_result)

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "yes")

    assert len(calls) == 3
    assert "CHANGE_PHASE=preflight" in calls[0]
    assert "CHANGE_PHASE=snapshot" in calls[1]
    assert "CHANGE_PHASE=apply" in calls[2]
    assert result["backup_result"] == "SUCCESS"
    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["event_phase"] for event in events] == ["started", "completed"]
    assert events[0]["event_id"] == events[1]["event_id"]
    assert events[1]["backup_choice"] == "yes"


def test_execute_change_bundle_stops_when_snapshot_fails(monkeypatch, tmp_path):
    artifacts = {}
    for phase in ("preflight", "snapshot", "apply", "verify", "rollback"):
        (tmp_path / f"{phase}.sql").write_text(f"prompt {phase}\n", encoding="utf-8")
        artifacts[phase] = f"{phase}.sql"
    (tmp_path / "change.json").write_text(
        json.dumps(
            {
                "version": 1,
                "id": "stop-on-backup-error",
                "kind": "oracle_data",
                "target": {"type": "table", "name": "DATA.T"},
                "baseline": {"fingerprint": "sha256:observed"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    calls = []
    monkeypatch.setattr(mcp, "ROOT", tmp_path)
    monkeypatch.setattr(mcp, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(mcp, "doctor_report", lambda: {"ready": True, "code": "READY"})
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "x"}, None))

    def sqlcl_result(profile, statements):
        calls.append(statements)
        if "CHANGE_PHASE=preflight" in statements:
            return mcp.CommandResult(0, "__CHANGE_BASELINE_OK=sha256:observed\n", "")
        return mcp.CommandResult(1, "", "ORA-01031: insufficient privileges")

    monkeypatch.setattr(mcp, "sqlcl_result", sqlcl_result)

    result = mcp.execute_change_bundle_artifact("change.json", "test", True, "yes")

    assert result["code"] == "BACKUP_FAILED"
    assert len(calls) == 2
    assert "CHANGE_PHASE=snapshot" in calls[1]
    assert "CHANGE_PHASE=apply" not in calls[1]


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
