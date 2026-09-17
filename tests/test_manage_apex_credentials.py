"""Unit tests for manage_apex_credentials module."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from manage_apex_credentials import (
    ALLOWED_MODULES,
    REQUIRED_FIELDS,
    SERVICE,
    connection_kwargs,
    get_profile,
    import_module_safe,
    parse_env,
    save_profile,
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
        """Handle invalid JSON in keyring."""
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = "invalid json"

        with pytest.raises(json.JSONDecodeError):
            get_profile(mock_keyring, "test")


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
        # Extra fields should not cause errors
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
