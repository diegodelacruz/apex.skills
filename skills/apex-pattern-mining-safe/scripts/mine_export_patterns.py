#!/usr/bin/env python3
"""Read-only evidence inventory for split Oracle APEX ZIP exports."""

import collections
import json
import re
import sys
import zipfile
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "scripts"))

from path_setup import setup_skills_path

setup_skills_path(__file__)

from apex_metadata import ApexMetadata
from cli_utils import CLIParser, exit_with_error

from apex_export_utilities import extract_apex_export_metadata, list_export_pages

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def inspect(path):
    """Inspect an APEX export and extract patterns."""
    try:
        root, metadata = extract_apex_export_metadata(path)

        with zipfile.ZipFile(path) as z:
            readable_pages = list_export_pages(z, root, "readable")
            sql_pages = list_export_pages(z, root, "sql")
            names = z.namelist()

            page_content_parts = []
            for n in readable_pages:
                try:
                    page_content_parts.append(z.read(n).decode("utf-8", "strict"))
                except UnicodeDecodeError as err:
                    raise ValueError(f"{path}: page {n} contains invalid UTF-8: {err}") from err

            page_content = "\n".join(page_content_parts)

        apex_meta = ApexMetadata(metadata)
        app_info = apex_meta.get_application_info()
        security = apex_meta.get_security_settings()

        return {
            "archive": path.name,
            "application": {
                "id": app_info.get("id"),
                "name": app_info.get("name"),
                "alias": app_info.get("alias"),
                "schema": app_info.get("schema"),
            },
            "pages": len(readable_pages),
            "security": security,
            "component_types": collections.Counter(
                re.findall(r"^\s*type:\s*(.+?)\s*$", page_content, re.M)
            ).most_common(20),
            "templates": collections.Counter(re.findall(r"^\s*template:\s*(.+?)\s*$", page_content, re.M)).most_common(
                20
            ),
            "readable_pages": len(readable_pages),
            "sql_pages": len(sql_pages),
            "assets": sum("/app_static_files/" in n or "/theme_42/static_files/" in n for n in names),
        }

    except (OSError, ValueError, zipfile.BadZipFile) as err:
        raise ValueError(f"{path}: {err}") from None


def main():
    parser = CLIParser("Mine patterns from Oracle APEX export ZIPs")
    parser.add_argument("export_zip", nargs="+", type=Path, help="Path(s) to APEX export ZIP files")
    parser.add_json_output_arg()
    args = parser.parse_args()

    try:
        report = [inspect(x) for x in args.export_zip]
    except ValueError as err:
        exit_with_error(str(err), "MINING_FAIL")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in report:
            print(f"{item['archive']}: {item['application']['name']} ({item['pages']} readable pages)")


if __name__ == "__main__":
    main()
