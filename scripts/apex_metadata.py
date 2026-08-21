#!/usr/bin/env python3
"""Shared metadata extraction utilities for Oracle APEX exports."""

import re
from typing import Optional, Dict


class ApexMetadata:
	"""Helper class for extracting APEX metadata from YAML."""

	# Standard APEX metadata fields
	STANDARD_FIELDS = ("id", "name", "alias", "parsing-schema")

	# Security-related fields
	SECURITY_FIELDS = {
		"session_state_protection": r"session-state-protection:\s*\n\s+enabled:\s*true",
		"extended_html_escaping": r"html-escaping-mode:\s*Extended",
		"deep_links_disabled": r"deep-linking:\s*Disabled",
		"frames_denied": r"embed-in-frames:\s*Deny",
	}

	def __init__(self, metadata_yaml: str):
		"""Initialize with APEX metadata YAML text.

		Args:
			metadata_yaml: Raw YAML content from APEX export
		"""
		self.metadata_yaml = metadata_yaml

	@staticmethod
	def get_field(yaml_text: Optional[str], field_name: Optional[str]) -> Optional[str]:
		"""Extract a field value from YAML text using regex.

		This is the canonical APEX field extraction function, consolidating
		previous lookup() and field() implementations.

		Args:
			yaml_text: Raw YAML text content
			field_name: Name of the field to extract (e.g., 'id', 'name', 'parsing-schema')

		Returns:
			The field value with quotes stripped, or None if field not found.

		Examples:
			>>> ApexMetadata.get_field("name: 'My App'", "name")
			'My App'
			>>> ApexMetadata.get_field("id: 12345", "id")
			'12345'
			>>> ApexMetadata.get_field("unknown", "missing")
			None
		"""
		if not yaml_text or not field_name:
			return None

		try:
			match = re.search(
				rf"^\s*{re.escape(field_name)}:\s*(.+?)\s*$",
				yaml_text,
				re.MULTILINE,
			)
			return match.group(1).strip(" '\"") if match else None
		except (TypeError, AttributeError):
			return None

	def get_application_info(self) -> Dict[str, Optional[str]]:
		"""Extract standard application metadata.

		Returns:
			Dictionary with keys: id, name, alias, schema
		"""
		return {
			"id": self.get_field(self.metadata_yaml, "id"),
			"name": self.get_field(self.metadata_yaml, "name"),
			"alias": self.get_field(self.metadata_yaml, "alias"),
			"schema": self.get_field(self.metadata_yaml, "parsing-schema"),
		}

	def get_security_settings(self) -> Dict[str, bool]:
		"""Extract security-related settings.

		Returns:
			Dictionary with security flags: session_state_protection,
			extended_html_escaping, deep_links_disabled, frames_denied
		"""
		return {
			key: bool(re.search(pattern, self.metadata_yaml))
			for key, pattern in self.SECURITY_FIELDS.items()
		}

	def is_secure(self) -> bool:
		"""Check if application has all recommended security settings enabled.

		Returns:
			True if all security checks pass, False otherwise
		"""
		settings = self.get_security_settings()
		return all(settings.values())

	def validate_export_structure(self) -> bool:
		"""Validate that metadata contains required security settings.

		Returns:
			True if export structure is valid, False otherwise

		Raises:
			ValueError: If required fields are missing
		"""
		info = self.get_application_info()
		if not info.get("id"):
			raise ValueError("missing application id in metadata")
		if not info.get("name"):
			raise ValueError("missing application name in metadata")

		return True
