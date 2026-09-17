"""Unit tests for apex_rest_client module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from apex_rest_client import ApexRestClient


class TestApexRestClientInit:
    """Test client initialization."""

    @pytest.mark.unit
    def test_init_with_required_params(self):
        """Initialize client with required parameters."""
        client = ApexRestClient("https://apex.example.com", "admin", "password")
        assert client.base_url == "https://apex.example.com"
        assert client.username == "admin"
        assert client.password == "password"  # pragma: allowlist secret

    @pytest.mark.unit
    def test_init_trims_trailing_slash(self):
        """Initialize trims trailing slash from URL."""
        client = ApexRestClient("https://apex.example.com/", "admin", "pass")
        assert client.base_url == "https://apex.example.com"

    @pytest.mark.unit
    def test_init_with_custom_timeout(self):
        """Initialize with custom timeout."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass", timeout=60)
        assert client.timeout == 60


class TestAuthentication:
    """Test authentication methods."""

    @pytest.mark.unit
    def test_authenticate_creates_token(self):
        """Authentication creates access token."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        token = client._authenticate()
        assert token is not None
        assert token.startswith("token_")

    @pytest.mark.unit
    def test_authenticate_caches_token(self):
        """Authentication caches token."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        token1 = client._authenticate()
        token2 = client._authenticate()
        assert token1 == token2

    @pytest.mark.unit
    def test_authenticate_logs_operation(self):
        """Authentication logs to audit trail."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        client._authenticate()
        assert len(client.get_audit_log()) > 0


class TestCRUDOperations:
    """Test CRUD operations."""

    @pytest.mark.unit
    def test_create_application(self):
        """Create application."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        app_id = client.create_application({"name": "Test App"})
        assert app_id is not None
        assert isinstance(app_id, str)

    @pytest.mark.unit
    def test_get_application(self):
        """Get application metadata."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        app = client.get_application("100")
        assert app["id"] == "100"
        assert "name" in app

    @pytest.mark.unit
    def test_update_application(self):
        """Update application configuration."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        client.update_application("100", {"name": "Updated"})
        assert len(client.get_audit_log()) > 0

    @pytest.mark.unit
    def test_delete_application(self):
        """Delete application."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        client.delete_application("100")
        assert len(client.get_audit_log()) > 0


class TestExportImport:
    """Test export/import operations."""

    @pytest.mark.unit
    def test_export_application(self):
        """Export application as ZIP."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        zip_data = client.export_application("100")
        assert isinstance(zip_data, bytes)
        assert zip_data.startswith(b"PK")  # ZIP signature

    @pytest.mark.unit
    def test_import_application(self):
        """Import application from ZIP."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        app_id = client.import_application(b"PK\x03\x04")
        assert app_id is not None


class TestDeployment:
    """Test deployment operations."""

    @pytest.mark.unit
    def test_deploy_to_dev_environment(self):
        """Deploy to development environment."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        result = client.deploy_to_environment("100", "development")
        assert result is True

    @pytest.mark.unit
    def test_deploy_to_test_environment(self):
        """Deploy to test environment."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        result = client.deploy_to_environment("100", "test")
        assert result is True

    @pytest.mark.unit
    def test_deploy_to_prod_environment(self):
        """Deploy to production environment."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        result = client.deploy_to_environment("100", "production")
        assert result is True

    @pytest.mark.unit
    def test_deployment_logs_operations(self):
        """Deployment logs all operations."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        client.deploy_to_environment("100", "test")
        logs = client.get_audit_log()
        assert len(logs) > 3  # Auth + validate + export + import


class TestSynchronization:
    """Test environment synchronization."""

    @pytest.mark.unit
    def test_sync_dev_to_test(self):
        """Synchronize from dev to test."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        result = client.sync_between_environments("100", "development", "test")
        assert result["status"] == "success"

    @pytest.mark.unit
    def test_sync_test_to_prod(self):
        """Synchronize from test to production."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        result = client.sync_between_environments("100", "test", "production")
        assert "changes_merged" in result

    @pytest.mark.unit
    def test_sync_reports_conflicts(self):
        """Sync reports any conflicts."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        result = client.sync_between_environments("100", "dev", "prod")
        assert "conflicts" in result

    @pytest.mark.unit
    def test_sync_logs_operations(self):
        """Sync logs all operations."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        client.sync_between_environments("100", "dev", "test")
        logs = client.get_audit_log()
        assert any("diff" in log for log in logs)


class TestValidation:
    """Test validation operations."""

    @pytest.mark.unit
    def test_validate_app_status(self):
        """Validate application health."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        status = client.validate_app_status("100")
        assert status["status"] == "healthy"

    @pytest.mark.unit
    def test_validate_returns_metadata(self):
        """Validate returns health metadata."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        status = client.validate_app_status("100")
        assert "last_deployment" in status
        assert "errors" in status


class TestAuditLog:
    """Test audit logging."""

    @pytest.mark.unit
    def test_get_audit_log(self):
        """Get audit log."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        client.get_application("100")
        logs = client.get_audit_log()
        assert len(logs) > 0

    @pytest.mark.unit
    def test_audit_log_immutability(self):
        """Audit log returned as copy."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        client.create_application({})
        logs1 = client.get_audit_log()
        logs2 = client.get_audit_log()
        assert logs1 == logs2
        assert logs1 is not logs2

    @pytest.mark.unit
    def test_clear_audit_log(self):
        """Clear audit log."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")
        client.create_application({})
        assert len(client.get_audit_log()) > 0
        client.clear_audit_log()
        assert len(client.get_audit_log()) == 0


class TestRetryLogic:
    """Test retry with backoff."""

    @pytest.mark.unit
    def test_retry_succeeds_immediately(self):
        """Retry succeeds on first attempt."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")

        def success_func():
            return "success"

        result = client._retry_with_backoff(success_func)
        assert result == "success"

    @pytest.mark.unit
    def test_retry_raises_after_max_attempts(self):
        """Retry raises after max attempts."""
        client = ApexRestClient("https://apex.example.com", "admin", "pass")

        def always_fails():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            client._retry_with_backoff(always_fails, max_retries=2)
