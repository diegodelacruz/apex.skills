#!/usr/bin/env python3
"""Inspect Oracle APEX export ZIP contents, extract metadata, and analyze structure."""

import json
import sys
import zipfile
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))

from path_setup import setup_skills_path

setup_skills_path(__file__)

from apex_metadata import ApexMetadata
from cli_utils import CLIParser, exit_with_error, format_key_value

from apex_export_utilities import extract_apex_export_metadata, list_export_pages


def main():
    parser = CLIParser("Inspect Oracle APEX export ZIP contents and metadata")
    parser.add_argument("export_zip", type=Path, help="Path to APEX export ZIP file")
    parser.add_json_output_arg()
    args = parser.parse_args()

    try:
        root, metadata = extract_apex_export_metadata(args.export_zip)

        with zipfile.ZipFile(args.export_zip) as z:
            readable_pages = list_export_pages(z, root, "readable")
            sql_pages = list_export_pages(z, root, "sql")
            names = z.namelist()

        apex_meta = ApexMetadata(metadata)
        app_info = apex_meta.get_application_info()

        out = {
            "archive": args.export_zip.name,
            "root": root,
            "application_id": app_info.get("id"),
            "application_name": app_info.get("name"),
            "alias": app_info.get("alias"),
            "parsing_schema": app_info.get("schema"),
            "readable_pages": len(readable_pages),
            "sql_pages": len(sql_pages),
            "install_sql": f"{root}/install.sql" in names,
        }

    except (OSError, ValueError, zipfile.BadZipFile) as err:
        exit_with_error(str(err), "INSPECT_FAIL")

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(format_key_value(out))


if __name__ == "__main__":
    main()
