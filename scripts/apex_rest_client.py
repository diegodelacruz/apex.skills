#!/usr/bin/env python3
"""Oracle APEX REST client using SQLcl backend.

Provides backward compatibility while using official SQLcl for operations.
All methods delegate to ApexSQLclClient for reliability and official support.
"""

import logging
from typing import Any, Dict

from apex_sqlcl_client import ApexSQLclClient

logger = logging.getLogger(__name__)


class ApexRestClient:
    """APEX REST client facade using SQLcl backend.

    Maintains backward compatibility while delegating to ApexSQLclClient
    which uses official Oracle SQLcl for reliable operations.
    """

    def __init__(self, base_url: str, username: str, password: str, timeout: int = 30):
        """Initialize APEX REST client (SQLcl-backed).

        Args:
            base_url: APEX instance base URL
            username: APEX workspace admin username
            password: APEX workspace admin password (used in db_connection_string)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout

        # Initialize SQLcl client with connection string
        db_connection_string = f"{username}/{password}"
        self._sqlcl_client = ApexSQLclClient(
            db_connection_string=db_connection_string,
            apex_instance_url=base_url,
            timeout=timeout,
        )

        logger.info(f"ApexRestClient initialized with SQLcl backend: {self._sqlcl_client}")

    def export_application(self, app_id: str) -> bytes:
        """Export application as ZIP file.

        Args:
            app_id: Application ID

        Returns:
            ZIP file bytes
        """
        import tempfile

        app_id_int = int(app_id) if isinstance(app_id, str) else app_id
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
            output_file = f.name

        success = self._sqlcl_client.export_application(app_id_int, output_file)
        if success:
            with open(output_file, "rb") as f:
                return f.read()
        return b""

    def import_application(self, zip_data: bytes) -> str:
        """Import application from ZIP file.

        Args:
            zip_data: ZIP file bytes

        Returns:
            Imported application ID
        """
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
            f.write(zip_data)
            zip_file = f.name

        app_id = self._sqlcl_client.import_application(zip_file)
        return str(app_id) if app_id else "0"

    def deploy_to_environment(self, app_id: str, target_env: str) -> bool:
        """Deploy application to target environment.

        Args:
            app_id: Application ID
            target_env: Target environment (dev, test, prod)

        Returns:
            True if deployment successful
        """
        app_id_int = int(app_id) if isinstance(app_id, str) else app_id
        return self._sqlcl_client.deploy_to_environment(app_id_int, target_env)

    def sync_between_environments(self, app_id: str, source_env: str, target_env: str) -> Dict[str, Any]:
        """Synchronize application between environments.

        Args:
            app_id: Application ID
            source_env: Source environment
            target_env: Target environment

        Returns:
            Sync result with status and changes
        """
        app_id_int = int(app_id) if isinstance(app_id, str) else app_id
        return self._sqlcl_client.sync_between_environments(app_id_int, source_env, target_env)

    def validate_app_status(self, app_id: str) -> Dict[str, Any]:
        """Validate application health status.

        Args:
            app_id: Application ID

        Returns:
            Health status dictionary
        """
        app_id_int = int(app_id) if isinstance(app_id, str) else app_id
        return self._sqlcl_client.validate_app_status(app_id_int)

    def get_audit_log(self) -> list:
        """Get operation audit log.

        Returns:
            List of logged operations
        """
        return self._sqlcl_client.get_audit_log()

    def clear_audit_log(self) -> None:
        """Clear operation audit log."""
        self._sqlcl_client.clear_audit_log()

    def __repr__(self) -> str:
        """String representation."""
        return f"ApexRestClient(url={self.base_url}, sqlcl_backend=True)"
