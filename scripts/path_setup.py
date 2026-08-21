#!/usr/bin/env python3
"""Shared path setup utilities for APEX Skills.

This module provides centralized path setup functions to avoid duplicating
sys.path.insert() across multiple scripts. All functions return Path objects
for the directory they set up.

Example:
	>>> from path_setup import get_repo_root
	>>> repo = get_repo_root()
	>>> exports_dir = repo / "tests/fixtures/apex-exports"
"""

import sys
from pathlib import Path


def setup_scripts_path(script_file: str = __file__):
	"""Add the scripts directory to sys.path for imports.

	This centralizes the path setup logic used across multiple CLI scripts.
	Instead of duplicating sys.path.insert in each script, call this function.

	Args:
		script_file: __file__ from the calling script (default: this module)

	Returns:
		Path object for the scripts directory

	Example:
		>>> # In any script (e.g., validate_export.py):
		>>> from path_setup import setup_scripts_path
		>>> setup_scripts_path(__file__)
		>>> from apex_export_utilities import extract_apex_export_metadata
	"""
	scripts_dir = Path(script_file).resolve().parent
	if str(scripts_dir) not in sys.path:
		sys.path.insert(0, str(scripts_dir))
	return scripts_dir


def setup_skills_path(script_file: str = __file__):
	"""Add the skills/*/scripts directory's parent scripts to sys.path.

	Used by skill-level scripts that need to import from the main scripts directory.

	Args:
		script_file: __file__ from the calling script

	Returns:
		Path object for the root scripts directory

	Example:
		>>> # In a skill script (e.g., skills/apex-export-qa-safe/scripts/validate_export.py):
		>>> from path_setup import setup_skills_path
		>>> setup_skills_path(__file__)
		>>> from apex_export_utilities import extract_apex_export_metadata
	"""
	# Navigate from: skills/*/scripts/script.py to scripts/
	skill_script_path = Path(script_file).resolve()
	root_scripts_dir = skill_script_path.parent.parent.parent.parent / "scripts"

	if str(root_scripts_dir) not in sys.path:
		sys.path.insert(0, str(root_scripts_dir))

	return root_scripts_dir


def setup_test_path(test_file: str = __file__) -> Path:
	"""Add the scripts directory to sys.path for test files.

	Args:
		test_file: __file__ from the test script

	Returns:
		Path object for the scripts directory

	Example:
		>>> # In a test file (e.g., tests/test_apex_export_utilities.py):
		>>> from path_setup import setup_test_path
		>>> setup_test_path(__file__)
		>>> from apex_export_utilities import extract_apex_export_metadata
	"""
	test_path = Path(test_file).resolve()
	scripts_dir = test_path.parent.parent / "scripts"

	if str(scripts_dir) not in sys.path:
		sys.path.insert(0, str(scripts_dir))

	return scripts_dir


def get_repo_root(start_path: str = __file__) -> Path:
	"""Get the root directory of the apex.skills repository.

	Searches upward from start_path for the .git directory to find repo root.

	Args:
		start_path: Starting path for search (__file__ by default)

	Returns:
		Path object pointing to repository root

	Raises:
		RuntimeError: If .git directory not found (not in a git repository)

	Example:
		>>> root = get_repo_root()
		>>> assert (root / 'CLAUDE.md').exists()
		>>> skills_dir = root / 'skills'
	"""
	current = Path(start_path).resolve()
	if current.is_file():
		current = current.parent

	# Search upward for .git directory
	for path in [current] + list(current.parents):
		if (path / '.git').exists():
			return path

	raise RuntimeError(f"Could not find repository root starting from {start_path}")


def get_script_dir() -> Path:
	"""Get the scripts/ directory of apex.skills.

	Returns:
		Path object for the scripts directory

	Example:
		>>> scripts_dir = get_script_dir()
		>>> cli_utils = scripts_dir / 'cli_utils.py'
	"""
	repo_root = get_repo_root(__file__)
	return repo_root / 'scripts'
