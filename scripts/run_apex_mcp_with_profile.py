#!/usr/bin/env python3
"""Start apex-mcp with a TEST or production profile held in the OS keyring."""

import argparse
import json
import os
import sys


SERVICE = "apex-skills"
REQUIRED_MAPPING = {
	"ORACLE_DB_USER": "db_user",
	"ORACLE_DB_PASS": "db_pass",
	"ORACLE_DSN": "dsn",
	"APEX_WORKSPACE_ID": "workspace_id",
	"APEX_SCHEMA": "schema",
	"APEX_WORKSPACE_NAME": "workspace_name",
}
OPTIONAL_MAPPING = {
	"ORACLE_WALLET_DIR": "wallet_dir",
	"ORACLE_WALLET_PASSWORD": "wallet_pass",
}


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--environment", required=True, choices=("test", "production"))
	parser.add_argument("mcp_args", nargs=argparse.REMAINDER)
	args = parser.parse_args()

	try:
		import keyring
	except ImportError as error:
		raise SystemExit(
			"Missing dependency: keyring. Install requirements.txt in the shared skills environment."
		) from error

	raw_profile = keyring.get_password(SERVICE, args.environment)
	if not raw_profile:
		raise SystemExit(f"Missing secure profile: {args.environment}. Import or set it first.")
	try:
		profile = json.loads(raw_profile)
	except json.JSONDecodeError as error:
		raise SystemExit(f"Invalid secure profile: {args.environment}. Import or set it again.") from error

	missing = [
		environment_name
		for environment_name, profile_name in REQUIRED_MAPPING.items()
		if not profile.get(profile_name)
	]
	if missing:
		raise SystemExit("Incomplete secure profile; missing mapped values: " + ", ".join(missing))

	environment = os.environ.copy()
	for environment_name, profile_name in {**REQUIRED_MAPPING, **OPTIONAL_MAPPING}.items():
		if profile.get(profile_name):
			environment[environment_name] = str(profile[profile_name])
	os.execvpe(sys.executable, [sys.executable, "-m", "apex_mcp", *args.mcp_args], environment)


if __name__ == "__main__":
	main()
