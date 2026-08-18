#!/usr/bin/env python3
"""Store and validate APEX environment profiles in the OS secure keyring."""
import argparse, getpass, json, sys

SERVICE='apex-skills'
FIELDS=('db_user','db_pass','dsn','wallet_dir','wallet_pass','workspace_id','schema','workspace_name')

def keyring_module():
	try:
		import keyring
		return keyring
	except ImportError:
		print('Missing dependency: keyring. Install requirements.txt first.',file=sys.stderr)
		raise SystemExit(2)

def get_profile(keyring, environment):
	raw=keyring.get_password(SERVICE, environment)
	return json.loads(raw) if raw else None

def set_profile(keyring, environment):
	profile={
		'db_user': input('Oracle user: ').strip(),
		'db_pass': getpass.getpass('Oracle password: '),
		'dsn': input('Oracle DSN: ').strip(),
		'wallet_dir': input('Wallet directory: ').strip(),
		'wallet_pass': getpass.getpass('Wallet password: '),
		'workspace_id': input('APEX workspace ID: ').strip(),
		'schema': input('APEX parsing schema: ').strip(),
		'workspace_name': input('APEX workspace name: ').strip(),
	}
	if not all(profile.values()): raise SystemExit('All profile fields are required; nothing was saved.')
	keyring.set_password(SERVICE, environment, json.dumps(profile))
	print(f'PROFILE_SAVED environment={environment} service={SERVICE}')

def status(keyring, environment):
	profile=get_profile(keyring,environment)
	if not profile: print(f'PROFILE_MISSING environment={environment}'); return 1
	missing=[field for field in FIELDS if not profile.get(field)]
	print(f"PROFILE_{'READY' if not missing else 'INCOMPLETE'} environment={environment}" + (f" missing={','.join(missing)}" if missing else ''))
	return int(bool(missing))

def validate(keyring, environment):
	profile=get_profile(keyring,environment)
	if not profile or any(not profile.get(field) for field in FIELDS): raise SystemExit('Profile is missing or incomplete.')
	try: import oracledb
	except ImportError: raise SystemExit('Missing dependency: oracledb. Install requirements.txt first.')
	try:
		with oracledb.connect(user=profile['db_user'],password=profile['db_pass'],dsn=profile['dsn'],config_dir=profile['wallet_dir'],wallet_location=profile['wallet_dir'],wallet_password=profile['wallet_pass']) as connection:
			with connection.cursor() as cursor:
				cursor.execute("select sys_context('userenv','current_schema') from dual")
				cursor.fetchone()
	except Exception as exc:
		print(f'PROFILE_VALIDATION_FAIL environment={environment} error={type(exc).__name__}',file=sys.stderr); return 1
	print(f'PROFILE_VALIDATION_PASS environment={environment} mode=read-only')
	return 0

def main():
	p=argparse.ArgumentParser(); p.add_argument('action',choices=('set','status','validate')); p.add_argument('--environment',required=True,choices=('test','production')); a=p.parse_args(); keyring=keyring_module()
	if a.action=='set': set_profile(keyring,a.environment); return 0
	if a.action=='status': return status(keyring,a.environment)
	return validate(keyring,a.environment)
if __name__=='__main__': raise SystemExit(main())
