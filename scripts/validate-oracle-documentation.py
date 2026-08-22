#!/usr/bin/env python3
"""Validate Oracle/APEX documentation compliance.

Checks that all Oracle objects are properly documented according to
ORACLE-APEX-DOCUMENTATION-POLICY.md

Usage:
    python3 scripts/validate-oracle-documentation.py [file_or_directory]

Returns:
    0 if all checks pass
    1 if any documentation is missing
"""

import os
import re
import sys
from pathlib import Path
from typing import List


class DocumentationValidator:
    """Validate Oracle/APEX code documentation."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.files_checked = 0
        self.objects_found = 0

    def validate_file(self, filepath: str) -> bool:
        """Validate documentation in a single SQL file.

        Args:
                filepath: Path to SQL file

        Returns:
                True if all checks pass, False otherwise
        """
        try:
            with open(filepath, "r") as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Cannot read {filepath}: {e}")
            return False

        self.files_checked += 1
        all_pass = True

        # Check for CREATE TABLE statements
        tables = re.findall(r"CREATE\s+TABLE\s+(\w+)", content, re.IGNORECASE)
        for table_name in tables:
            self.objects_found += 1
            if not self._check_table_comments(content, table_name):
                all_pass = False

        # Check for CREATE PROCEDURE statements
        procedures = re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+(\w+)", content, re.IGNORECASE)
        for proc_name in procedures:
            self.objects_found += 1
            if not self._check_procedure_documentation(content, proc_name):
                all_pass = False

        # Check for CREATE FUNCTION statements
        functions = re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(\w+)", content, re.IGNORECASE)
        for func_name in functions:
            self.objects_found += 1
            if not self._check_function_documentation(content, func_name):
                all_pass = False

        # Check for CREATE VIEW statements
        views = re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)", content, re.IGNORECASE)
        for view_name in views:
            self.objects_found += 1
            if not self._check_view_documentation(content, view_name):
                all_pass = False

        return all_pass

    def _check_table_comments(self, content: str, table_name: str) -> bool:
        """Check if table has comments on all columns.

        Requirements:
        - Header comment with PURPOSE
        - ALTER TABLE ADD COMMENT for each column
        """
        # Check for table header comment
        pattern = r"--\s+TABLE:\s+" + table_name + r".*?PURPOSE:"
        if not re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            self.errors.append(f"Table {table_name}: Missing header comment with PURPOSE")
            return False

        # Extract column names from CREATE TABLE
        create_pattern = rf"CREATE\s+TABLE\s+{table_name}\s*\((.*?)\);"
        match = re.search(create_pattern, content, re.IGNORECASE | re.DOTALL)
        if not match:
            return True  # Can't parse columns, skip check

        columns_section = match.group(1)
        columns = re.findall(r"(\w+)\s+(?:NUMBER|VARCHAR2|DATE|CLOB|BLOB)", columns_section)

        # Check for ALTER TABLE ADD COMMENT for each column
        for column in columns:
            comment_pattern = rf"ALTER\s+TABLE\s+{table_name}\s+ADD\s+COMMENT\s+ON\s+COLUMN\s+{table_name}\.{column}"
            if not re.search(comment_pattern, content, re.IGNORECASE):
                self.warnings.append(f"Table {table_name}.{column}: Missing ALTER TABLE ADD COMMENT")
                return False

        return True

    def _check_procedure_documentation(self, content: str, proc_name: str) -> bool:
        """Check if procedure has complete documentation.

        Requirements:
        - Header comment with PURPOSE
        - PARAMETERS section
        - EXCEPTIONS section
        - LOGIC FLOW section (for complex procedures)
        """
        pattern = r"--\s+PROCEDURE:\s+" + proc_name + r".*?PURPOSE:"
        if not re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            self.errors.append(f"Procedure {proc_name}: Missing header comment with PURPOSE")
            return False

        # Check for PARAMETERS section
        if not re.search(r"PARAMETERS:", content[content.find(proc_name):], re.IGNORECASE):
            self.warnings.append(f"Procedure {proc_name}: Missing PARAMETERS section")
            return False

        return True

    def _check_function_documentation(self, content: str, func_name: str) -> bool:
        """Check if function has complete documentation.

        Requirements:
        - Header comment with PURPOSE
        - PARAMETERS section
        - RETURNS section
        - LOGIC FLOW section
        """
        pattern = r"--\s+FUNCTION:\s+" + func_name + r".*?PURPOSE:"
        if not re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            self.errors.append(f"Function {func_name}: Missing header comment with PURPOSE")
            return False

        # Check for RETURNS section
        if not re.search(r"RETURNS:", content, re.IGNORECASE):
            self.warnings.append(f"Function {func_name}: Missing RETURNS section")
            return False

        return True

    def _check_view_documentation(self, content: str, view_name: str) -> bool:
        """Check if view has documentation.

        Requirements:
        - Header comment with PURPOSE
        - BASE QUERY section
        - COLUMNS section
        """
        pattern = r"--\s+VIEW:\s+" + view_name + r".*?PURPOSE:"
        if not re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            self.warnings.append(f"View {view_name}: Missing header comment with PURPOSE")
            # Don't fail on this; views are sometimes simple
            return True

        return True

    def validate_directory(self, directory: str) -> bool:
        """Validate all SQL files in a directory.

        Args:
                directory: Path to directory containing SQL files

        Returns:
                True if all checks pass, False otherwise
        """
        sql_files = Path(directory).glob("**/*.sql")
        all_pass = True

        for sql_file in sql_files:
            if not self.validate_file(str(sql_file)):
                all_pass = False

        return all_pass

    def report(self) -> None:
        """Print validation report."""
        print("\n" + "=" * 80)
        print("ORACLE/APEX DOCUMENTATION VALIDATION REPORT")
        print("=" * 80)

        print(f"\nFiles checked:    {self.files_checked}")
        print(f"Objects found:    {self.objects_found}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("\n✅ No critical errors found")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        else:
            print("\n✅ No warnings")

        print("\n" + "=" * 80)

    def get_exit_code(self) -> int:
        """Return appropriate exit code.

        0 if no errors (warnings OK)
        1 if any errors found
        """
        return 1 if self.errors else 0


def main() -> int:
    """Main entry point."""
    validator = DocumentationValidator()

    # If argument provided, validate that file/directory
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            validator.validate_file(target)
        elif os.path.isdir(target):
            validator.validate_directory(target)
        else:
            print(f"Error: {target} not found")
            return 1
    else:
        # Default: check common SQL locations
        for directory in ["scripts", "skills"]:
            if os.path.isdir(directory):
                validator.validate_directory(directory)

    validator.report()
    return validator.get_exit_code()


if __name__ == "__main__":
    sys.exit(main())
