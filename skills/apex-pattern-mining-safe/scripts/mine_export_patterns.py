#!/usr/bin/env python3
"""Read-only evidence inventory for split Oracle APEX ZIP exports."""
import argparse
import collections
import json
import re
import sys
import zipfile
from pathlib import Path

try:
	sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
	pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / 'scripts'))
from apex_export_utilities import extract_apex_export_metadata, get_yaml_field, list_export_pages


def inspect(path):
	"""Inspect an APEX export and extract patterns."""
	try:
		root, metadata = extract_apex_export_metadata(path)

		with zipfile.ZipFile(path) as z:
			readable_pages = list_export_pages(z, root, 'readable')
			sql_pages = list_export_pages(z, root, 'sql')
			names = z.namelist()

			page_content = '\n'.join(
				z.read(n).decode('utf-8', 'strict')
				for n in readable_pages
			)

		return {
			'archive': path.name,
			'application': {
				'id': get_yaml_field(metadata, 'id'),
				'name': get_yaml_field(metadata, 'name'),
				'alias': get_yaml_field(metadata, 'alias'),
				'schema': get_yaml_field(metadata, 'parsing-schema')
			},
			'pages': len(readable_pages),
			'security': {
				'session_state_protection': bool(
					re.search(r'session-state-protection:\s*\n\s+enabled:\s*true', metadata)
				),
				'extended_html_escaping': 'html-escaping-mode: Extended' in metadata,
				'deep_links_disabled': 'deep-linking: Disabled' in metadata,
				'frames_denied': 'embed-in-frames: Deny' in metadata
			},
			'component_types': collections.Counter(
				re.findall(r'^\s*type:\s*(.+?)\s*$', page_content, re.M)
			).most_common(20),
			'templates': collections.Counter(
				re.findall(r'^\s*template:\s*(.+?)\s*$', page_content, re.M)
			).most_common(20),
			'readable_pages': len(readable_pages),
			'sql_pages': len(sql_pages),
			'assets': sum(
				'/app_static_files/' in n or '/theme_42/static_files/' in n
				for n in names
			)
		}

	except (OSError, ValueError, zipfile.BadZipFile) as err:
		raise ValueError(f'{path}: {err}') from None


def main():
	p = argparse.ArgumentParser()
	p.add_argument('export_zip', nargs='+', type=Path)
	p.add_argument('--json', action='store_true')
	a = p.parse_args()

	try:
		report = [inspect(x) for x in a.export_zip]
	except ValueError as err:
		print(f'MINING_FAIL: {err}')
		raise SystemExit(1)

	if a.json:
		print(json.dumps(report, ensure_ascii=False, indent=2))
	else:
		for item in report:
			print(f"{item['archive']}: {item['application']['name']} ({item['pages']} readable pages)")


if __name__ == '__main__':
	main()
