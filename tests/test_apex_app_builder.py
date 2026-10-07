from scripts.apex_app_builder import preflight


def test_missing_apex_env_profile_requires_configuration(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_TESTING_USER=user\n", encoding="utf-8")

    result = preflight("test", env_file)

    assert result.code == "CONFIGURATION_REQUIRED"
    assert "repository .env" in result.reason
