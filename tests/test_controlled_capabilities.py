from scripts.controlled_capabilities import (
    Authorization,
    CapabilityErrorCode,
    apex_import_preflight,
    capability_matrix,
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

    def execute(self, statement, parameters=None):
        self.executed.append(statement)

    def fetchone(self):
        return ("DATA", "DATA")


class Connection:
    def __init__(self):
        self.cursor_instance = Cursor()

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        raise AssertionError("DDL must not claim transactional commit handling")


def test_missing_identity_is_external_blocker():
    _, result = verify_authorization(None, None, "test", "oracle.ddl")
    assert result.code is CapabilityErrorCode.EXTERNAL_DEPENDENCY_BLOCKED


def test_wrong_scope_is_authorization_denied():
    result = apex_import_preflight(authorization(), "24.1.3", "FINZ", 109, [291], True)
    assert result.code is CapabilityErrorCode.AUTHORIZATION_DENIED


def test_incompatible_apex_is_not_a_privilege_error():
    result = apex_import_preflight(authorization(), "24.2.13", "FINZ", 109, [290], True)
    assert result.code is CapabilityErrorCode.ADAPTER_INCOMPATIBLE


def test_scoped_oracle_ddl_uses_same_connection_identity():
    connection = Connection()
    result = execute_oracle_ddl(
        connection, authorization(), "DATA", "TMP_CAPABILITY_TEST", "create table data.tmp_capability_test (id number)"
    )
    assert result.code is CapabilityErrorCode.ADAPTER_INCOMPATIBLE
    assert connection.cursor_instance.executed == []


def test_cross_object_ddl_is_denied_before_execution():
    connection = Connection()
    result = execute_oracle_ddl(
        connection, authorization(), "DATA", "TMP_CAPABILITY_TEST", "drop table data.other_table"
    )
    assert result.code is CapabilityErrorCode.ADAPTER_INCOMPATIBLE
    assert connection.cursor_instance.executed == []


def test_ddl_grammar_rejects_common_bypasses():
    from scripts.controlled_capabilities import validate_ddl

    for statement in (
        "create table data.tmp_capability_test_x (id number)",
        "alter table data.tmp_capability_test rename to other_table",
        "create table data.tmp_capability_test as select * from data.source",
        "drop table data.tmp_capability_test; drop table data.other_table",
    ):
        assert validate_ddl(statement, "data", "tmp_capability_test").available is False


def test_capability_matrix_preserves_blocked_state():
    _, blocked = verify_authorization(None, None, "test", "oracle.ddl")
    matrix = capability_matrix(blocked, blocked, blocked, blocked)
    assert matrix["oracle_create_modify_delete"]["available"] is False
    assert matrix["apex"]["code"] == "EXTERNAL_DEPENDENCY_BLOCKED"
