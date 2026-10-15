"""Regression tests for one-session, read-only Oracle query batches."""

import json
from pathlib import Path

import pytest

import scripts.apex_controlled_mcp as mcp


def _configure_batch(monkeypatch, tmp_path, fake_sqlcl):
    monkeypatch.setattr(mcp, "ROOT", Path(tmp_path))
    monkeypatch.setattr(mcp, "AUDIT_PATH", Path(tmp_path) / "audit.jsonl")
    monkeypatch.setattr(mcp, "load_profile", lambda environment: ({"user": "configured"}, None))
    monkeypatch.setattr(mcp, "sqlcl_result", fake_sqlcl)


def test_readonly_batch_runs_once_in_read_only_transaction_with_identity(monkeypatch, tmp_path):
    calls = []

    def fake_sqlcl(profile, statements, **kwargs):
        calls.append((statements, kwargs))
        markers = [line.removeprefix("prompt ") for line in statements.splitlines() if line.startswith("prompt ")]
        output = f"{markers[0]}\nDDELACRUZ|DATA|TEST\n{markers[1]}\n{markers[2]}\nrow one\n{markers[3]}\n"
        return mcp.CommandResult(0, output, "")

    _configure_batch(monkeypatch, tmp_path, fake_sqlcl)
    result = mcp.execute_readonly_batch(["select 1 from dual"], "test", {"application_id": 109, "page_id": 131})

    assert result["ok"] is True
    assert len(calls) == 1
    statements, kwargs = calls[0]
    assert kwargs["read_only_transaction"] is True
    assert kwargs["bind_variables"] == {"application_id": 109, "page_id": 131}
    assert "sys_context('userenv','session_user')" in statements
    assert result["identity"] == {"session_user": "DDELACRUZ", "current_schema": "DATA", "service": "TEST"}
    assert result["results"] == [{"index": 0, "code": "SUCCESS", "output": "row one", "ora_codes": []}]


def test_readonly_batch_rejects_entire_batch_before_profile_or_connection(monkeypatch):
    calls = []
    monkeypatch.setattr(mcp, "load_profile", lambda environment: calls.append("profile"))
    monkeypatch.setattr(mcp, "sqlcl_result", lambda *args, **kwargs: calls.append("sqlcl"))

    result = mcp.execute_readonly_batch(["select 1 from dual", "delete from data.t"], "test")

    assert result["ok"] is False
    assert result["code"] == "READ_ONLY_QUERY_REQUIRED"
    assert calls == []


@pytest.mark.parametrize(
    "queries",
    [
        ["select 1 from dual"] * 26,
        ["select 'x' from dual"] * 6,
    ],
)
def test_readonly_batch_enforces_count_and_total_size_limits(monkeypatch, queries):
    called = []
    monkeypatch.setattr(mcp, "load_profile", lambda environment: called.append(True))
    if len(queries) == 6:
        queries = ["select '" + ("x" * 19000) + "' from dual"] * len(queries)

    result = mcp.execute_readonly_batch(queries, "test")

    assert result["ok"] is False
    assert result["code"] == "BATCH_LIMIT_EXCEEDED"
    assert called == []


def test_readonly_batch_continues_after_query_error_and_reports_ora(monkeypatch, tmp_path):
    def fake_sqlcl(profile, statements, **kwargs):
        markers = [line.removeprefix("prompt ") for line in statements.splitlines() if line.startswith("prompt ")]
        return mcp.CommandResult(
            0,
            f"{markers[0]}\nORA-00904: invalid identifier\n{markers[1]}\n" f"{markers[2]}\nok\n{markers[3]}\n",
            "",
        )

    _configure_batch(monkeypatch, tmp_path, fake_sqlcl)
    result = mcp.execute_readonly_batch(
        ["select missing from dual", "select 1 from dual"], "test", include_identity=False
    )

    assert result["ok"] is False
    assert result["results"][0]["code"] == "ORACLE_ERROR"
    assert result["results"][0]["ora_codes"] == ["ORA-00904"]
    assert result["results"][1]["code"] == "SUCCESS"
    assert result["results"][1]["output"] == "ok"


def test_batch_sql_error_continuation_is_opt_in_and_mutation_default_stays_fail_closed(monkeypatch):
    captured = []
    monkeypatch.setattr(mcp, "runtime_state", lambda: {"java_home": "java", "sqlcl_path": "sql"})

    def fake_run(args, **kwargs):
        captured.append(kwargs["input"])
        return type("Process", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(mcp.subprocess, "run", fake_run)
    profile = {"user": "u", "password": "p", "host": "db", "port": "1521", "service": "test"}
    mcp.sqlcl_result(profile, "delete from data.t;")
    mcp.sqlcl_result(profile, "select 1 from dual;", continue_on_sql_error=True)

    assert "whenever sqlerror exit sql.sqlcode rollback" in captured[0]
    assert "whenever sqlerror continue" in captured[1]


def test_controlled_mutation_execution_keeps_fail_closed_sqlcl_default(monkeypatch):
    captured = {}

    def fake_sqlcl(profile, statements, **kwargs):
        captured.update(kwargs)
        return mcp.CommandResult(1031, "ORA-01031: insufficient privileges", "")

    monkeypatch.setattr(mcp, "sqlcl_result", fake_sqlcl)
    result = mcp.execute_mutation_statements({"user": "configured"}, "delete from data.t;")

    assert result["ok"] is False
    assert "continue_on_sql_error" not in captured


def test_readonly_batch_markers_do_not_split_marker_like_query_data(monkeypatch, tmp_path):
    marker = "__APEX_BATCH_1234567890_QUERY_0_BEGIN__"
    monkeypatch.setattr(mcp.uuid, "uuid4", lambda: "1234567890")

    def fake_sqlcl(profile, statements, **kwargs):
        assert marker in statements
        end = marker.replace("BEGIN", "END")
        return mcp.CommandResult(0, f"{marker}\nlookalike __APEX_BATCH_1234567890_QUERY_0_BEGIN__ suffix\n{end}\n", "")

    _configure_batch(monkeypatch, tmp_path, fake_sqlcl)
    result = mcp.execute_readonly_batch(["select 1 from dual"], "test", include_identity=False)

    assert result["results"][0]["output"] == "lookalike __APEX_BATCH_1234567890_QUERY_0_BEGIN__ suffix"


def test_readonly_batch_audit_has_hashes_and_no_sql_binds_or_result_data(monkeypatch, tmp_path):
    query = "select 'private-row-data' from dual where 109 = :application_id"

    def fake_sqlcl(profile, statements, **kwargs):
        marker = next(line.removeprefix("prompt ") for line in statements.splitlines() if line.startswith("prompt "))
        end = marker.replace("BEGIN", "END")
        return mcp.CommandResult(0, f"{marker}\nprivate-row-data\n{end}\n", "")

    _configure_batch(monkeypatch, tmp_path, fake_sqlcl)
    result = mcp.execute_readonly_batch([query], "test", {"application_id": 109}, include_identity=False)

    audit_text = (Path(tmp_path) / "audit.jsonl").read_text(encoding="utf-8")
    audit = json.loads(audit_text)
    assert result["timings_ms"]["query_count"] == 1
    assert {"profile_load", "sqlcl_process", "route_total", "query_count"} == set(result["timings_ms"])
    assert audit["source"] == "inline_readonly_batch"
    assert len(audit["query_sha256s"]) == 1
    assert audit["results"] == [{"index": 0, "code": "SUCCESS", "ora_codes": []}]
    assert query not in audit_text
    assert "private-row-data" not in audit_text
    assert '"application_id": 109' not in audit_text


def test_snapshot_queries_validate_and_use_only_supported_binds():
    path = Path(__file__).parents[1] / "skills/apex-database-diagnostics/references/page-snapshot-queries.md"
    queries = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().lower().startswith("select ")
    ]

    assert queries
    for query in queries:
        mcp.validate_read_only_query(query)
        binds = set(__import__("re").findall(r":([a-z][a-z0-9_]*)", query.lower()))
        assert binds <= {"application_id", "page_id"}


def test_diagnostic_skill_mentions_batch_tool():
    skill = (Path(__file__).parents[1] / "skills/apex-database-diagnostics/SKILL.md").read_text(encoding="utf-8")
    assert "execute_readonly_batch" in skill
