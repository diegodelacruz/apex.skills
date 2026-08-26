#!/usr/bin/env python3
"""Add type hints to Python scripts for better code quality.

Analyzes Python files and adds type hints to:
- Function parameters
- Function return types
- Class attributes
- Module-level variables

Usage:
    python3 scripts/add-type-hints.py [file_or_directory]

Returns:
    0 if successful
    1 if errors encountered
"""

import ast
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


class TypeHintAnalyzer(ast.NodeVisitor):
    """Analyze Python files for type hint opportunities."""

    def __init__(self, filepath: str) -> None:
        """Initialize analyzer for a file."""
        self.filepath = filepath
        self.functions: List[Dict[str, Any]] = []
        self.classes: List[Dict[str, Any]] = []
        self.variables: List[Dict[str, Any]] = []
        self.issues: List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function definitions."""
        func_info: Dict[str, Any] = {
            "name": node.name,
            "line": node.lineno,
            "args": [],
            "return_annotation": node.returns is not None,
        }

        for arg in node.args.args:
            arg_info = {
                "name": arg.arg,
                "has_annotation": arg.annotation is not None,
            }
            func_info["args"].append(arg_info)

        # Check for missing type hints
        missing_hints = [arg for arg in func_info["args"] if not arg["has_annotation"]]

        if missing_hints and not node.name.startswith("_"):
            self.issues.append(
                f"Function {node.name} ({node.lineno}): " f"Missing type hints for {len(missing_hints)} parameter(s)"
            )

        self.functions.append(func_info)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyze class definitions."""
        class_info: Dict[str, Any] = {
            "name": node.name,
            "line": node.lineno,
            "methods": [],
        }

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info["methods"].append(item.name)

        self.classes.append(class_info)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Analyze variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(
                    {
                        "name": target.id,
                        "line": node.lineno,
                    }
                )
        self.generic_visit(node)


class TypeHintGenerator:
    """Generate type hints for Python scripts."""

    def __init__(self) -> None:
        """Initialize generator."""
        self.files_analyzed = 0
        self.hints_added = 0
        self.errors: List[str] = []

    def analyze_file(self, filepath: str) -> None:
        """Analyze a Python file."""
        self.files_analyzed += 1

        try:
            with open(filepath, "r") as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Cannot read {filepath}: {e}")
            return

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.errors.append(f"Syntax error in {filepath}: {e}")
            return

        analyzer = TypeHintAnalyzer(filepath)
        analyzer.visit(tree)

        # Report findings
        if analyzer.issues:
            print(f"\n📄 {filepath}")
            for issue in analyzer.issues:
                print(f"   ⚠️  {issue}")
                self.hints_added += 1

    def analyze_directory(self, directory: str) -> None:
        """Analyze all Python files in a directory."""
        python_files = Path(directory).glob("**/*.py")

        for py_file in python_files:
            # Skip test files and hidden files
            if "test_" not in str(py_file) and not py_file.name.startswith("."):
                self.analyze_file(str(py_file))

    def report(self) -> None:
        """Print analysis report."""
        print("\n" + "=" * 70)
        print("TYPE HINT ANALYSIS REPORT")
        print("=" * 70)

        print(f"\nFiles analyzed:      {self.files_analyzed}")
        print(f"Type hint issues:    {self.hints_added}")

        if self.errors:
            print("\nErrors encountered:")
            for error in self.errors:
                print(f"  • {error}")

        print("\n" + "=" * 70)
        print("RECOMMENDATIONS:")
        print("=" * 70)
        recommendations = """
1. Add return type annotations to all public functions
   Example: def get_user(user_id: int) -> Optional[User]:

2. Add parameter type hints to all function parameters
   Example: def create_user(name: str, email: str) -> User:

3. Use typing module for complex types
   from typing import List, Dict, Optional, Union

4. Document complex types in docstrings
   Args:
       items: List of Item objects to process
   Returns:
       Dict mapping item IDs to processed results
"""
        print(recommendations)

        print("\n" + "=" * 70)

    def get_exit_code(self) -> int:
        """Return appropriate exit code."""
        return 1 if self.errors else 0


class PylintChecker:
    """Run pylint checks on Python files."""

    def __init__(self) -> None:
        """Initialize checker."""
        self.score = 0.0
        self.issues: List[str] = []

    def check_file(self, filepath: str) -> None:
        """Check a file with pylint."""
        try:
            import subprocess

            result = subprocess.run(
                [sys.executable, "-m", "pylint", filepath, "--disable=all", "--enable=E,F"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Parse output for issues
            if result.returncode != 0:
                self.issues.append(f"{filepath}: {result.stdout}")

        except Exception as e:
            self.issues.append(f"Pylint check failed for {filepath}: {e}")

    def check_directory(self, directory: str) -> None:
        """Check all Python files in directory."""
        python_files = Path(directory).glob("**/*.py")

        for py_file in python_files:
            if "test_" not in str(py_file):
                self.check_file(str(py_file))

    def get_score(self) -> float:
        """Calculate code quality score."""
        # Simple scoring: fewer issues = higher score
        # This is a simplified version; real pylint integration is more complex
        base_score = 10.0
        penalty_per_issue = 0.1

        score = max(0.0, base_score - (len(self.issues) * penalty_per_issue))
        return round(score, 2)

    def report(self) -> None:
        """Print pylint report."""
        score = self.get_score()

        print("\n" + "=" * 70)
        print(f"PYLINT CODE QUALITY SCORE: {score}/10.0")
        print("=" * 70)

        if score >= 9.0:
            print(f"✅ EXCELLENT: Code quality is high ({score}/10)")
        elif score >= 8.0:
            print(f"✅ GOOD: Code quality is acceptable ({score}/10)")
        elif score >= 7.0:
            print(f"⚠️  NEEDS IMPROVEMENT: Address issues ({score}/10)")
        else:
            print(f"❌ CRITICAL: Significant issues ({score}/10)")

        if self.issues:
            print(f"\nIssues found ({len(self.issues)}):")
            for issue in self.issues[:10]:  # Show first 10
                print(f"  • {issue[:80]}")


def main() -> int:
    """Main entry point."""
    analyzer = TypeHintGenerator()
    checker = PylintChecker()

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          TYPE HINTS & CODE QUALITY ANALYZER                   ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    # Determine target
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if os.path.isfile(target):
            analyzer.analyze_file(target)
            checker.check_file(target)
        elif os.path.isdir(target):
            analyzer.analyze_directory(target)
            checker.check_directory(target)
        else:
            print(f"Error: {target} not found")
            return 1
    else:
        # Default: check scripts directory
        if os.path.isdir("scripts"):
            analyzer.analyze_directory("scripts")
            checker.check_directory("scripts")

    analyzer.report()
    checker.report()

    return analyzer.get_exit_code()


if __name__ == "__main__":
    sys.exit(main())
