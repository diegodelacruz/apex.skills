#!/usr/bin/env python3
import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / 'scripts'))
from apex_export_utilities import extract_apex_export_metadata, get_yaml_field, list_export_pages


def main():
	p = argparse.ArgumentParser()
	p.add_argument('export_zip', type=Path)
	a = p.parse_args()

	try:
		root, metadata = extract_apex_export_metadata(a.export_zip)

		with zipfile.ZipFile(a.export_zip) as z:
			names = z.namelist()
			readable_pages = list_export_pages(z, root, 'readable')
			sql_pages = list_export_pages(z, root, 'sql')
			has_install_sql = f'{root}/install.sql' in names

		checks = [
			has_install_sql,
			len(readable_pages) > 0,
			len(sql_pages) > 0,
			bool(re.search(r'session-state-protection:\s*\n\s+enabled:\s*true', metadata)),
			'html-escaping-mode: Extended' in metadata,
			'theme: Universal Theme # 42' in metadata
		]

		if not all(checks):
			raise ValueError('required structure or declared security setting is absent')

	except (OSError, ValueError, zipfile.BadZipFile) as err:
		print(f'STATIC_FAIL: {err}')
		raise SystemExit(1)

	print(f'STATIC_PASS: {a.export_zip.name}')
	print('sha256: ' + hashlib.sha256(a.export_zip.read_bytes()).hexdigest())


if __name__ == '__main__':
	main()
