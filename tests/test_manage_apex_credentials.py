"""Regression coverage for repository-local .env credential profiles."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from env_credentials import load_apex_profile, load_database_profile, parse_env, update_env  # noqa: E402
from manage_apex_credentials import (  # noqa: E402
    ALLOWED_MODULES,
    apex_status,
    classify_connection_error,
    connection_kwargs,
    get_profile,
    import_env_profile,
    oracle_error_code,
    probe,
    read_profile,
    save_apex_profile,
    save_profile,
    status,
    validate,
)

DB_VALUES = """DB_TESTING_USER=app_user
DB_TESTING_PASSWORD=test-password
DB_TESTING_HOST=db.example
DB_TESTING_PORT=1521
DB_TESTING_SID=service
"""
APEX_VALUES = """APEX_TESTING_BASE_URL=https://apex.example
APEX_TESTING_WORKSPACE=workspace
APEX_TESTING_USER=admin
APEX_TESTING_PASSWORD=apex-secret
"""


def test_parser_reads_quotes_and_ignores_comments(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# note\nVALUE='space value'\nOTHER=plain # trailing comment\n", encoding="utf-8")

    assert parse_env(env_file) == {"VALUE": "space value", "OTHER": "plain"}


def test_update_env_preserves_unrelated_lines_and_round_trips(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# keep\nDB_ENV=test\nOTHER=unchanged\n", encoding="utf-8")

    update_env({"DB_ENV": "production", "PASSWORD": "p'ass\\word"}, env_file)

    values = parse_env(env_file)
    assert values == {"DB_ENV": "production", "OTHER": "unchanged", "PASSWORD": "p'ass\\word"}


def test_database_profile_comes_from_selected_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(DB_VALUES, encoding="utf-8")

    profile = get_profile("test", env_file)

    assert profile["db_user"] == "app_user"
    assert profile["db_pass"] == "test-password"  # pragma: allowlist secret
    assert profile["dsn"] == "db.example:1521/service"


def test_database_profile_does_not_use_process_environment(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_TESTING_USER=process-user\n", encoding="utf-8")
    monkeypatch.setenv("DB_TESTING_PASSWORD", "process-secret")
    monkeypatch.setenv("DB_TESTING_HOST", "process-host")
    monkeypatch.setenv("DB_TESTING_PORT", "1521")
    monkeypatch.setenv("DB_TESTING_SID", "service")

    profile, missing = load_database_profile("test", env_file)

    assert profile is None
    assert "DB_TESTING_PASSWORD" in missing


def test_apex_profile_comes_from_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(APEX_VALUES, encoding="utf-8")

    profile, missing = load_apex_profile("test", env_file)

    assert not missing
    assert profile["apex_pass"] == "apex-secret"


@pytest.mark.parametrize("environment,prefix", [("test", "DB_TESTING"), ("production", "DB_PRODUCTION")])
def test_load_database_profile_supports_each_environment(tmp_path, environment, prefix):
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"{prefix}_USER=user\n{prefix}_PASSWORD=pass\n{prefix}_HOST=db\n{prefix}_PORT=1521\n{prefix}_SID=svc\n",
        encoding="utf-8",
    )

    profile, missing = load_database_profile(environment, env_file)

    assert not missing
    assert profile["dsn"] == "db:1521/svc"


def test_get_profile_reports_incomplete_dotenv_profile(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_TESTING_USER=user\n", encoding="utf-8")

    assert get_profile("test", env_file) is None
    assert read_profile("apex-skills", "test", env_file)[1] == "incomplete"


def test_save_profile_updates_only_requested_env_keys(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# preserve\nOTHER=value\n", encoding="utf-8")
    profile = {
        "db_user": "user",
        "db_pass": "pass",  # pragma: allowlist secret
        "host": "host",
        "port": "1521",
        "service": "svc",
    }  # pragma: allowlist secret

    save_profile("test", profile, env_file)

    values = parse_env(env_file)
    assert values["DB_TESTING_PASSWORD"] == "pass"  # pragma: allowlist secret
    assert values["OTHER"] == "value"
    assert env_file.read_text(encoding="utf-8").startswith("# preserve\n")


def test_save_apex_profile_writes_to_same_env_file(tmp_path):
    env_file = tmp_path / ".env"

    save_apex_profile(
        "production",
        {"base_url": "https://apex.example/", "workspace": "ws", "apex_user": "u", "apex_pass": "p"},
        env_file,
    )

    values = parse_env(env_file)
    assert values["APEX_PRODUCTION_BASE_URL"] == "https://apex.example"
    assert values["APEX_PRODUCTION_PASSWORD"] == "p"


def test_profile_writers_reject_incomplete_values(tmp_path):
    with pytest.raises(SystemExit):
        save_profile("test", {"db_user": "only-user"}, tmp_path / ".env")
    with pytest.raises(SystemExit):
        save_apex_profile("test", {"apex_user": "only-user"}, tmp_path / ".env")


def test_status_and_apex_status_report_readiness(tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text(DB_VALUES + APEX_VALUES, encoding="utf-8")

    assert read_profile("apex-skills", "test", env_file)[1] == "ready"
    assert status("test", env_file) == 0
    assert apex_status("test", env_file) == 0
    assert "ORACLE_PROFILE_READY" in capsys.readouterr().out


def test_import_env_is_validation_only(tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text(DB_VALUES, encoding="utf-8")
    before = env_file.read_text(encoding="utf-8")

    import_env_profile("test", env_file)

    assert env_file.read_text(encoding="utf-8") == before
    assert "ENV_PROFILE_READY" in capsys.readouterr().out


def test_import_env_rejects_missing_profile(tmp_path):
    with pytest.raises(SystemExit):
        import_env_profile("test", tmp_path / ".env")


def test_credential_reader_allows_only_oracle_driver():
    assert ALLOWED_MODULES == {"oracledb"}


def test_connection_kwargs_includes_optional_wallet_fields():
    kwargs = connection_kwargs(
        {
            "db_user": "u",
            "db_pass": "p",
            "dsn": "db/svc",
            "wallet_dir": "wallet",
            "wallet_pass": "wallet-pass",  # pragma: allowlist secret
        }
    )

    assert kwargs["config_dir"] == "wallet"
    assert kwargs["wallet_location"] == "wallet"
    assert kwargs["wallet_password"] == "wallet-pass"  # pragma: allowlist secret


@pytest.mark.parametrize(
    "code,expected",
    [
        ("01017", "ORACLE_AUTH_FAIL"),
        ("28000", "ORACLE_AUTH_FAIL"),
        ("12514", "ORACLE_CONNECTION_FAIL"),
        ("00942", "ORACLE_PROBE_FAIL"),
    ],
)
def test_connection_error_classification(code, expected):
    error = Exception(f"ORA-{code}: diagnostic detail")

    assert oracle_error_code(error) == code
    assert classify_connection_error(error) == expected


def test_probe_uses_dotenv_profile_and_hides_driver_message(tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text(DB_VALUES, encoding="utf-8")
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.cursor.return_value.__enter__.return_value.fetchone.return_value = ("APP_USER", "APP_USER")
    driver = MagicMock()
    driver.connect.return_value = connection

    with (
        patch("manage_apex_credentials.get_profile", return_value=get_profile("test", env_file)),
        patch("manage_apex_credentials.import_module_safe", return_value=driver),
    ):
        assert probe("test") == 0

    assert driver.connect.call_args.kwargs["password"] == "test-password"  # pragma: allowlist secret
    assert "source=.env" in capsys.readouterr().out


def test_probe_reports_authentication_error_without_driver_details(tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text(DB_VALUES, encoding="utf-8")
    driver = MagicMock()
    driver.connect.side_effect = Exception("ORA-01017: secret-host and password detail")

    with (
        patch("manage_apex_credentials.get_profile", return_value=get_profile("test", env_file)),
        patch("manage_apex_credentials.import_module_safe", return_value=driver),
    ):
        assert probe("test") == 1

    output = capsys.readouterr().out
    assert "ORACLE_AUTH_FAIL environment=test error=ORA-01017" in output
    assert "secret-host" not in output


def test_validate_uses_read_only_identity_query(tmp_path, capsys):
    env_file = tmp_path / ".env"
    env_file.write_text(DB_VALUES, encoding="utf-8")
    cursor = MagicMock()
    cursor.__enter__.return_value = cursor
    cursor.fetchone.return_value = ("APP_USER",)
    connection = MagicMock()
    connection.__enter__.return_value = connection
    connection.cursor.return_value = cursor
    driver = MagicMock()
    driver.connect.return_value = connection

    with (
        patch("manage_apex_credentials.get_profile", return_value=get_profile("test", env_file)),
        patch("manage_apex_credentials.import_module_safe", return_value=driver),
    ):
        assert validate("test") == 0

    assert "from dual" in cursor.execute.call_args.args[0].lower()
    assert "source=.env" in capsys.readouterr().out
