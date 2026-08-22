-- ============================================================================
-- File: user_management_example.sql
-- Purpose: Demonstrate Oracle/APEX documentation policy compliance
-- Created: 2026-08-22
-- Policy Reference: docs/ORACLE-APEX-DOCUMENTATION-POLICY.md
-- ============================================================================

-- TABLE: users_example
-- PURPOSE: Example user management table with full documentation
-- NOTES: Demonstrates documentation policy compliance

CREATE TABLE users_example (
	user_id NUMBER PRIMARY KEY,
	username VARCHAR2(100) NOT NULL UNIQUE,
	email VARCHAR2(255) NOT NULL UNIQUE,
	first_name VARCHAR2(100),
	last_name VARCHAR2(100),
	created_date DATE DEFAULT SYSDATE,
	status VARCHAR2(20) DEFAULT 'ACTIVE'
);

comment on column users_example.user_id
	IS 'Unique user identifier. Primary key. Auto-generated via sequence.';

comment on column users_example.username
	IS 'Login username. 3-100 chars, alphanumeric + underscore. Must be unique.';

comment on column users_example.email
	IS 'User email address. Must be unique. Used for notifications and password reset.';

comment on column users_example.first_name
	IS 'User first name. Optional. Maximum 100 characters. Display purposes.';

comment on column users_example.last_name
	IS 'User last name. Optional. Maximum 100 characters. Display purposes.';

comment on column users_example.created_date
	IS 'Account creation timestamp. Automatically set to SYSDATE. Audit purposes.';

comment on column users_example.status
	IS 'Account status: ACTIVE, INACTIVE, SUSPENDED. Controls login eligibility.';

-- ============================================================================
-- PROCEDURE: create_example_user
-- PURPOSE: Create new user with validation
--
-- PARAMETERS:
--   p_username  IN VARCHAR2 - Login username (3-100 chars, unique)
--   p_email     IN VARCHAR2 - Email address (unique, valid format)
--   p_first     IN VARCHAR2 - First name (optional, max 100 chars)
--   p_last      IN VARCHAR2 - Last name (optional, max 100 chars)
--   p_user_id   OUT NUMBER   - Generated user ID
--
-- EXCEPTIONS:
--   USERNAME_EXISTS - If username already taken
--   EMAIL_EXISTS - If email already registered
--   INVALID_EMAIL - If email format invalid
--
-- LOGIC FLOW:
--   1. Validate username (3-100 chars, alphanumeric + underscore)
--   2. Check username uniqueness
--   3. Validate email format
--   4. Check email uniqueness
--   5. Insert new record
--   6. Retrieve generated user_id
--   7. Return user_id
-- ============================================================================

CREATE OR REPLACE PROCEDURE create_example_user (
	p_username  IN VARCHAR2,
	p_email     IN VARCHAR2,
	p_first     IN VARCHAR2 DEFAULT NULL,
	p_last      IN VARCHAR2 DEFAULT NULL,
	p_user_id   OUT NUMBER
) AS
	v_count NUMBER;
BEGIN
	-- Validate username
	IF LENGTH(p_username) < 3 OR LENGTH(p_username) > 100 THEN
		RAISE_APPLICATION_ERROR(-20001, 'Username must be 3-100 characters');
	END IF;

	-- Check username uniqueness
	SELECT COUNT(*) INTO v_count FROM users_example
		WHERE LOWER(username) = LOWER(p_username);
	IF v_count > 0 THEN
		RAISE_APPLICATION_ERROR(-20002, 'Username already exists');
	END IF;

	-- Validate email format
	IF NOT REGEXP_LIKE(p_email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$') THEN
		RAISE_APPLICATION_ERROR(-20003, 'Invalid email format');
	END IF;

	-- Check email uniqueness
	SELECT COUNT(*) INTO v_count FROM users_example
		WHERE LOWER(email) = LOWER(p_email);
	IF v_count > 0 THEN
		RAISE_APPLICATION_ERROR(-20004, 'Email already registered');
	END IF;

	-- Insert new user
	INSERT INTO users_example (username, email, first_name, last_name)
		VALUES (p_username, p_email, p_first, p_last)
		RETURNING user_id INTO p_user_id;

	COMMIT;
END create_example_user;
/

-- ============================================================================
-- FUNCTION: get_user_display_name
-- PURPOSE: Generate formatted user display name
--
-- PARAMETERS:
--   p_user_id IN NUMBER - User ID to retrieve
--
-- RETURNS: VARCHAR2 - Formatted display name (First Last or username fallback)
--
-- LOGIC FLOW:
--   1. Query user record by ID
--   2. If first_name and last_name present: return "First Last"
--   3. If only first_name present: return first_name
--   4. Otherwise: return username
--   5. If user not found: return 'Unknown User'
-- ============================================================================

CREATE OR REPLACE FUNCTION get_user_display_name (
	p_user_id IN NUMBER
) RETURN VARCHAR2 AS
	v_first_name VARCHAR2(100);
	v_last_name VARCHAR2(100);
	v_username VARCHAR2(100);
BEGIN
	SELECT first_name, last_name, username
		INTO v_first_name, v_last_name, v_username
		FROM users_example
		WHERE user_id = p_user_id;

	IF v_first_name IS NOT NULL AND v_last_name IS NOT NULL THEN
		RETURN TRIM(v_first_name || ' ' || v_last_name);
	ELSIF v_first_name IS NOT NULL THEN
		RETURN v_first_name;
	ELSE
		RETURN v_username;
	END IF;

EXCEPTION
	WHEN NO_DATA_FOUND THEN
		RETURN 'Unknown User';
END get_user_display_name;
/

-- ============================================================================
-- VIEW: active_users_example_vw
-- PURPOSE: Display active users with display names
--
-- BASE QUERY:
--   SELECT from users_example
--   WHERE status = 'ACTIVE'
--
-- FILTERS:
--   - status = 'ACTIVE': Only active accounts
--
-- COLUMNS:
--   user_id      - User identifier
--   username     - Login name
--   display_name - Formatted first/last name or username
--   email        - Email address
--   created_date - Account creation date
-- ============================================================================

CREATE OR REPLACE VIEW active_users_example_vw AS
	SELECT
		user_id,
		username,
		get_user_display_name(user_id) AS display_name,
		email,
		created_date
	FROM users_example
	WHERE status = 'ACTIVE'
	ORDER BY created_date DESC;

-- ============================================================================
-- TRIGGER: users_example_audit_trg
-- PURPOSE: Log all changes to users_example table for audit trail
--
-- FIRES: AFTER INSERT, UPDATE, DELETE ON users_example
-- FOR EACH ROW
--
-- ACTIONS:
--   - INSERT: Log new user creation
--   - UPDATE: Log modified fields
--   - DELETE: Log user deletion
-- ============================================================================

CREATE OR REPLACE TRIGGER users_example_audit_trg
AFTER INSERT OR UPDATE OR DELETE ON users_example
FOR EACH ROW
DECLARE
	v_operation VARCHAR2(10);
BEGIN
	v_operation := CASE
		WHEN INSERTING THEN 'INSERT'
		WHEN UPDATING THEN 'UPDATE'
		WHEN DELETING THEN 'DELETE'
	END;

	INSERT INTO users_example_audit (
		operation,
		user_id,
		username,
		email,
		changed_by,
		changed_date
	) VALUES (
		v_operation,
		NVL(:NEW.user_id, :OLD.user_id),
		NVL(:NEW.username, :OLD.username),
		NVL(:NEW.email, :OLD.email),
		USER,
		SYSDATE
	);
END users_example_audit_trg;
/

-- ============================================================================
-- Example Usage: Testing the documented procedures
-- ============================================================================

/*
-- Create test user
DECLARE
	v_user_id NUMBER;
BEGIN
	create_example_user(
		p_username => 'john_doe',
		p_email => 'john@example.com',
		p_first => 'John',
		p_last => 'Doe',
		p_user_id => v_user_id
	);
	DBMS_OUTPUT.PUT_LINE('Created user: ' || v_user_id);
END;
/

-- Query display name
SELECT get_user_display_name(1) AS display_name FROM DUAL;

-- Query active users view
SELECT * FROM active_users_example_vw;
*/

-- END OF FILE
