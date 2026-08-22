#!/usr/bin/env python3
"""Validate Oracle APEX export ZIP structure, metadata, and content integrity."""

import hashlib
import re
import sys
import zipfile
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))

from path_setup import setup_skills_path
setup_skills_path(__file__)

from apex_export_utilities import extract_apex_export_metadata, list_export_pages
from apex_metadata import ApexMetadata
from cli_utils import CLIParser, exit_with_error, exit_with_success


def main():
	parser = CLIParser("Validate Oracle APEX export ZIP structure and security settings")
	parser.add_argument("export_zip", type=Path, help="Path to APEX export ZIP file")
	args = parser.parse_args()

	try:
		root, metadata = extract_apex_export_metadata(args.export_zip)

		with zipfile.ZipFile(args.export_zip) as z:
			names = z.namelist()
			readable_pages = list_export_pages(z, root, "readable")
			sql_pages = list_export_pages(z, root, "sql")
			has_install_sql = f"{root}/install.sql" in names

		apex_meta = ApexMetadata(metadata)
		security_settings = apex_meta.get_security_settings()

		checks = [
			has_install_sql,
			len(readable_pages) > 0,
			len(sql_pages) > 0,
			security_settings.get("session_state_protection", False),
			security_settings.get("extended_html_escaping", False),
			"theme: Universal Theme # 42" in metadata,
		]

		if not all(checks):
			missing = []
			if not has_install_sql:
				missing.append("install.sql")
			if len(readable_pages) == 0:
				missing.append("readable pages")
			if len(sql_pages) == 0:
				missing.append("SQL pages")
			if not security_settings.get("session_state_protection"):
				missing.append("session-state-protection")
			if not security_settings.get("extended_html_escaping"):
				missing.append("extended HTML escaping")
			if "theme: Universal Theme # 42" not in metadata:
				missing.append("Theme: Universal Theme # 42")

			raise ValueError(f"missing: {', '.join(missing)}")

	except (OSError, ValueError, zipfile.BadZipFile) as err:
		exit_with_error(str(err), "STATIC_FAIL")

	sha256_hash = hashlib.sha256(args.export_zip.read_bytes()).hexdigest()
	exit_with_success(f"{args.export_zip.name} | sha256={sha256_hash}", "STATIC_PASS")


if __name__ == "__main__":
	main()
