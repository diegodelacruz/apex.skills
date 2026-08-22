#!/usr/bin/env python3
"""Shared CLI utilities for APEX Skills scripts."""

import argparse
import sys
from typing import Dict, List, Optional, Tuple


class CLIParser:
    """Unified argument parser for APEX Skills CLI scripts."""

    def __init__(self, description: str, add_common_args: bool = True):
        """Initialize CLI parser.

        Args:
                description: Script description for help text
                add_common_args: Whether to add common arguments (environment, json, etc)
        """
        self.parser = argparse.ArgumentParser(description=description)
        self.add_common_args = add_common_args

    def add_argument(self, *args, **kwargs) -> None:
        """Add an argument to the parser.

        Args:
                *args: Positional arguments passed to argparse.add_argument
                **kwargs: Keyword arguments passed to argparse.add_argument

        Example:
                >>> parser = CLIParser("My script")
                >>> parser.add_argument('--output', default='output.json')
        """
        self.parser.add_argument(*args, **kwargs)

    def add_environment_arg(self, choices: Tuple[str, ...] = ("test", "production"), default: str = "test") -> None:
        """Add --environment argument."""
        self.parser.add_argument(
            "--environment",
            choices=choices,
            default=default,
            help=f"Target environment (default: {default})",
        )

    def add_json_output_arg(self) -> None:
        """Add --json flag for JSON output."""
        self.parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON",
        )

    def add_verbose_arg(self) -> None:
        """Add --verbose flag."""
        self.parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Verbose output",
        )

    def add_quiet_arg(self) -> None:
        """Add --quiet flag."""
        self.parser.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            help="Suppress output",
        )

    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """Parse and return arguments."""
        return self.parser.parse_args(args)


def exit_with_error(message: str, error_code: str = "ERROR", exit_code: int = 1) -> None:
    """Print error message and exit.

    Args:
            message: Error message to display
            error_code: Error code prefix (e.g., "VALIDATE_FAIL")
            exit_code: Exit code (default: 1)

    Raises:
            SystemExit: Always exits with specified code
    """
    print(f"{error_code}: {message}", file=sys.stderr)
    raise SystemExit(exit_code)


def exit_with_success(message: str, success_code: str = "SUCCESS") -> None:
    """Print success message and exit.

    Args:
            message: Success message to display
            success_code: Success code prefix (e.g., "VALIDATE_PASS")

    Raises:
            SystemExit: Always exits with code 0
    """
    print(f"{success_code}: {message}")
    raise SystemExit(0)


def format_key_value(data: Dict[str, any]) -> str:
    """Format dictionary as key=value output.

    Args:
            data: Dictionary to format

    Returns:
            Formatted output string
    """
    return "\n".join(f"{k}: {v}" for k, v in data.items())
