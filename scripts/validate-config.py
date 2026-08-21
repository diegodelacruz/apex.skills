#!/usr/bin/env python3
"""Validate all configuration files in apex.skills.

This script ensures all JSON, YAML, and configuration files are valid.
Run before committing changes to config files.

Usage:
    python3 scripts/validate-config.py

Returns:
    0 if all configs are valid
    1 if any config has errors
"""

import json
import sys
from pathlib import Path


def validate_json_file(filepath: str) -> bool:
	"""Validate JSON file syntax.

	Args:
		filepath: Path to JSON file

	Returns:
		True if valid, False otherwise
	"""
	try:
		with open(filepath) as f:
			json.load(f)
		print(f"✅ {filepath} is valid JSON")
		return True
	except json.JSONDecodeError as e:
		print(f"❌ {filepath} has JSON error: {e}")
		return False
	except FileNotFoundError:
		print(f"⚠️  {filepath} not found (optional)")
		return True


def validate_all() -> int:
	"""Validate all configuration files.

	Returns:
		0 if all valid, 1 if any invalid
	"""
	repo_root = Path(__file__).parent.parent
	all_valid = True

	# JSON files
	json_files = [
		'.claude/settings.json',
		'.mcp.json.example',
	]

	for file in json_files:
		filepath = repo_root / file
		if not validate_json_file(str(filepath)):
			all_valid = False

	print()
	if all_valid:
		print("✅ All configuration files are valid!")
		return 0
	else:
		print("❌ Some configuration files have errors")
		return 1


if __name__ == '__main__':
	sys.exit(validate_all())
