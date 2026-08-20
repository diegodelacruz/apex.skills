"""Unit tests for apex_export_utilities module."""

import pytest
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
import zipfile

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from apex_export_utilities import (
	extract_apex_export_metadata,
	get_yaml_field,
	list_export_pages,
)


class TestGetYamlField:
	"""Tests for get_yaml_field() function."""

	@pytest.mark.unit
	def test_simple_field_extraction(self):
		"""Extract a simple YAML field value."""
		yaml_text = "name: TestApp"
		assert get_yaml_field(yaml_text, "name") == "TestApp"

	@pytest.mark.unit
	def test_quoted_field_extraction(self):
		"""Extract a quoted YAML field value."""
		yaml_text = "name: 'My Application'"
		assert get_yaml_field(yaml_text, "name") == "My Application"

	@pytest.mark.unit
	def test_hyphenated_field_name(self):
		"""Extract a field with hyphenated name."""
		yaml_text = "parsing-schema: MYSCHEMA"
		assert get_yaml_field(yaml_text, "parsing-schema") == "MYSCHEMA"

	@pytest.mark.unit
	def test_missing_field(self):
		"""Return None for missing field."""
		yaml_text = "name: TestApp"
		assert get_yaml_field(yaml_text, "missing") is None

	@pytest.mark.unit
	def test_null_inputs(self):
		"""Return None for null/empty inputs."""
		assert get_yaml_field(None, "field") is None
		assert get_yaml_field("", "field") is None
		assert get_yaml_field("text", None) is None

	@pytest.mark.unit
	def test_multiline_yaml(self):
		"""Extract field from multiline YAML."""
		yaml_text = """
		id: 12345
		name: MyApp
		alias: my_app
		"""
		assert get_yaml_field(yaml_text, "id") == "12345"
		assert get_yaml_field(yaml_text, "name") == "MyApp"
		assert get_yaml_field(yaml_text, "alias") == "my_app"

	@pytest.mark.unit
	def test_numeric_field(self):
		"""Extract numeric field value."""
		yaml_text = "id: 12345"
		assert get_yaml_field(yaml_text, "id") == "12345"

	@pytest.mark.unit
	def test_double_quoted_field(self):
		"""Extract double-quoted field value."""
		yaml_text = 'name: "Application Name"'
		assert get_yaml_field(yaml_text, "name") == "Application Name"


class TestExtractApexExportMetadata:
	"""Tests for extract_apex_export_metadata() function."""

	@pytest.mark.unit
	def test_invalid_zip_file(self):
		"""Raise error for invalid ZIP file."""
		with NamedTemporaryFile(suffix=".zip") as tmp:
			tmp.write(b"not a zip file")
			tmp.flush()
			with pytest.raises(Exception):
				extract_apex_export_metadata(Path(tmp.name))

	@pytest.mark.unit
	def test_zip_with_no_root_directory(self):
		"""Raise error for ZIP without proper root directory."""
		with NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
			try:
				with zipfile.ZipFile(tmp.name, "w") as z:
					z.writestr("file1.txt", "content")
					z.writestr("file2.txt", "content")

				with pytest.raises(ValueError, match="expected exactly one export root"):
					extract_apex_export_metadata(Path(tmp.name))
			finally:
				Path(tmp.name).unlink()

	@pytest.mark.unit
	def test_zip_with_multiple_roots(self):
		"""Raise error for ZIP with multiple root directories."""
		with NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
			try:
				with zipfile.ZipFile(tmp.name, "w") as z:
					z.writestr("f123/file.txt", "content")
					z.writestr("f456/file.txt", "content")

				with pytest.raises(ValueError, match="expected exactly one export root"):
					extract_apex_export_metadata(Path(tmp.name))
			finally:
				Path(tmp.name).unlink()


class TestListExportPages:
	"""Tests for list_export_pages() function."""

	@pytest.mark.unit
	def test_list_readable_pages(self):
		"""List readable (YAML) pages from export."""
		with NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
			try:
				with zipfile.ZipFile(tmp.name, "w") as z:
					z.writestr("f123/readable/application/pages/page1.yaml", "")
					z.writestr("f123/readable/application/pages/page2.yaml", "")
					z.writestr("f123/application/pages/page1.sql", "")

				with zipfile.ZipFile(tmp.name) as z:
					pages = list_export_pages(z, "f123", "readable")
					assert len(pages) == 2
					assert all(p.endswith(".yaml") for p in pages)
			finally:
				Path(tmp.name).unlink()

	@pytest.mark.unit
	def test_list_sql_pages(self):
		"""List SQL pages from export."""
		with NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
			try:
				with zipfile.ZipFile(tmp.name, "w") as z:
					z.writestr("f123/readable/application/pages/page1.yaml", "")
					z.writestr("f123/application/pages/page1.sql", "")
					z.writestr("f123/application/pages/page2.sql", "")

				with zipfile.ZipFile(tmp.name) as z:
					pages = list_export_pages(z, "f123", "sql")
					assert len(pages) == 2
					assert all(p.endswith(".sql") for p in pages)
			finally:
				Path(tmp.name).unlink()
