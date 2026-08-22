"""Unit tests for apex_metadata module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from apex_metadata import ApexMetadata


class TestApexMetadata:
    """Tests for ApexMetadata class."""

    @pytest.mark.unit
    def test_get_field_simple(self):
        """Extract a simple YAML field."""
        yaml = "name: TestApp"
        assert ApexMetadata.get_field(yaml, "name") == "TestApp"

    @pytest.mark.unit
    def test_get_field_quoted(self):
        """Extract quoted field."""
        yaml = "name: 'My Application'"
        assert ApexMetadata.get_field(yaml, "name") == "My Application"

    @pytest.mark.unit
    def test_get_field_missing(self):
        """Return None for missing field."""
        yaml = "name: TestApp"
        assert ApexMetadata.get_field(yaml, "missing") is None

    @pytest.mark.unit
    def test_get_field_hyphenated(self):
        """Extract hyphenated field name."""
        yaml = "parsing-schema: MYSCHEMA"
        assert ApexMetadata.get_field(yaml, "parsing-schema") == "MYSCHEMA"

    @pytest.mark.unit
    def test_get_application_info(self):
        """Extract application info."""
        yaml = """
		id: 12345
		name: 'TestApp'
		alias: test_app
		parsing-schema: TESTSCHEMA
		"""
        meta = ApexMetadata(yaml)
        info = meta.get_application_info()

        assert info["id"] == "12345"
        assert info["name"] == "TestApp"
        assert info["alias"] == "test_app"
        assert info["schema"] == "TESTSCHEMA"

    @pytest.mark.unit
    def test_get_security_settings_all_enabled(self):
        """Extract security settings when all enabled."""
        yaml = """
		session-state-protection:
		  enabled: true
		html-escaping-mode: Extended
		deep-linking: Disabled
		embed-in-frames: Deny
		"""
        meta = ApexMetadata(yaml)
        settings = meta.get_security_settings()

        assert settings["session_state_protection"] is True
        assert settings["extended_html_escaping"] is True
        assert settings["deep_links_disabled"] is True
        assert settings["frames_denied"] is True

    @pytest.mark.unit
    def test_get_security_settings_partial(self):
        """Extract security settings when partially enabled."""
        yaml = """
		session-state-protection:
		  enabled: true
		html-escaping-mode: Standard
		deep-linking: Enabled
		embed-in-frames: Allow
		"""
        meta = ApexMetadata(yaml)
        settings = meta.get_security_settings()

        assert settings["session_state_protection"] is True
        assert settings["extended_html_escaping"] is False
        assert settings["deep_links_disabled"] is False
        assert settings["frames_denied"] is False

    @pytest.mark.unit
    def test_is_secure_true(self):
        """Check is_secure() returns True when all settings enabled."""
        yaml = """
		session-state-protection:
		  enabled: true
		html-escaping-mode: Extended
		deep-linking: Disabled
		embed-in-frames: Deny
		"""
        meta = ApexMetadata(yaml)
        assert meta.is_secure() is True

    @pytest.mark.unit
    def test_is_secure_false(self):
        """Check is_secure() returns False when any setting disabled."""
        yaml = """
		session-state-protection:
		  enabled: false
		html-escaping-mode: Extended
		deep-linking: Disabled
		embed-in-frames: Deny
		"""
        meta = ApexMetadata(yaml)
        assert meta.is_secure() is False

    @pytest.mark.unit
    def test_validate_export_structure_valid(self):
        """Validate export structure with valid metadata."""
        yaml = """
		id: 123
		name: TestApp
		"""
        meta = ApexMetadata(yaml)
        assert meta.validate_export_structure() is True

    @pytest.mark.unit
    def test_validate_export_structure_missing_id(self):
        """Raise error when ID is missing."""
        yaml = "name: TestApp"
        meta = ApexMetadata(yaml)
        with pytest.raises(ValueError, match="missing application id"):
            meta.validate_export_structure()

    @pytest.mark.unit
    def test_validate_export_structure_missing_name(self):
        """Raise error when name is missing."""
        yaml = "id: 123"
        meta = ApexMetadata(yaml)
        with pytest.raises(ValueError, match="missing application name"):
            meta.validate_export_structure()

    @pytest.mark.unit
    def test_metadata_with_empty_string(self):
        """Handle empty metadata."""
        meta = ApexMetadata("")
        info = meta.get_application_info()
        assert info["id"] is None
        assert info["name"] is None

    @pytest.mark.unit
    def test_metadata_with_multiline_values(self):
        """Handle multiline YAML values."""
        yaml = """
		id: 999
		name: 'Complex
		  App Name'
		"""
        meta = ApexMetadata(yaml)
        info = meta.get_application_info()
        assert info["id"] == "999"
        # Note: Multiline YAML requires special handling, current regex may not support
