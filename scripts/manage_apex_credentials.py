#!/usr/bin/env python3
"""Store, import, and validate secure APEX environment profiles."""
import argparse
import getpass
import importlib
import json
import sys
from pathlib import Path

SERVICE = "apex-skills"
REQUIRED_FIELDS = ("db_user", "db_pass", "dsn", "workspace_id", "schema", "workspace_name")
ALLOWED_MODULES = {"keyring", "oracledb"}


def import_module_safe(name):
	"""Safely import a module from the allowed list.

	Args:
		name: Module name to import (must be in ALLOWED_MODULES)

	Returns:
		The imported module object

	Raises:
		SystemExit: If module not in whitelist or import fails
	"""
	if name not in ALLOWED_MODULES:
		raise SystemExit(f"Module '{name}' is not in the allowed list: {', '.join(ALLOWED_MODULES)}")

	try:
		return importlib.import_module(name)
	except ImportError as error:
		raise SystemExit(f"Missing dependency: {name}. Install requirements.txt first.") from error


def get_profile(keyring, environment):
	raw = keyring.get_password(SERVICE, environment)
	return json.loads(raw) if raw else None


def save_profile(keyring, environment, profile):
	missing = [field for field in REQUIRED_FIELDS if not profile.get(field)]
	if missing:
		raise SystemExit("Profile is incomplete; nothing was saved. Missing: " + ", ".join(missing))
	keyring.set_password(SERVICE, environment, json.dumps(profile))
	print(f"PROFILE_SAVED environment={environment} service={SERVICE}")


def parse_env(path):
	values = {}
	for raw_line in path.read_text(encoding="utf-8").splitlines():
		line = raw_line.strip()
		if line and not line.startswith("#") and "=" in line:
			key, value = line.split("=", 1)
			values[key.strip()] = value.strip().strip('"').strip("'")
	return values


def connection_kwargs(profile):
	kwargs = {"user": profile["db_user"], "password": profile["db_pass"], "dsn": profile["dsn"]}
	if profile.get("wallet_dir"):
		kwargs.update(config_dir=profile["wallet_dir"], wallet_location=profile["wallet_dir"])
		if profile.get("wallet_pass"):
			kwargs["wallet_password"] = profile["wallet_pass"]
	return kwargs


def discover_apex_metadata(profile):
	with import_module_safe("oracledb").connect(**connection_kwargs(profile)) as connection:
		with connection.cursor() as cursor:
			cursor.execute("select workspace_id from apex_workspace_schemas where schema = sys_context('userenv', 'current_schema') order by workspace_id")
			workspace_ids = [str(row[0]) for row in cursor.fetchall()]
			workspace = None
			if len(workspace_ids) == 1:
				cursor.execute("select workspace from apex_workspaces where workspace_id = :workspace_id", [workspace_ids[0]])
				workspace = cursor.fetchone()
				if workspace:
					profile["workspace_id"] = workspace_ids[0]
					profile["workspace_name"] = str(workspace[0])
					cursor.execute("select sys_context('userenv', 'current_schema') from dual")
					profile["schema"] = cursor.fetchone()[0]
					return profile
			cursor.execute(
				"select owner, workspace, workspace_id from ("
				"select owner, workspace, workspace_id, count(*) application_count "
				"from apex_applications "
				"where workspace <> 'INTERNAL' and workspace not like 'COM.ORACLE.%' "
				"group by owner, workspace, workspace_id "
				"order by count(*) desc, workspace) where rownum = 1"
			)
			workspace = cursor.fetchone()
			if not workspace:
				raise SystemExit("No functional APEX workspace was found. No profile was saved.")
	profile["schema"], profile["workspace_name"], workspace_id = workspace
	profile["workspace_id"] = str(workspace_id)
	return profile


def set_profile(keyring, environment):
	profile = {"db_user": input("Oracle user: ").strip(), "db_pass": getpass.getpass("Oracle password: "), "dsn": input("Oracle DSN: ").strip()}
	save_profile(keyring, environment, discover_apex_metadata(profile))


def import_env_profile(keyring, environment, env_file):
	values = parse_env(env_file)
	prefix = "DB_TESTING" if environment == "test" else "DB_PRODUCTION"
	needed = tuple(f"{prefix}_{field}" for field in ("USER", "PASSWORD", "HOST", "PORT", "SID"))
	missing = [name for name in needed if not values.get(name)]
	if missing:
		raise SystemExit("Missing .env values: " + ", ".join(missing))
	profile = {"db_user": values[f"{prefix}_USER"], "db_pass": values[f"{prefix}_PASSWORD"], "dsn": "{}:{}/{}".format(values[f"{prefix}_HOST"], values[f"{prefix}_PORT"], values[f"{prefix}_SID"])}
	save_profile(keyring, environment, discover_apex_metadata(profile))
	print(f"PROFILE_IMPORTED environment={environment} source={env_file.name} mode=direct-connection")


def status(keyring, environment):
	profile = get_profile(keyring, environment)
	if not profile:
		print(f"PROFILE_MISSING environment={environment}")
		return 1
	missing = [field for field in REQUIRED_FIELDS if not profile.get(field)]
	print(f"PROFILE_{'READY' if not missing else 'INCOMPLETE'} environment={environment}" + (f" missing={','.join(missing)}" if missing else ""))
	return int(bool(missing))


def validate(keyring, environment):
	profile = get_profile(keyring, environment)
	if not profile or any(not profile.get(field) for field in REQUIRED_FIELDS):
		raise SystemExit("Profile is missing or incomplete.")
	try:
		with import_module_safe("oracledb").connect(**connection_kwargs(profile)) as connection:
			with connection.cursor() as cursor:
				cursor.execute("select sys_context('userenv', 'current_schema') from dual")
				cursor.fetchone()
	except Exception as error:
		print(f"PROFILE_VALIDATION_FAIL environment={environment} error={type(error).__name__}", file=sys.stderr)
		return 1
	print(f"PROFILE_VALIDATION_PASS environment={environment} mode=read-only")
	return 0


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("action", choices=("set", "import-env", "status", "validate"))
	parser.add_argument("--environment", required=True, choices=("test", "production"))
	parser.add_argument("--env-file", type=Path, default=Path(__file__).resolve().parent.parent / ".env")
	args = parser.parse_args()
	keyring = import_module_safe("keyring")
	if args.action == "set":
		set_profile(keyring, args.environment)
	elif args.action == "import-env":
		import_env_profile(keyring, args.environment, args.env_file)
	elif args.action == "status":
		return status(keyring, args.environment)
	else:
		return validate(keyring, args.environment)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
