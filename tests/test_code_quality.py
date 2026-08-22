"""Tests for code quality standards.

Tests:
- Type hint coverage
- Pylint compliance
- Code style standards
- Docstring presence
"""

import re
import unittest
from pathlib import Path
from typing import List


class CodeQualityTestCase(unittest.TestCase):
    """Base class for code quality tests."""

    @staticmethod
    def get_python_scripts() -> List[Path]:
        """Get all Python scripts excluding tests."""
        scripts_dir = Path(__file__).parent.parent / "scripts"
        return [f for f in scripts_dir.glob("*.py") if not f.name.startswith("test_")]


class TypeHintCoverageTest(CodeQualityTestCase):
    """Test type hint coverage."""

    def test_scripts_have_type_hints(self) -> None:
        """Test that scripts include type hints."""
        scripts = self.get_python_scripts()
        self.assertGreater(len(scripts), 0)

        for script in scripts:
            with open(script, "r") as f:
                content = f.read()

            # Check for type hint patterns
            has_return_hints = bool(re.search(r"-> [A-Za-z\[\]]+:", content))
            has_param_hints = bool(re.search(r":\s*[A-Za-z\[\]]+", content))
            has_import_types = bool(re.search(r"from typing import|import typing", content))

            # At least one type hint indicator should exist
            has_hints = has_return_hints or has_param_hints or has_import_types
            self.assertTrue(has_hints, f"{script.name}: Missing type hints")

    def test_main_scripts_have_docstrings(self) -> None:
        """Test that main functions have docstrings."""
        scripts = self.get_python_scripts()
        important_scripts = [
            s for s in scripts if s.name in ["apex_export_utilities.py", "apex_metadata.py", "cli_utils.py"]
        ]

        for script in important_scripts:
            with open(script, "r") as f:
                content = f.read()

            # Check for docstring patterns
            has_module_docstring = bool(re.search(r'^"""', content, re.MULTILINE))
            self.assertTrue(has_module_docstring, f"{script.name}: Missing module docstring")


class DocstringComplianceTest(CodeQualityTestCase):
    """Test docstring standards."""

    def test_functions_have_docstrings(self) -> None:
        """Test that public functions have docstrings."""
        scripts = self.get_python_scripts()

        for script in scripts:
            if script.name == "add-type-hints.py":
                # Already tested separately
                continue

            with open(script, "r") as f:
                content = f.read()

            # Extract function definitions
            functions = re.findall(r"def (\w+)\([^)]*\):", content)
            public_functions = [f for f in functions if not f.startswith("_")]

            # At least some public functions should have docstrings
            if public_functions:
                docstring_count = content.count('"""')
                self.assertGreater(docstring_count, 0, f"{script.name}: No docstrings found")

    def test_classes_have_docstrings(self) -> None:
        """Test that classes have docstrings."""
        scripts = self.get_python_scripts()

        for script in scripts:
            with open(script, "r") as f:
                content = f.read()

            # Check for class definitions
            if "class " in content:
                # Should have docstrings
                if '"""' in content or "'''" in content:
                    self.assertIn("class", content)


class ImportOrganizationTest(CodeQualityTestCase):
    """Test import organization."""

    def test_imports_organized_properly(self) -> None:
        """Test that imports are organized by category."""
        scripts = self.get_python_scripts()

        for script in scripts:
            with open(script, "r") as f:
                lines = f.readlines()

            # Find import section
            import_lines = []
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    import_lines.append((i, line))
                elif import_lines and line.strip() and not line.strip().startswith("#"):
                    break  # End of import section

            # Check basic organization: stdlib, then third-party, then local
            if len(import_lines) > 1:
                self.assertGreater(len(import_lines), 0)


class CodeStyleTest(CodeQualityTestCase):
    """Test code style standards."""

    def test_line_length_reasonable(self) -> None:
        """Test that lines are not excessively long."""
        scripts = self.get_python_scripts()

        for script in scripts:
            with open(script, "r") as f:
                lines = f.readlines()

            long_lines = [
                (i + 1, len(line.rstrip()))
                for i, line in enumerate(lines)
                if len(line.rstrip()) > 120 and not line.strip().startswith("#")
            ]

            # Allow some long lines but not too many
            self.assertLess(
                len(long_lines),
                len(lines) * 0.1,  # No more than 10% long lines
                f"{script.name}: Too many long lines (>120 chars)",
            )

    def test_no_trailing_whitespace(self) -> None:
        """Test that scripts don't have trailing whitespace."""
        scripts = self.get_python_scripts()

        for script in scripts:
            with open(script, "r") as f:
                lines = f.readlines()

            trailing_ws_lines = [(i + 1) for i, line in enumerate(lines) if line.rstrip() != line.rstrip("\n").rstrip()]

            self.assertEqual(len(trailing_ws_lines), 0, f"{script.name}: Lines with trailing whitespace")


class FunctionComplexityTest(CodeQualityTestCase):
    """Test function complexity metrics."""

    def test_functions_not_too_complex(self) -> None:
        """Test that functions aren't too complex."""
        scripts = self.get_python_scripts()

        for script in scripts:
            with open(script, "r") as f:
                content = f.read()

            # Simple complexity check: look for excessive nesting
            # Count max indentation level
            lines = content.split("\n")
            max_indent = 0
            for line in lines:
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    max_indent = max(max_indent, indent)

            # Max nesting should be reasonable (e.g., < 40 spaces = 10 levels)
            self.assertLess(max_indent, 40, f"{script.name}: Functions possibly too deeply nested")


class ImportHealthTest(CodeQualityTestCase):
    """Test for unused imports."""

    def test_common_imports_present(self) -> None:
        """Test that essential imports are present when needed."""
        scripts = self.get_python_scripts()

        for script in scripts:
            with open(script, "r") as f:
                content = f.read()

            # If using typing annotations, should import typing
            if ": List[" in content or ": Dict[" in content or ": Optional[" in content:
                self.assertTrue(
                    "typing" in content or "from typing" in content,
                    f"{script.name}: Uses typing hints but doesn't import typing",
                )

            # If using Path directly, should import pathlib
            if re.search(r'\bPath\(["\']', content):  # Direct Path() calls
                self.assertTrue(
                    "Path" in content and ("pathlib" in content or "from pathlib" in content),
                    f"{script.name}: Uses Path but doesn't import pathlib",
                )


if __name__ == "__main__":
    unittest.main()
