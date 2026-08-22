"""Unit tests for cli_utils module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cli_utils import CLIParser, format_key_value  # noqa: E402


class TestCLIParser:
    """Tests for CLIParser class."""

    @pytest.mark.unit
    def test_parser_creation(self):
        """Create a basic CLI parser."""
        parser = CLIParser("Test parser")
        assert parser.parser is not None

    @pytest.mark.unit
    def test_add_environment_arg(self):
        """Add environment argument."""
        parser = CLIParser("Test")
        parser.add_environment_arg(choices=("test", "prod"), default="test")
        args = parser.parse_args(["--environment", "prod"])
        assert args.environment == "prod"

    @pytest.mark.unit
    def test_environment_arg_default(self):
        """Test environment argument defaults."""
        parser = CLIParser("Test")
        parser.add_environment_arg()
        args = parser.parse_args([])
        assert args.environment == "test"

    @pytest.mark.unit
    def test_add_json_output_arg(self):
        """Add JSON output flag."""
        parser = CLIParser("Test")
        parser.add_json_output_arg()
        args = parser.parse_args(["--json"])
        assert args.json is True

    @pytest.mark.unit
    def test_json_output_default_false(self):
        """JSON output defaults to False."""
        parser = CLIParser("Test")
        parser.add_json_output_arg()
        args = parser.parse_args([])
        assert args.json is False

    @pytest.mark.unit
    def test_add_verbose_arg(self):
        """Add verbose flag."""
        parser = CLIParser("Test")
        parser.add_verbose_arg()
        args = parser.parse_args(["-v"])
        assert args.verbose is True

    @pytest.mark.unit
    def test_add_quiet_arg(self):
        """Add quiet flag."""
        parser = CLIParser("Test")
        parser.add_quiet_arg()
        args = parser.parse_args(["--quiet"])
        assert args.quiet is True

    @pytest.mark.unit
    def test_combined_arguments(self):
        """Test multiple arguments together."""
        parser = CLIParser("Test")
        parser.add_argument("--name", type=str)
        parser.add_environment_arg()
        parser.add_json_output_arg()
        args = parser.parse_args(["--name", "MyApp", "--environment", "production", "--json"])
        assert args.name == "MyApp"
        assert args.environment == "production"
        assert args.json is True


class TestFormatKeyValue:
    """Tests for format_key_value() function."""

    @pytest.mark.unit
    def test_simple_dict(self):
        """Format a simple dictionary."""
        data = {"name": "TestApp", "id": "123"}
        output = format_key_value(data)
        assert "name: TestApp" in output
        assert "id: 123" in output

    @pytest.mark.unit
    def test_empty_dict(self):
        """Format empty dictionary."""
        output = format_key_value({})
        assert output == ""

    @pytest.mark.unit
    def test_single_item(self):
        """Format single item."""
        output = format_key_value({"key": "value"})
        assert output == "key: value"

    @pytest.mark.unit
    def test_none_values(self):
        """Handle None values."""
        data = {"name": "App", "value": None}
        output = format_key_value(data)
        assert "name: App" in output
        assert "value: None" in output

    @pytest.mark.unit
    def test_numeric_values(self):
        """Handle numeric values."""
        data = {"count": 42, "ratio": 3.14}
        output = format_key_value(data)
        assert "count: 42" in output
        assert "ratio: 3.14" in output
