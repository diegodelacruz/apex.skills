#!/usr/bin/env python3
import argparse
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / 'scripts'))
from apex_export_utilities import extract_apex_export_metadata, get_yaml_field, list_export_pages


def main():
	p = argparse.ArgumentParser()
	p.add_argument('export_zip', type=Path)
	p.add_argument('--json', action='store_true')
	a = p.parse_args()

	try:
		root, metadata = extract_apex_export_metadata(a.export_zip)

		with zipfile.ZipFile(a.export_zip) as z:
			readable_pages = list_export_pages(z, root, 'readable')
			sql_pages = list_export_pages(z, root, 'sql')
			names = z.namelist()

		out = {
			'archive': a.export_zip.name,
			'root': root,
			'application_id': get_yaml_field(metadata, 'id'),
			'application_name': get_yaml_field(metadata, 'name'),
			'alias': get_yaml_field(metadata, 'alias'),
			'parsing_schema': get_yaml_field(metadata, 'parsing-schema'),
			'readable_pages': len(readable_pages),
			'sql_pages': len(sql_pages),
			'install_sql': f'{root}/install.sql' in names
		}

	except (OSError, ValueError, zipfile.BadZipFile) as err:
		print(f'INSPECT_FAIL: {err}')
		raise SystemExit(1)

	if a.json:
		print(json.dumps(out, ensure_ascii=False, indent=2))
	else:
		for k, v in out.items():
			print(f'{k}: {v}')


if __name__ == '__main__':
	main()
