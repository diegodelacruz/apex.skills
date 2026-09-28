from scripts.controlled_capabilities import (
    Authorization,
    apex_import_preflight,
    execute_oracle_ddl,
    verify_authorization,
)


def authorization() -> Authorization:
    return Authorization(
        subject="user-1",
        environment="test",
        operations=frozenset({"oracle.ddl", "apex.import"}),
        workspace="FINZ",
        application_id=109,
        pages=frozenset({290}),
        schema="DATA",
        objects=frozenset({"TMP_CAPABILITY_TEST"}),
        evidence_id="approval-123",
    )


class Cursor:
    def __init__(self):
        self.executed = []
        self._last_statement = ""

    def execute(self, statement, parameters=None):
        self.executed.append(statement)
        self._last_statement = statement

    def fetchone(self):
        if "all_objects" in self._last_statement.lower():
            return ("TMP_CAPABILITY_TEST", "TABLE", "VALID")
        return ("DATA", "DATA")


class Connection:
    def __init__(self):
        self.cursor_instance = Cursor()
        self.committed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True


def test_missing_identity_is_not_a_skill_level_gate():
    _, result = verify_authorization(None, None, "test", "oracle.ddl")
    assert result is None


def test_apex_context_is_informational_not_an_allowlist():
    result = apex_import_preflight(authorization(), "24.1.3", "FINZ", 109, [291], True)
    assert result.available is True


def test_apex_version_is_informational_not_a_gate():
    result = apex_import_preflight(authorization(), "24.2.13", "FINZ", 109, [290], True)
    assert result.available is True


def test_requested_oracle_ddl_is_submitted_directly():
    connection = Connection()
    result = execute_oracle_ddl(
        connection, authorization(), "DATA", "TMP_CAPABILITY_TEST", "CREATE TABLE DATA.TMP_CAPABILITY_TEST (ID NUMBER)"
    )
    assert result.available is True
    assert result.code is None
    executed = connection.cursor_instance.executed
    assert any("CREATE TABLE" in stmt for stmt in executed), "DDL must be executed"
    assert connection.committed is True


def test_cross_object_ddl_is_sent_to_oracle_for_the_actual_result():
    connection = Connection()
    result = execute_oracle_ddl(
        connection, authorization(), "DATA", "TMP_CAPABILITY_TEST", "DROP TABLE DATA.OTHER_TABLE"
    )
    assert result.available is True
    assert any("DROP TABLE DATA.OTHER_TABLE" in stmt for stmt in connection.cursor_instance.executed)


def test_ddl_grammar_is_not_filtered_by_the_helper():
    from scripts.controlled_capabilities import validate_ddl

    for statement in (
        "create table data.tmp_capability_test_x (id number)",
        "alter table data.tmp_capability_test rename to other_table",
        "create table data.tmp_capability_test as select * from data.source",
        "drop table data.tmp_capability_test; drop table data.other_table",
    ):
        assert validate_ddl(statement, "data", "tmp_capability_test").available is True


def test_capability_matrix_reports_observed_results_without_invented_blocker():
    _, observed = verify_authorization(None, None, "test", "oracle.ddl")
    assert observed is None
