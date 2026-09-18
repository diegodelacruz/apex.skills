#!/usr/bin/env python3
"""Shared utilities for Oracle APEX export processing."""

import zipfile
from pathlib import Path
from typing import List, Optional, Tuple, Union

from scripts.apex_metadata import ApexMetadata


def extract_apex_export_metadata(zip_path: Union[str, Path]) -> Tuple[str, str]:
    """Extract root directory and metadata YAML from an APEX export ZIP.

    Args:
        zip_path: Path to the export ZIP file

    Returns:
        Tuple of (root_dir, metadata_yaml_text) where:
        - root_dir is the single root directory name in the export
        - metadata_yaml_text is the decoded YAML metadata content

    Raises:
        ValueError: If ZIP structure is invalid (multiple roots or missing metadata)
        OSError: If file cannot be read
        zipfile.BadZipFile: If file is not a valid ZIP
        TypeError: If zip_path is neither string nor Path
    """
    if not isinstance(zip_path, (str, Path)):
        raise TypeError(f"zip_path must be str or Path, not {type(zip_path).__name__}")

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        roots = {x.split("/", 1)[0] for x in names if "/" in x}

        if len(roots) != 1:
            raise ValueError(f"{zip_path}: expected exactly one export root, found {len(roots)}")

        root = roots.pop()
        meta_path = f"{root}/readable/application/{root}.yaml"

        if meta_path not in names:
            raise ValueError(f"{zip_path}: missing readable application YAML at {meta_path}")

        try:
            metadata = z.read(meta_path).decode("utf-8", "strict")
        except UnicodeDecodeError as err:
            raise ValueError(f"{zip_path}: metadata YAML contains invalid UTF-8 at {meta_path}: {err}") from err

        return root, metadata


def get_yaml_field(yaml_text: Optional[str], field_name: Optional[str]) -> Optional[str]:
    """Extract a field value from YAML text using regex.

    Backward-compatible wrapper around ApexMetadata.get_field().
    Replaces previous lookup() and field() functions with unified implementation.

    Args:
        yaml_text: Raw YAML text content
        field_name: Name of the field to extract (e.g., 'id', 'name', 'parsing-schema')

    Returns:
        The field value with quotes stripped, or None if field not found.

    Examples:
        >>> get_yaml_field("name: 'My App'", "name")
        'My App'
        >>> get_yaml_field("id: 12345", "id")
        '12345'
        >>> get_yaml_field("unknown", "missing")
        None
    """
    return ApexMetadata.get_field(yaml_text, field_name)


def list_export_pages(
    zip_path: Union[str, Path, zipfile.ZipFile], root_dir: str, page_type: str = "readable"
) -> List[str]:
    """List pages in an APEX export ZIP.

    Args:
        zip_path: Path to or ZipFile object
        root_dir: Root directory name in the export
        page_type: 'readable' (YAML) or 'sql' (SQL)

    Returns:
        List of page file paths matching the type

    Raises:
        ValueError: If page_type is not 'readable' or 'sql'
        TypeError: If zip_path is not str, Path, or ZipFile
        ValueError: If root_dir is empty
    """
    if not root_dir:
        raise ValueError("root_dir cannot be empty")

    if page_type not in ("readable", "sql"):
        raise ValueError(f"Invalid page_type: {page_type}. Must be 'readable' or 'sql'.")

    if isinstance(zip_path, zipfile.ZipFile):
        names = zip_path.namelist()
    else:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()

    if page_type == "readable":
        return [n for n in names if n.startswith(f"{root_dir}/readable/application/pages/") and n.endswith(".yaml")]
    else:  # page_type == "sql"
        return [n for n in names if n.startswith(f"{root_dir}/application/pages/") and n.endswith(".sql")]
