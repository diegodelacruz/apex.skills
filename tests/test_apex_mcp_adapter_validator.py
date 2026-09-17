import hashlib
from pathlib import Path

import scripts.validate_apex_mcp_adapter as validator


def write_adapter(root: Path, db_source: str) -> None:
    (root / "tools").mkdir(parents=True)
    (root / "__init__.py").write_text("", encoding="utf-8")
    (root / "db.py").write_text(db_source, encoding="utf-8")
    (root / "tools" / "sql_tools.py").write_text("def apex_connect(): pass\n", encoding="utf-8")


VALID_DB = """
connect_kwargs = {\"user\": user, \"password\": password, \"dsn\": dsn}
if wallet_dir:
    connect_kwargs[\"config_dir\"] = wallet_dir
connection = oracledb.connect(**connect_kwargs)
"""


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def test_valid_contract_is_ready_and_unsafe_surface_is_separate(tmp_path):
    adapter = tmp_path / "apex_mcp"
    write_adapter(adapter, VALID_DB)
    (adapter / "tools" / "sql_tools.py").write_text("# UPDATE APEX_240100.x\n", encoding="utf-8")

    result = validator.validate_adapter(adapter)

    assert result.adapter_status == "MCP_ADAPTER_READY"
    assert result.surface_status == "MCP_SURFACE_UNSAFE"


def test_contract_without_connect_kwargs_is_incompatible(tmp_path):
    adapter = tmp_path / "apex_mcp"
    write_adapter(adapter, "connection = oracledb.connect(user=user, password=password, dsn=dsn)\n")

    assert validator.validate_adapter(adapter).adapter_status == "MCP_ADAPTER_INCOMPATIBLE"


def test_contract_without_direct_connect_call_is_incompatible(tmp_path):
    adapter = tmp_path / "apex_mcp"
    write_adapter(adapter, "connect_kwargs = {}\nif wallet_dir:\n    pass\n")

    assert validator.validate_adapter(adapter).adapter_status == "MCP_ADAPTER_INCOMPATIBLE"


def test_missing_adapter_is_unverified(tmp_path):
    result = validator.validate_adapter(tmp_path / "missing")

    assert result.adapter_status == "MCP_ADAPTER_UNVERIFIED"
    assert result.surface_status == "MCP_SURFACE_NOT_EVALUATED"


def test_validator_does_not_mutate_inspected_files(tmp_path):
    adapter = tmp_path / "apex_mcp"
    write_adapter(adapter, VALID_DB)
    before = tree_hash(adapter)

    validator.validate_adapter(adapter)

    assert tree_hash(adapter) == before
