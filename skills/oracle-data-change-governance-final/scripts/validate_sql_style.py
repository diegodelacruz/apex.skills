#!/usr/bin/env python3
"""Validate SQL filenames, indentation, and non-literal identifiers."""
import argparse
import re
from pathlib import Path


IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_$#]*")


def code_without_literals_or_comments(line: str, in_block_comment: bool) -> tuple[str, bool]:
	"""Mask text which may legitimately retain upper/mixed case."""
	if not in_block_comment and line.lstrip().lower().startswith('prompt'):
		return '', False
	result = []
	index = 0
	in_string = False
	while index < len(line):
		if in_block_comment:
			end = line.find('*/', index)
			if end == -1:
				return ''.join(result), True
			index = end + 2
			in_block_comment = False
			continue
		character = line[index]
		if not in_string and line[index : index + 2] == '--':
			break
		if not in_string and line[index : index + 2] == '/*':
			in_block_comment = True
			index += 2
			continue
		if character == "'":
			in_string = not in_string
			result.append(' ')
			index += 1
			continue
		result.append(' ' if in_string else character)
		index += 1
	return ''.join(result), in_block_comment


def uppercase_identifiers(line: str, in_block_comment: bool) -> tuple[list[str], bool]:
	code, in_block_comment = code_without_literals_or_comments(line, in_block_comment)
	return [
		match.group(0)
		for match in IDENTIFIER.finditer(code)
		if match.group(0) != match.group(0).lower()
	], in_block_comment


def main():
	p = argparse.ArgumentParser()
	p.add_argument('path', type=Path)
	arguments = p.parse_args()
	files = [arguments.path] if arguments.path.is_file() else sorted(arguments.path.rglob('*.sql'))
	errors = []
	for file in files:
		if file.name != file.name.lower():
			errors.append(f'{file}: filename must be lower-case')
		in_block_comment = False
		for number, line in enumerate(file.read_text(encoding='utf-8').splitlines(), 1):
			if line.startswith(' '):
				errors.append(f'{file}:{number}: use a tab, not leading spaces')
			identifiers, in_block_comment = uppercase_identifiers(line, in_block_comment)
			for identifier in identifiers:
				errors.append(f'{file}:{number}: identifier must be lower-case: {identifier}')
	if errors:
		print('STYLE_FAIL:\n' + '\n'.join(errors))
		raise SystemExit(1)
	print(f'STYLE_PASS: {len(files)} SQL file(s)')


if __name__ == '__main__':
	main()
