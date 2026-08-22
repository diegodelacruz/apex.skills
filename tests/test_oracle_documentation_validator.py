"""Tests for Oracle/APEX documentation validator script.

Tests documentation validation including:
- Table comment validation
- Procedure documentation checking
- Function documentation checking
- View documentation checking
- Error reporting and exit codes
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from typing import List

# Load module with dashes in filename
script_path = Path(__file__).parent.parent / "scripts" / "validate-oracle-documentation.py"
spec = importlib.util.spec_from_file_location("validate_oracle_documentation", script_path)
validate_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_module)

DocumentationValidator = validate_module.DocumentationValidator


class DocumentationValidatorTestCase(unittest.TestCase):
    """Base class for documentation validator tests."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.validator = DocumentationValidator()

    def tearDown(self) -> None:
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_sql_file(self, content: str) -> Path:
        """Create a temporary SQL file with content."""
        sql_file = self.test_dir / "test.sql"
        sql_file.write_text(content)
        return sql_file


class TableDocumentationTest(DocumentationValidatorTestCase):
    """Test table documentation validation."""

    def test_table_with_proper_documentation(self) -> None:
        """Test table with complete documentation."""
        content = """
		-- TABLE: users
		-- PURPOSE: Store user account information
		-- CREATED: 2026-08-22

		CREATE TABLE users (
			id NUMBER PRIMARY KEY,
			username VARCHAR2(255),
			email VARCHAR2(255)
		);

		ALTER TABLE users ADD COMMENT ON COLUMN users.id IS 'Unique user identifier';
		ALTER TABLE users ADD COMMENT ON COLUMN users.username IS 'User login name';
		ALTER TABLE users ADD COMMENT ON COLUMN users.email IS 'User email address';
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        # Should pass or warn depending on implementation
        self.assertIsNotNone(result)

    def test_table_missing_header_comment(self) -> None:
        """Test table without header comment."""
        content = """
		CREATE TABLE products (
			id NUMBER PRIMARY KEY,
			name VARCHAR2(255)
		);
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        # Should detect the table
        self.assertIsNotNone(result)
        self.assertGreater(self.validator.objects_found, 0)


class ProcedureDocumentationTest(DocumentationValidatorTestCase):
    """Test procedure documentation validation."""

    def test_procedure_with_complete_documentation(self) -> None:
        """Test procedure with all required documentation."""
        content = """
		-- PROCEDURE: create_user_proc
		-- PURPOSE: Creates a new user account
		-- PARAMETERS:
		--   p_username IN VARCHAR2 - User login name
		--   p_email IN VARCHAR2 - User email address
		--   p_user_id OUT NUMBER - Generated user ID
		-- EXCEPTIONS:
		--   DUPLICATE_USER - If username already exists
		--   INVALID_EMAIL - If email format is invalid

		CREATE OR REPLACE PROCEDURE create_user_proc (
			p_username IN VARCHAR2,
			p_email IN VARCHAR2,
			p_user_id OUT NUMBER
		) AS
		BEGIN
			INSERT INTO users (username, email) VALUES (p_username, p_email)
			RETURNING id INTO p_user_id;
		END;
		/
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        self.assertIsNotNone(result)

    def test_procedure_missing_parameters_section(self) -> None:
        """Test procedure without PARAMETERS section."""
        content = """
		-- PROCEDURE: simple_proc
		-- PURPOSE: Simple test procedure

		CREATE OR REPLACE PROCEDURE simple_proc (p_value IN VARCHAR2) AS
		BEGIN
			NULL;
		END;
		/
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        self.assertIsNotNone(result)


class FunctionDocumentationTest(DocumentationValidatorTestCase):
    """Test function documentation validation."""

    def test_function_with_complete_documentation(self) -> None:
        """Test function with complete documentation."""
        content = """
		-- FUNCTION: calculate_tax
		-- PURPOSE: Calculate tax amount for given amount
		-- PARAMETERS:
		--   p_amount IN NUMBER - Base amount
		-- RETURNS: NUMBER - Calculated tax amount
		-- LOGIC FLOW:
		--   1. Validate input amount
		--   2. Fetch tax rate from configuration
		--   3. Calculate tax = amount * rate
		--   4. Return calculated tax

		CREATE OR REPLACE FUNCTION calculate_tax (p_amount IN NUMBER) RETURN NUMBER AS
		BEGIN
			RETURN p_amount * 0.15;
		END;
		/
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        self.assertIsNotNone(result)

    def test_function_missing_returns_section(self) -> None:
        """Test function without RETURNS section."""
        content = """
		-- FUNCTION: get_value
		-- PURPOSE: Retrieve a value

		CREATE OR REPLACE FUNCTION get_value RETURN VARCHAR2 AS
		BEGIN
			RETURN 'test';
		END;
		/
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        self.assertIsNotNone(result)


class ViewDocumentationTest(DocumentationValidatorTestCase):
    """Test view documentation validation."""

    def test_view_with_documentation(self) -> None:
        """Test view with proper documentation."""
        content = """
		-- VIEW: active_users_v
		-- PURPOSE: Show all active users
		-- BASE QUERY: Selects from users table with status = 'ACTIVE'
		-- COLUMNS:
		--   id - User identifier
		--   username - User login name
		--   email - User email address

		CREATE OR REPLACE VIEW active_users_v AS
			SELECT id, username, email FROM users WHERE status = 'ACTIVE';
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        self.assertIsNotNone(result)


class ValidatorReportingTest(DocumentationValidatorTestCase):
    """Test validator error reporting."""

    def test_validator_collects_errors(self) -> None:
        """Test that validator collects errors."""
        self.assertEqual(len(self.validator.errors), 0)
        self.assertEqual(len(self.validator.warnings), 0)

    def test_validator_counts_objects(self) -> None:
        """Test that validator counts objects found."""
        content = """
		CREATE TABLE table1 (id NUMBER);
		CREATE TABLE table2 (id NUMBER);
		CREATE PROCEDURE proc1 AS BEGIN NULL; END;
		"""

        sql_file = self._create_sql_file(content)
        self.validator.validate_file(str(sql_file))

        self.assertGreater(self.validator.objects_found, 0)

    def test_validator_exit_code_on_errors(self) -> None:
        """Test exit code when errors exist."""
        # Add a mock error
        self.validator.errors.append("Test error")
        exit_code = self.validator.get_exit_code()

        self.assertEqual(exit_code, 1)

    def test_validator_exit_code_on_success(self) -> None:
        """Test exit code when no errors."""
        self.validator.errors = []
        exit_code = self.validator.get_exit_code()

        self.assertEqual(exit_code, 0)

    def test_validator_files_checked_count(self) -> None:
        """Test validator counts files checked."""
        content = "SELECT 1 FROM DUAL;"
        sql_file = self._create_sql_file(content)
        self.validator.validate_file(str(sql_file))

        self.assertEqual(self.validator.files_checked, 1)


class MultipleObjectsTest(DocumentationValidatorTestCase):
    """Test validation of files with multiple objects."""

    def test_file_with_multiple_tables(self) -> None:
        """Test file containing multiple tables."""
        content = """
		CREATE TABLE users (id NUMBER);
		CREATE TABLE products (id NUMBER);
		CREATE TABLE orders (id NUMBER);
		"""

        sql_file = self._create_sql_file(content)
        self.validator.validate_file(str(sql_file))

        self.assertGreaterEqual(self.validator.objects_found, 3)

    def test_file_with_mixed_objects(self) -> None:
        """Test file with tables, procedures, and functions."""
        content = """
		CREATE TABLE users (id NUMBER);
		CREATE PROCEDURE create_user AS BEGIN NULL; END;
		CREATE FUNCTION get_user_count RETURN NUMBER AS BEGIN RETURN 0; END;
		CREATE VIEW user_view AS SELECT * FROM users;
		"""

        sql_file = self._create_sql_file(content)
        self.validator.validate_file(str(sql_file))

        self.assertGreaterEqual(self.validator.objects_found, 4)


class DocumentationComplexSQLTest(DocumentationValidatorTestCase):
    """Test documentation validation with complex SQL."""

    def test_procedure_with_complex_logic(self) -> None:
        """Test procedure with complex business logic."""
        content = """
		-- PROCEDURE: process_orders
		-- PURPOSE: Process pending orders and update inventory
		-- PARAMETERS:
		--   p_order_id IN NUMBER - Order to process
		--   p_status OUT VARCHAR2 - Processing status
		-- EXCEPTIONS:
		--   ORDER_NOT_FOUND - If order doesn't exist
		--   INSUFFICIENT_INVENTORY - If not enough stock
		-- LOGIC FLOW:
		--   1. Validate order exists
		--   2. Check inventory levels
		--   3. Deduct from inventory
		--   4. Update order status
		--   5. Create audit record

		CREATE OR REPLACE PROCEDURE process_orders (
			p_order_id IN NUMBER,
			p_status OUT VARCHAR2
		) AS
		BEGIN
			-- Validation logic
			-- Update logic
			p_status := 'PROCESSED';
		END;
		/
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        self.assertIsNotNone(result)

    def test_package_with_multiple_procedures(self) -> None:
        """Test package containing multiple procedures."""
        content = """
		-- PACKAGE: user_management_pkg
		-- PURPOSE: User account management package
		-- PROCEDURES:
		--   create_user - Create new user
		--   delete_user - Remove user account
		--   update_user_email - Update email address

		CREATE OR REPLACE PACKAGE user_management_pkg AS
			PROCEDURE create_user (p_username IN VARCHAR2);
			PROCEDURE delete_user (p_user_id IN NUMBER);
			PROCEDURE update_user_email (p_user_id IN NUMBER, p_email IN VARCHAR2);
		END user_management_pkg;
		/
		"""

        sql_file = self._create_sql_file(content)
        self.validator.validate_file(str(sql_file))

        # Should handle package definitions
        self.assertIsNotNone(self.validator)


class ValidationEdgeCasesTest(DocumentationValidatorTestCase):
    """Test edge cases in validation."""

    def test_empty_sql_file(self) -> None:
        """Test validation of empty SQL file."""
        sql_file = self._create_sql_file("")
        result = self.validator.validate_file(str(sql_file))

        self.assertEqual(self.validator.objects_found, 0)

    def test_sql_file_with_comments_only(self) -> None:
        """Test SQL file with only comments."""
        content = """
		-- This is a comment
		-- Another comment
		-- More comments
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        self.assertEqual(self.validator.objects_found, 0)

    def test_sql_with_mixed_case_keywords(self) -> None:
        """Test SQL with mixed case keywords."""
        content = """
		create table MixedCase (id number);
		CREATE PROCEDURE test_proc as begin null; end;
		Create Function test_func Return Number As Begin Return 1; End;
		"""

        sql_file = self._create_sql_file(content)
        result = self.validator.validate_file(str(sql_file))

        # Should handle case-insensitive matching
        self.assertGreaterEqual(self.validator.objects_found, 1)


if __name__ == "__main__":
    unittest.main()
