#!/usr/bin/env python3
"""Validate lower-case SQL filenames and tab-only indentation."""
import argparse
from pathlib import Path

def main():
	p=argparse.ArgumentParser(); p.add_argument('path',type=Path); a=p.parse_args()
	files=[a.path] if a.path.is_file() else sorted(a.path.rglob('*.sql'))
	errors=[]
	for file in files:
		if file.name != file.name.lower(): errors.append(f'{file}: filename must be lower-case')
		for number,line in enumerate(file.read_text(encoding='utf-8').splitlines(),1):
			if line.startswith(' '): errors.append(f'{file}:{number}: use a tab, not leading spaces')
	if errors: print('STYLE_FAIL:\n'+'\n'.join(errors)); raise SystemExit(1)
	print(f'STYLE_PASS: {len(files)} SQL file(s)')
if __name__=='__main__': main()
