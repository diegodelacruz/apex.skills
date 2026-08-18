#!/usr/bin/env python3
"""Start apex-mcp with a TEST or production profile held in the OS keyring."""
import argparse, json, os, sys

SERVICE='apex-skills'

def main():
	p=argparse.ArgumentParser(); p.add_argument('--environment',required=True,choices=('test','production')); p.add_argument('mcp_args',nargs=argparse.REMAINDER); a=p.parse_args()
	try: import keyring
	except ImportError: raise SystemExit('Missing dependency: keyring. Install requirements.txt in the shared skills environment.')
	raw=keyring.get_password(SERVICE,a.environment)
	if not raw: raise SystemExit(f'Missing secure profile: {a.environment}. Run manage_apex_credentials.py set first.')
	try: profile=json.loads(raw)
	except json.JSONDecodeError: raise SystemExit(f'Invalid secure profile: {a.environment}. Set it again.')
	mapping={'ORACLE_DB_USER':'db_user','ORACLE_DB_PASS':'db_pass','ORACLE_DSN':'dsn','ORACLE_WALLET_DIR':'wallet_dir','ORACLE_WALLET_PASSWORD':'wallet_pass','APEX_WORKSPACE_ID':'workspace_id','APEX_SCHEMA':'schema','APEX_WORKSPACE_NAME':'workspace_name'}
	missing=[target for target,source in mapping.items() if not profile.get(source)]
	if missing: raise SystemExit('Incomplete secure profile; missing mapped values: '+', '.join(missing))
	env=os.environ.copy(); env.update({target:str(profile[source]) for target,source in mapping.items()})
	os.execvpe(sys.executable,[sys.executable,'-m','apex_mcp',*a.mcp_args],env)
if __name__=='__main__': main()
