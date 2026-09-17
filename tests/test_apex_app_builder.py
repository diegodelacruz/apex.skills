from unittest.mock import MagicMock

from scripts.apex_app_builder import preflight


def test_missing_apex_profile_requires_configuration():
    keyring = MagicMock()
    keyring.get_password.return_value = None
    result = preflight(keyring, "test")
    assert result.code == "CONFIGURATION_REQUIRED"
