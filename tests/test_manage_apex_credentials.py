"""Unit tests for manage_apex_credentials module."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from manage_apex_credentials import (  # noqa: E402
    ALLOWED_MODULES,
    APEX_REQUIRED_FIELDS,
    APEX_SERVICE,
    REQUIRED_FIELDS,
    SERVICE,
    apex_status,
    classify_connection_error,
    connection_kwargs,
    get_profile,
    import_env_profile,
    import_module_safe,
    main,
    oracle_error_code,
    parse_env,
    probe,
    save_apex_profile,
    save_profile,
    status,
    validate,
)


class TestImportModuleSafe:
    """Test import_module_safe function."""

    @pytest.mark.unit
    def test_import_allowed_keyring(self):
        """Import keyring module (allowed)."""
        result = import_module_safe("keyring")
        assert result is not None
        assert "get_password" in dir(result)

    @pytest.mark.unit
    def test_import_allowed_oracledb(self):
        """Import oracledb module (allowed)."""
        with patch("importlib.import_module") as mock_import:
            mock_import.return_value = MagicMock()
            result = import_module_safe("oracledb")
            mock_import.assert_called_once_with("oracledb")
            assert result is not None

    @pytest.mark.unit
    def test_import_disallowed_module(self):
        """Attempt to import disallowed module."""
        with pytest.raises(SystemExit):
            import_module_safe("os")

    @pytest.mark.unit
    def test_import_disallowed_subprocess(self):
        """Attempt to import subprocess (security check)."""
        with pytest.raises(SystemExit):
            import_module_safe("subprocess")

    @pytest.mark.unit
    def test_import_missing_dependency(self):
        """Handle missing dependency."""
        with patch("importlib.import_module", side_effect=ImportError):
            with pytest.raises(SystemExit):
                import_module_safe("keyring")


class TestGetProfile:
    """Test get_profile function."""

    @pytest.mark.unit
    def test_get_profile_exists(self):
        """Get existing profile from keyring."""
        mock_keyring = MagicMock()
        profile_data = {
            "db_user": "test_user",
            "db_pass": "test_pass",  # pragma: allowlist secret
            "dsn": "test_dsn",
            "workspace_id": 1,
            "schema": "test_schema",
            "workspace_name": "test_workspace",
        }
        mock_keyring.get_password.return_value = json.dumps(profile_data)

        result = get_profile(mock_keyring, "test")

        assert result == profile_data
        mock_keyring.get_password.assert_called_once_with(SERVICE, "test")

    @pytest.mark.unit
    def test_get_profile_not_found(self):
        """Get non-existent profile."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = None

        result = get_profile(mock_keyring, "nonexistent")

        assert result is None

    @pytest.mark.unit
    def test_get_profile_empty_string(self):
        """Get profile when keyring returns empty string."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = ""

        result = get_profile(mock_keyring, "test")

        assert result is None

    @pytest.mark.unit
    def test_get_profile_invalid_json(self):
        """Malformed keyring JSON is treated as an invalid, non-throwing profile."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = "invalid json"

        assert get_profile(mock_keyring, "test") is None

    @pytest.mark.unit
    def test_get_profile_keyring_exception_is_non_throwing(self):
        mock_keyring = MagicMock()
        mock_keyring.get_password.side_effect = RuntimeError("backend unavailable")

        assert get_profile(mock_keyring, "test") is None


class TestSaveProfile:
    """Test save_profile function."""

    @pytest.mark.unit
    def test_save_valid_profile(self):
        """Save complete profile."""
        mock_keyring = MagicMock()
        profile = {
            "db_user": "user",
            "db_pass": "pwd123",  # pragma: allowlist secret
            "dsn": "dsn",
            "workspace_id": 1,
            "schema": "schema",
            "workspace_name": "workspace",
        }

        with patch("builtins.print"):
            save_profile(mock_keyring, "test", profile)

        mock_keyring.set_password.assert_called_once()
        call_args = mock_keyring.set_password.call_args
        assert call_args[0][0] == SERVICE
        assert call_args[0][1] == "test"
        assert json.loads(call_args[0][2]) == profile

    @pytest.mark.unit
    def test_save_profile_missing_field(self):
        """Reject profile missing required field."""
        mock_keyring = MagicMock()
        incomplete_profile = {"db_user": "user"}

        with pytest.raises(SystemExit):
            save_profile(mock_keyring, "test", incomplete_profile)

    @pytest.mark.unit
    def test_save_profile_all_fields_required(self):
        """Verify all required fields are checked."""
        mock_keyring = MagicMock()

        for missing_field in REQUIRED_FIELDS:
            profile = {field: f"value_{field}" for field in REQUIRED_FIELDS}
            profile[missing_field] = None

            with pytest.raises(SystemExit):
                save_profile(mock_keyring, "test", profile)

    @pytest.mark.unit
    def test_save_profile_empty_value(self):
        """Reject profile with empty string value."""
        mock_keyring = MagicMock()
        profile = {
            "db_user": "",
            "db_pass": "pwd123",  # pragma: allowlist secret
            "dsn": "dsn",
            "workspace_id": 1,
            "schema": "schema",
            "workspace_name": "workspace",
        }

        with pytest.raises(SystemExit):
            save_profile(mock_keyring, "test", profile)


class TestParseEnv:
    """Test parse_env function."""

    @pytest.mark.unit
    def test_parse_simple_env(self, tmp_path):
        """Parse simple .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("DB_USER=testuser\nDB_PWD=test123\n", encoding="utf-8")  # pragma: allowlist secret

        result = parse_env(env_file)

        assert result == {"DB_USER": "testuser", "DB_PWD": "test123"}  # pragma: allowlist secret

    @pytest.mark.unit
    def test_parse_env_with_quotes(self, tmp_path):
        """Parse .env with quoted values."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=\"value1\"\nKEY2='value2'\n", encoding="utf-8")

        result = parse_env(env_file)

        assert result["KEY1"] == "value1"
        assert result["KEY2"] == "value2"

    @pytest.mark.unit
    def test_parse_env_with_comments(self, tmp_path):
        """Parse .env ignoring comments."""
        env_file = tmp_path / ".env"
        env_file.write_text("# Comment\nKEY=value\n# Another comment\n", encoding="utf-8")

        result = parse_env(env_file)

        assert result == {"KEY": "value"}

    @pytest.mark.unit
    def test_parse_env_empty_lines(self, tmp_path):
        """Parse .env with empty lines."""
        env_file = tmp_path / ".env"
        env_file.write_text("KEY1=value1\n\nKEY2=value2\n\n", encoding="utf-8")

        result = parse_env(env_file)

        assert result == {"KEY1": "value1", "KEY2": "value2"}

    @pytest.mark.unit
    def test_parse_env_with_spaces(self, tmp_path):
        """Parse .env with spaces around keys and values."""
        env_file = tmp_path / ".env"
        env_file.write_text(" KEY = value \n", encoding="utf-8")

        result = parse_env(env_file)

        assert result == {"KEY": "value"}

    @pytest.mark.unit
    def test_parse_env_equals_in_value(self, tmp_path):
        """Parse .env with equals sign in value."""
        env_file = tmp_path / ".env"
        env_file.write_text("CONNECTION_STRING=user=admin;pass=123\n", encoding="utf-8")

        result = parse_env(env_file)

        assert result == {"CONNECTION_STRING": "user=admin;pass=123"}


class TestConnectionKwargs:
    """Test connection_kwargs function."""

    @pytest.mark.unit
    def test_build_connection_kwargs(self):
        """Build connection parameters from profile."""
        profile = {  # pragma: allowlist secret
            "db_user": "scott",
            "db_pass": "tiger",  # pragma: allowlist secret
            "dsn": "localhost:1521/orcl",
            "workspace_id": 1,
            "schema": "scott",
            "workspace_name": "internal",
        }

        result = connection_kwargs(profile)

        assert result["user"] == "scott"
        assert result["password"] == "tiger"  # pragma: allowlist secret
        assert result["dsn"] == "localhost:1521/orcl"

    @pytest.mark.unit
    def test_connection_kwargs_with_wallet(self):
        """Build connection kwargs including wallet parameters."""
        profile = {  # pragma: allowlist secret
            "db_user": "admin",
            "db_pass": "secret",  # pragma: allowlist secret
            "dsn": "mydb_high",
            "wallet_dir": "/opt/wallets/mydb",
            "wallet_pass": "walletpwd",  # pragma: allowlist secret
        }

        result = connection_kwargs(profile)

        assert result["config_dir"] == "/opt/wallets/mydb"
        assert result["wallet_location"] == "/opt/wallets/mydb"
        assert result["wallet_password"] == "walletpwd"  # pragma: allowlist secret

    @pytest.mark.unit
    def test_connection_kwargs_wallet_no_password(self):
        """Build connection kwargs with wallet dir but no wallet password."""
        profile = {  # pragma: allowlist secret
            "db_user": "admin",
            "db_pass": "secret",  # pragma: allowlist secret
            "dsn": "mydb_high",
            "wallet_dir": "/opt/wallets/mydb",
        }

        result = connection_kwargs(profile)

        assert result["config_dir"] == "/opt/wallets/mydb"
        assert result["wallet_location"] == "/opt/wallets/mydb"
        assert "wallet_password" not in result

    @pytest.mark.unit
    def test_connection_kwargs_extra_fields(self):
        """Build connection kwargs with extra fields in profile."""
        profile = {  # pragma: allowlist secret
            "db_user": "user",
            "db_pass": "pwd123",  # pragma: allowlist secret
            "dsn": "dsn",
            "workspace_id": 1,
            "schema": "schema",
            "workspace_name": "workspace",
            "extra_field": "extra_value",
        }

        result = connection_kwargs(profile)

        assert "user" in result
        assert "password" in result
        assert "dsn" in result
        assert isinstance(result, dict)


class TestIntegration:
    """Integration tests for credential flow."""

    @pytest.mark.unit
    def test_allowed_modules_whitelist(self):
        """Verify allowed modules whitelist."""
        assert "keyring" in ALLOWED_MODULES
        assert "oracledb" in ALLOWED_MODULES
        assert len(ALLOWED_MODULES) >= 2

    @pytest.mark.unit
    def test_required_fields_complete(self):
        """Verify all critical fields are required."""
        assert "db_user" in REQUIRED_FIELDS
        assert "db_pass" in REQUIRED_FIELDS
        assert "dsn" in REQUIRED_FIELDS
        assert "workspace_id" in REQUIRED_FIELDS
        assert len(REQUIRED_FIELDS) >= 5

    @pytest.mark.unit
    def test_service_constant_set(self):
        """Verify SERVICE constant is set."""
        assert SERVICE == "apex-skills"
        assert isinstance(SERVICE, str)


COMPLETE_PROFILE = {
    "db_user": "scott",
    "db_pass": "tiger",  # pragma: allowlist secret
    "dsn": "localhost:1521/orcl",
    "workspace_id": "100",
    "schema": "SCOTT",
    "workspace_name": "INTERNAL",
}


class TestStatus:
    """Test status function."""

    @pytest.mark.unit
    def test_status_profile_ready(self):
        """Status returns 0 for complete profile."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = json.dumps(COMPLETE_PROFILE)

        with patch("builtins.print"):
            result = status(mock_keyring, "test")

        assert result == 0

    @pytest.mark.unit
    def test_status_profile_missing(self):
        """Status returns 1 when profile is missing."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = None

        with patch("builtins.print"):
            result = status(mock_keyring, "test")

        assert result == 1


class TestApexProfiles:
    @pytest.mark.unit
    def test_apex_profile_is_stored_in_a_separate_service(self):
        keyring = MagicMock()
        profile = {field: f"value_{field}" for field in APEX_REQUIRED_FIELDS}
        with patch("builtins.print"):
            save_apex_profile(keyring, "test", profile)
        assert keyring.set_password.call_args[0][0] == APEX_SERVICE

    @pytest.mark.unit
    def test_apex_status_missing_does_not_use_oracle_profile(self):
        keyring = MagicMock()
        keyring.get_password.return_value = None
        with patch("builtins.print"):
            assert apex_status(keyring, "test") == 1

    @pytest.mark.unit
    def test_status_profile_incomplete(self):
        """Status returns 1 for incomplete profile."""
        mock_keyring = MagicMock()
        incomplete = {"db_user": "scott", "db_pass": "tiger"}  # pragma: allowlist secret
        mock_keyring.get_password.return_value = json.dumps(incomplete)

        with patch("builtins.print"):
            result = status(mock_keyring, "test")

        assert result == 1


class TestValidate:
    """Test validate function."""

    @pytest.mark.unit
    def test_validate_missing_profile(self):
        """Validate exits when profile missing."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = None

        with pytest.raises(SystemExit):
            validate(mock_keyring, "test")

    @pytest.mark.unit
    def test_validate_incomplete_profile(self):
        """Validate exits when profile incomplete."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = json.dumps({"db_user": "x"})

        with pytest.raises(SystemExit):
            validate(mock_keyring, "test")

    @pytest.mark.unit
    def test_validate_connection_success(self):
        """Validate returns 0 on successful connection."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = json.dumps(COMPLETE_PROFILE)

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("SCOTT",)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor

        mock_oracledb = MagicMock()
        mock_oracledb.connect.return_value = mock_conn

        with patch("manage_apex_credentials.import_module_safe", return_value=mock_oracledb):
            with patch("builtins.print"):
                result = validate(mock_keyring, "test")

        assert result == 0

    @pytest.mark.unit
    def test_validate_connection_failure(self):
        """Validate returns 1 on connection failure."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = json.dumps(COMPLETE_PROFILE)

        mock_oracledb = MagicMock()
        mock_oracledb.connect.side_effect = Exception("ORA-12154: TNS:could not resolve")

        with patch("manage_apex_credentials.import_module_safe", return_value=mock_oracledb):
            with patch("builtins.print"):
                result = validate(mock_keyring, "test")

        assert result == 1


class TestProbe:
    @pytest.mark.unit
    def test_probe_missing_profile_is_non_throwing(self):
        keyring = MagicMock()
        keyring.get_password.return_value = None
        with patch("builtins.print") as output:
            assert probe(keyring, "test") == 1
        assert "ORACLE_PROFILE_MISSING" in output.call_args[0][0]

    @pytest.mark.unit
    def test_probe_uses_only_dual_for_session_identity(self):
        source = (
            Path(__file__)
            .resolve()
            .parent.parent.joinpath("scripts", "manage_apex_credentials.py")
            .read_text(encoding="utf-8")
        )
        probe_source = source[source.index("def probe") : source.index("def main")]
        assert "from dual" in probe_source.lower()
        assert "v$instance" not in probe_source.lower()

    @pytest.mark.unit
    @pytest.mark.parametrize("code", ("01017", "28000", "28001"))
    def test_authentication_errors_are_classified(self, code):
        assert classify_connection_error(Exception(f"ORA-{code}: simulated")) == "ORACLE_AUTH_FAIL"

    @pytest.mark.unit
    @pytest.mark.parametrize("code", ("12154", "12514", "12541"))
    def test_connection_errors_are_classified(self, code):
        assert classify_connection_error(Exception(f"ORA-{code}: simulated")) == "ORACLE_CONNECTION_FAIL"

    @pytest.mark.unit
    def test_unknown_error_is_probe_failure(self):
        assert classify_connection_error(Exception("unclassified")) == "ORACLE_PROBE_FAIL"
        assert oracle_error_code(Exception("unclassified")) is None

    @pytest.mark.unit
    def test_probe_invalid_json(self):
        keyring = MagicMock()
        keyring.get_password.return_value = "not json"
        with patch("builtins.print") as output:
            assert probe(keyring, "test") == 1
        assert "ORACLE_PROFILE_INVALID" in output.call_args[0][0]

    @pytest.mark.unit
    def test_probe_keyring_exception(self):
        keyring = MagicMock()
        keyring.get_password.side_effect = RuntimeError("backend unavailable")
        with patch("builtins.print") as output:
            assert probe(keyring, "test") == 1
        assert "ORACLE_PROFILE_INVALID" in output.call_args[0][0]

    @pytest.mark.unit
    def test_probe_incomplete_profile(self):
        keyring = MagicMock()
        keyring.get_password.return_value = json.dumps({"db_user": "user"})
        with patch("builtins.print") as output:
            assert probe(keyring, "test") == 1
        assert "ORACLE_PROFILE_INCOMPLETE" in output.call_args[0][0]

    @pytest.mark.unit
    def test_probe_connection_error_does_not_expose_detail(self):
        keyring = MagicMock()
        keyring.get_password.return_value = json.dumps(COMPLETE_PROFILE)
        driver = MagicMock()
        driver.connect.side_effect = Exception("ORA-01017: secret-host")
        with patch("manage_apex_credentials.import_module_safe", return_value=driver):
            with patch("builtins.print") as output:
                assert probe(keyring, "test") == 1
        assert output.call_args[0][0] == "ORACLE_AUTH_FAIL environment=test error=ORA-01017"

    @pytest.mark.unit
    def test_probe_connection_fail_does_not_expose_detail(self):
        keyring = MagicMock()
        keyring.get_password.return_value = json.dumps(COMPLETE_PROFILE)
        driver = MagicMock()
        driver.connect.side_effect = Exception("ORA-12154: could not resolve the connect identifier")
        with patch("manage_apex_credentials.import_module_safe", return_value=driver):
            with patch("builtins.print") as output:
                assert probe(keyring, "test") == 1
        assert output.call_args[0][0] == "ORACLE_CONNECTION_FAIL environment=test error=ORA-12154"

    @pytest.mark.unit
    def test_probe_post_connection_failure_does_not_expose_detail(self):
        keyring = MagicMock()
        keyring.get_password.return_value = json.dumps(COMPLETE_PROFILE)
        cursor = MagicMock()
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=False)
        cursor.execute.side_effect = Exception("ORA-00600: internal error code")
        connection = MagicMock()
        connection.cursor.return_value = cursor
        connection.__enter__ = MagicMock(return_value=connection)
        connection.__exit__ = MagicMock(return_value=False)
        driver = MagicMock()
        driver.connect.return_value = connection
        with patch("manage_apex_credentials.import_module_safe", return_value=driver):
            with patch("builtins.print") as output:
                assert probe(keyring, "test") == 1
        assert output.call_args[0][0] == "ORACLE_PROBE_FAIL environment=test error=ORA-00600"

    @pytest.mark.unit
    def test_probe_success_uses_dual_identity_query(self):
        keyring = MagicMock()
        keyring.get_password.return_value = json.dumps(COMPLETE_PROFILE)
        cursor = MagicMock()
        cursor.fetchone.return_value = ("SCOTT", "SCOTT")
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=False)
        connection = MagicMock()
        connection.cursor.return_value = cursor
        connection.__enter__ = MagicMock(return_value=connection)
        connection.__exit__ = MagicMock(return_value=False)
        driver = MagicMock()
        driver.connect.return_value = connection
        with patch("manage_apex_credentials.import_module_safe", return_value=driver):
            with patch("builtins.print") as output:
                assert probe(keyring, "test") == 0
        observed = output.call_args[0][0]
        assert "ORACLE_CONNECTION_PASS" in observed
        assert "workspace=" not in observed
        assert "localhost" not in observed
        assert "from dual" in cursor.execute.call_args[0][0].lower()


class TestImportEnvProfile:
    """Test import_env_profile function."""

    @pytest.mark.unit
    def test_import_env_test_profile(self, tmp_path):
        """Import test profile from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DB_TESTING_USER=testuser\n"
            "DB_TESTING_PASSWORD=testpwd\n"  # pragma: allowlist secret
            "DB_TESTING_HOST=dbhost\n"
            "DB_TESTING_PORT=1521\n"
            "DB_TESTING_SID=ORCL\n",
            encoding="utf-8",
        )

        mock_keyring = MagicMock()

        with patch(
            "manage_apex_credentials.discover_apex_metadata",
            side_effect=lambda p: p.update({"workspace_id": "1", "schema": "TESTUSER", "workspace_name": "WS"}) or p,
        ):
            with patch("builtins.print"):
                import_env_profile(mock_keyring, "test", env_file)

        mock_keyring.set_password.assert_called_once()
        saved = json.loads(mock_keyring.set_password.call_args[0][2])
        assert saved["db_user"] == "testuser"
        assert saved["dsn"] == "dbhost:1521/ORCL"

    @pytest.mark.unit
    def test_import_env_with_apex_credentials(self, tmp_path):
        """Import both Oracle DB and APEX profiles from .env."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DB_TESTING_USER=testuser\n"
            "DB_TESTING_PASSWORD=testpwd\n"  # pragma: allowlist secret
            "DB_TESTING_HOST=dbhost\n"
            "DB_TESTING_PORT=1521\n"
            "DB_TESTING_SID=ORCL\n"
            "APEX_TESTING_BASE_URL=http://apex.example.com/ords/\n"
            "APEX_TESTING_WORKSPACE=MYWS\n"
            "APEX_TESTING_USER=apexadmin\n"
            "APEX_TESTING_PASSWORD=apexpwd\n",  # pragma: allowlist secret
            encoding="utf-8",
        )

        mock_keyring = MagicMock()

        with patch(
            "manage_apex_credentials.discover_apex_metadata",
            side_effect=lambda p: p.update({"workspace_id": "1", "schema": "TESTUSER", "workspace_name": "WS"}) or p,
        ):
            with patch("builtins.print"):
                import_env_profile(mock_keyring, "test", env_file)

        assert mock_keyring.set_password.call_count == 2
        oracle_call = mock_keyring.set_password.call_args_list[0]
        assert oracle_call[0][0] == SERVICE
        apex_call = mock_keyring.set_password.call_args_list[1]
        assert apex_call[0][0] == APEX_SERVICE
        apex_saved = json.loads(apex_call[0][2])
        assert apex_saved["base_url"] == "http://apex.example.com/ords"
        assert apex_saved["workspace"] == "MYWS"
        assert apex_saved["apex_user"] == "apexadmin"

    @pytest.mark.unit
    def test_import_env_apex_incomplete_is_skipped(self, tmp_path):
        """Incomplete APEX fields are skipped without error."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DB_TESTING_USER=testuser\n"
            "DB_TESTING_PASSWORD=testpwd\n"  # pragma: allowlist secret
            "DB_TESTING_HOST=dbhost\n"
            "DB_TESTING_PORT=1521\n"
            "DB_TESTING_SID=ORCL\n"
            "APEX_TESTING_BASE_URL=http://apex.example.com/ords/\n",
            encoding="utf-8",
        )

        mock_keyring = MagicMock()

        with patch(
            "manage_apex_credentials.discover_apex_metadata",
            side_effect=lambda p: p.update({"workspace_id": "1", "schema": "TESTUSER", "workspace_name": "WS"}) or p,
        ):
            with patch("builtins.print") as output:
                import_env_profile(mock_keyring, "test", env_file)

        mock_keyring.set_password.assert_called_once()
        printed = [call[0][0] for call in output.call_args_list]
        assert any("APEX_PROFILE_SKIPPED" in line for line in printed)

    @pytest.mark.unit
    def test_import_env_production_apex(self, tmp_path):
        """Production APEX uses APEX_PRODUCTION_ prefix."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "DB_PRODUCTION_USER=produser\n"
            "DB_PRODUCTION_PASSWORD=prodpwd\n"  # pragma: allowlist secret
            "DB_PRODUCTION_HOST=prodhost\n"
            "DB_PRODUCTION_PORT=1521\n"
            "DB_PRODUCTION_SID=PROD\n"
            "APEX_PRODUCTION_BASE_URL=http://prod.example.com/apex\n"
            "APEX_PRODUCTION_WORKSPACE=PRODWS\n"
            "APEX_PRODUCTION_USER=prodapex\n"  # pragma: allowlist secret
            "APEX_PRODUCTION_PASSWORD=prodapexpwd\n",  # pragma: allowlist secret
            encoding="utf-8",
        )

        mock_keyring = MagicMock()

        with patch(
            "manage_apex_credentials.discover_apex_metadata",
            side_effect=lambda p: p.update({"workspace_id": "2", "schema": "PRODUSER", "workspace_name": "PWS"}) or p,
        ):
            with patch("builtins.print"):
                import_env_profile(mock_keyring, "production", env_file)

        assert mock_keyring.set_password.call_count == 2
        apex_call = mock_keyring.set_password.call_args_list[1]
        assert apex_call[0][0] == APEX_SERVICE
        assert apex_call[0][1] == "production"

    @pytest.mark.unit
    def test_import_env_missing_values(self, tmp_path):
        """Import fails when required .env values are missing."""
        env_file = tmp_path / ".env"
        env_file.write_text("DB_TESTING_USER=testuser\n", encoding="utf-8")

        mock_keyring = MagicMock()

        with pytest.raises(SystemExit):
            import_env_profile(mock_keyring, "test", env_file)


class TestMain:
    """Test main entry point."""

    @pytest.mark.unit
    def test_main_status_action(self):
        """Main dispatches status action."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = json.dumps(COMPLETE_PROFILE)

        with patch("manage_apex_credentials.import_module_safe", return_value=mock_keyring):
            with patch("sys.argv", ["prog", "status", "--environment", "test"]):
                with patch("builtins.print"):
                    result = main()

        assert result == 0

    @pytest.mark.unit
    def test_main_validate_action(self):
        """Main dispatches validate action."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = None

        with patch("manage_apex_credentials.import_module_safe", return_value=mock_keyring):
            with patch("sys.argv", ["prog", "validate", "--environment", "test"]):
                with pytest.raises(SystemExit):
                    main()
