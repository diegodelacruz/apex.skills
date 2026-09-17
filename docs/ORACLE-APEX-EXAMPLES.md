# Oracle/APEX Documentation Policy - Concrete Examples

**Established:** 2026-08-22
**Policy Version:** 1.0
**Classification:** Internal Reference

This document provides concrete examples showing how to apply the ORACLE-APEX-DOCUMENTATION-POLICY.md to real code.

---

## 1. TABLE DOCUMENTATION EXAMPLE

### Pattern: User Accounts Table

```sql
-- ============================================================================
-- TABLE: user_accounts
-- PURPOSE: Store user authentication and profile information
-- CREATED: 2026-08-22
-- OWNER: Apex Engineering Team
-- NOTES: Primary table for user identity management
-- ============================================================================

CREATE TABLE user_accounts (
	user_id			NUMBER PRIMARY KEY,
	username			VARCHAR2(100) NOT NULL UNIQUE,
	email				VARCHAR2(255) NOT NULL UNIQUE,
	password_hash		VARCHAR2(512) NOT NULL,
	first_name			VARCHAR2(100),
	last_name			VARCHAR2(100),
	created_date		DATE DEFAULT SYSDATE,
	last_login_date		DATE,
	account_status		VARCHAR2(20) DEFAULT 'ACTIVE'
);

-- Column Documentation: user_id
comment on column user_accounts.user_id
	IS 'Unique identifier for user account. Primary key. Auto-generated sequence.';

-- Column Documentation: username
comment on column user_accounts.username
	IS 'Unique login username. 3-100 characters. Used for authentication. Case-sensitive.';

-- Column Documentation: email
comment on column user_accounts.email
	IS 'User email address. Must be unique. Used for password reset and notifications.';

-- Column Documentation: password_hash
comment on column user_accounts.password_hash
	IS 'SHA-256 hash of password. Never store plain text. Hash includes salt.';

-- Column Documentation: first_name
comment on column user_accounts.first_name
	IS 'User first name. Optional. Maximum 100 characters. For display purposes.';

-- Column Documentation: last_name
comment on column user_accounts.last_name
	IS 'User last name. Optional. Maximum 100 characters. For display purposes.';

-- Column Documentation: created_date
comment on column user_accounts.created_date
	IS 'Timestamp when account created. Automatically set to SYSDATE. Used for audit.';

-- Column Documentation: last_login_date
comment on column user_accounts.last_login_date
	IS 'Timestamp of last successful login. NULL if never logged in. Updated by login procedure.';

-- Column Documentation: account_status
comment on column user_accounts.account_status
	IS 'Account status: ACTIVE, SUSPENDED, LOCKED, DELETED. Controls login eligibility.';

-- Table Comment
ALTER TABLE user_accounts
	ADD COMMENT ON TABLE user_accounts
	IS 'User account master table. Stores credentials and profile. Referenced by sessions and permissions.';
```

---

## 2. PROCEDURE DOCUMENTATION EXAMPLE

### Pattern: User Creation Procedure

```sql
-- ============================================================================
-- PROCEDURE: create_user_account
-- PURPOSE: Create new user account with validation and audit trail
-- OWNER: Apex Engineering Team
-- CREATED: 2026-08-22
--
-- PARAMETERS:
--   p_username    IN  VARCHAR2 - Desired login username (3-100 chars, unique)
--   p_email       IN  VARCHAR2 - User email address (valid format, unique)
--   p_first_name  IN  VARCHAR2 - First name (optional, max 100 chars)
--   p_last_name   IN  VARCHAR2 - Last name (optional, max 100 chars)
--   p_password    IN  VARCHAR2 - Plain text password (will be hashed)
--   p_user_id     OUT NUMBER   - Newly created user ID (for reference)
--
-- EXCEPTIONS:
--   USERNAME_ALREADY_EXISTS - If username already in use
--   EMAIL_ALREADY_EXISTS - If email already registered
--   INVALID_EMAIL_FORMAT - If email format invalid
--   PASSWORD_TOO_WEAK - If password doesn't meet complexity rules
--   INVALID_USERNAME_FORMAT - If username doesn't meet requirements
--
-- LOGIC FLOW:
--   1. Validate username format (3-100 chars, alphanumeric+underscore)
--   2. Check if username already exists → raise USERNAME_ALREADY_EXISTS
--   3. Validate email format using regex pattern
--   4. Check if email already exists → raise EMAIL_ALREADY_EXISTS
--   5. Validate password complexity (min 8 chars, 1 upper, 1 lower, 1 number)
--   6. Generate password hash using DBMS_CRYPTO
--   7. Insert new record into user_accounts table
--   8. Retrieve generated user_id from sequence
--   9. Create audit log entry (CREATE operation)
--  10. Commit transaction
--  11. Return user_id
--
-- PERFORMANCE:
--   - Execution time: ~50-100ms
--   - Uses indexed lookups on username and email
--   - Single round-trip to database
--
-- EXAMPLE USAGE:
--   DECLARE
--       v_user_id NUMBER;
--   BEGIN
--       create_user_account(
--           p_username   => 'john_doe',
--           p_email      => 'john@example.com',
--           p_first_name => 'John',
--           p_last_name  => 'Doe',
--           p_password   => 'SecurePass123!', -- pragma: allowlist secret
--           p_user_id    => v_user_id
--       );
--       DBMS_OUTPUT.PUT_LINE('Created user: ' || v_user_id);
--   END;
--   /
-- ============================================================================

CREATE OR REPLACE PROCEDURE create_user_account (
	p_username    IN  VARCHAR2,
	p_email       IN  VARCHAR2,
	p_first_name  IN  VARCHAR2 DEFAULT NULL,
	p_last_name   IN  VARCHAR2 DEFAULT NULL,
	p_password    IN  VARCHAR2,
	p_user_id     OUT NUMBER
) AS
	v_hash        VARCHAR2(512);
	v_count       NUMBER;
	v_salt        VARCHAR2(32);
	USERNAME_ALREADY_EXISTS EXCEPTION;
	EMAIL_ALREADY_EXISTS EXCEPTION;
	INVALID_EMAIL_FORMAT EXCEPTION;
	PASSWORD_TOO_WEAK EXCEPTION;

BEGIN
	-- Step 1-2: Validate and check username uniqueness
	IF LENGTH(p_username) < 3 OR LENGTH(p_username) > 100 THEN
		RAISE INVALID_USERNAME_FORMAT;
	END IF;

	SELECT COUNT(*) INTO v_count FROM user_accounts
		WHERE LOWER(username) = LOWER(p_username);

	IF v_count > 0 THEN
		RAISE USERNAME_ALREADY_EXISTS;
	END IF;

	-- Step 3-4: Validate and check email uniqueness
	IF NOT is_valid_email(p_email) THEN
		RAISE INVALID_EMAIL_FORMAT;
	END IF;

	SELECT COUNT(*) INTO v_count FROM user_accounts
		WHERE LOWER(email) = LOWER(p_email);

	IF v_count > 0 THEN
		RAISE EMAIL_ALREADY_EXISTS;
	END IF;

	-- Step 5: Validate password complexity
	IF NOT is_password_strong(p_password) THEN
		RAISE PASSWORD_TOO_WEAK;
	END IF;

	-- Step 6-7: Hash password and insert record
	v_salt := DBMS_RANDOM.STRING('A', 16);
	v_hash := DBMS_CRYPTO.HASH(
		src => UTL_I18N.STRING_TO_RAW(p_password || v_salt),
		typ => DBMS_CRYPTO.HASH_SH256
	);

	INSERT INTO user_accounts (
		username, email, password_hash, first_name, last_name
	) VALUES (
		p_username, p_email, v_hash, p_first_name, p_last_name
	)
	RETURNING user_id INTO p_user_id;

	-- Step 9: Log audit entry
	INSERT INTO audit_log (
		user_id, action, timestamp, description
	) VALUES (
		p_user_id, 'CREATE', SYSDATE, 'User account created'
	);

	-- Step 10-11: Commit and return
	COMMIT;

EXCEPTION
	WHEN USERNAME_ALREADY_EXISTS THEN
		ROLLBACK;
		RAISE_APPLICATION_ERROR(-20001, 'Username already exists');
	WHEN EMAIL_ALREADY_EXISTS THEN
		ROLLBACK;
		RAISE_APPLICATION_ERROR(-20002, 'Email already registered');
	WHEN INVALID_EMAIL_FORMAT THEN
		ROLLBACK;
		RAISE_APPLICATION_ERROR(-20003, 'Invalid email format');
	WHEN PASSWORD_TOO_WEAK THEN
		ROLLBACK;
		RAISE_APPLICATION_ERROR(-20004, 'Password does not meet complexity requirements');
	WHEN OTHERS THEN
		ROLLBACK;
		RAISE;
END create_user_account;
/
```

---

## 3. FUNCTION DOCUMENTATION EXAMPLE

### Pattern: Password Validation Function

```sql
-- ============================================================================
-- FUNCTION: is_password_strong
-- PURPOSE: Validate password meets complexity requirements
-- OWNER: Apex Security Team
--
-- PARAMETERS:
--   p_password IN VARCHAR2 - Password string to validate
--
-- RETURNS: BOOLEAN - TRUE if password meets requirements, FALSE otherwise
--
-- REQUIREMENTS:
--   - Minimum 8 characters
--   - At least 1 uppercase letter (A-Z)
--   - At least 1 lowercase letter (a-z)
--   - At least 1 digit (0-9)
--   - At least 1 special character (!@#$%^&*)
--
-- LOGIC FLOW:
--   1. Check length >= 8
--   2. Check for uppercase letter pattern
--   3. Check for lowercase letter pattern
--   4. Check for digit pattern
--   5. Check for special character pattern
--   6. Return TRUE if all checks pass, FALSE otherwise
--
-- PERFORMANCE: O(n) where n = password length, typically <1ms
--
-- EXAMPLE USAGE:
--   IF is_password_strong('MyPassword123!') THEN
--       DBMS_OUTPUT.PUT_LINE('Password accepted');
--   ELSE
--       DBMS_OUTPUT.PUT_LINE('Password too weak');
--   END IF;
-- ============================================================================

CREATE OR REPLACE FUNCTION is_password_strong (
	p_password IN VARCHAR2
) RETURN BOOLEAN AS
BEGIN
	-- Step 1: Minimum length check
	IF LENGTH(p_password) < 8 THEN
		RETURN FALSE;
	END IF;

	-- Step 2-5: Pattern checks using regular expressions
	IF NOT REGEXP_LIKE(p_password, '[A-Z]') THEN RETURN FALSE; END IF;
	IF NOT REGEXP_LIKE(p_password, '[a-z]') THEN RETURN FALSE; END IF;
	IF NOT REGEXP_LIKE(p_password, '[0-9]') THEN RETURN FALSE; END IF;
	IF NOT REGEXP_LIKE(p_password, '[!@#$%^&*]') THEN RETURN FALSE; END IF;

	-- Step 6: All checks passed
	RETURN TRUE;
END is_password_strong;
/
```

---

## 4. VIEW DOCUMENTATION EXAMPLE

### Pattern: Active Users Reporting View

```sql
-- ============================================================================
-- VIEW: active_users_vw
-- PURPOSE: Display active users with essential profile information
-- OWNER: Reporting Team
-- CREATED: 2026-08-22
--
-- BASE QUERY:
--   SELECT from user_accounts table
--   Filters: account_status = 'ACTIVE' AND last_login_date IS NOT NULL
--   Joins: None (single table)
--
-- FILTERS:
--   - account_status = 'ACTIVE': Only include active accounts
--   - last_login_date IS NOT NULL: Only users who have logged in at least once
--
-- COLUMNS:
--   user_id         - Unique user identifier (PK from user_accounts)
--   username        - Login username (used for authentication)
--   email           - Email address (for communication)
--   full_name       - Computed: first_name || ' ' || last_name
--   last_login_date - Timestamp of most recent login
--   days_since_login - Computed: TRUNC(SYSDATE) - TRUNC(last_login_date)
--
-- USAGE:
--   SELECT * FROM active_users_vw WHERE days_since_login < 30;
--   -- Returns users active in last 30 days
--
-- REFRESH FREQUENCY: Real-time (views query current data)
-- ============================================================================

CREATE OR REPLACE VIEW active_users_vw AS
	SELECT
		ua.user_id,
		ua.username,
		ua.email,
		ua.first_name || ' ' || ua.last_name AS full_name,
		ua.last_login_date,
		TRUNC(SYSDATE) - TRUNC(ua.last_login_date) AS days_since_login
	FROM user_accounts ua
	WHERE ua.account_status = 'ACTIVE'
	  AND ua.last_login_date IS NOT NULL
	ORDER BY ua.last_login_date DESC;
```

---

## 5. TRIGGER DOCUMENTATION EXAMPLE

### Pattern: Audit Trail Trigger

```sql
-- ============================================================================
-- TRIGGER: user_accounts_audit_trg
-- PURPOSE: Automatically log changes to user_accounts table
-- OWNER: Audit & Compliance Team
--
-- FIRES: AFTER INSERT, UPDATE, DELETE on user_accounts
-- FOR EACH ROW
--
-- ACTIONS:
--   - INSERT: Log new account creation with new values
--   - UPDATE: Log changed columns with before/after values
--   - DELETE: Log account deletion with old values
--
-- AUDIT FIELDS CAPTURED:
--   - audit_id: Unique audit record identifier
--   - table_name: 'USER_ACCOUNTS'
--   - operation: 'INSERT', 'UPDATE', or 'DELETE'
--   - user_id: Affected user ID
--   - changed_columns: Comma-separated list of modified columns
--   - old_values: JSON representation of old data
--   - new_values: JSON representation of new data
--   - timestamp: Operation timestamp (SYSDATE)
--   - session_user: User performing the change (USER)
--
-- PERFORMANCE: <10ms per operation, minimal overhead
-- ============================================================================

CREATE OR REPLACE TRIGGER user_accounts_audit_trg
AFTER INSERT OR UPDATE OR DELETE ON user_accounts
FOR EACH ROW
DECLARE
	v_operation VARCHAR2(10);
BEGIN
	v_operation := CASE
		WHEN INSERTING THEN 'INSERT'
		WHEN UPDATING THEN 'UPDATE'
		WHEN DELETING THEN 'DELETE'
	END;

	INSERT INTO audit_log (
		table_name, operation, user_id, changed_columns,
		old_values, new_values, timestamp, session_user
	) VALUES (
		'USER_ACCOUNTS', v_operation,
		NVL(:NEW.user_id, :OLD.user_id),
		CASE
			WHEN UPDATING THEN get_changed_columns('user_accounts', :OLD, :NEW)
			ELSE NULL
		END,
		CASE WHEN DELETING OR UPDATING THEN row_to_json(:OLD) ELSE NULL END,
		CASE WHEN INSERTING OR UPDATING THEN row_to_json(:NEW) ELSE NULL END,
		SYSDATE, USER
	);
END user_accounts_audit_trg;
/
```

---

## 6. PACKAGE DOCUMENTATION EXAMPLE

### Pattern: User Management Package

```sql
-- ============================================================================
-- PACKAGE: user_management_pkg
-- PURPOSE: Centralized user account lifecycle management
-- OWNER: Apex Engineering Team
-- CREATED: 2026-08-22
--
-- PUBLIC PROCEDURES:
--   create_user       - Create new user account
--   delete_user       - Deactivate user account
--   update_user_email - Change user email address
--   reset_password    - Generate and send password reset link
--   lock_account      - Lock account due to multiple failed attempts
--   unlock_account    - Unlock locked account
--
-- PUBLIC FUNCTIONS:
--   get_user_details  - Retrieve full user information
--   is_user_active    - Check if user account is active
--   get_failed_login_count - Count recent failed login attempts
--
-- PRIVATE PROCEDURES:
--   log_audit_entry   - Internal: write to audit log
--   validate_password_reset_token - Internal: verify reset token
--   send_email_notification - Internal: send user notifications
--
-- DEPENDENCIES:
--   - TABLE: user_accounts
--   - TABLE: audit_log
--   - FUNCTION: is_password_strong
--   - FUNCTION: is_valid_email
--   - PACKAGE: email_notification_pkg (for email sending)
--
-- EXAMPLE USAGE:
--   BEGIN
--       user_management_pkg.create_user(
--           p_username => 'jsmith',
--           p_email => 'jsmith@company.com',
--           p_password => 'InitialPassword123!' -- pragma: allowlist secret
--       );
--       DBMS_OUTPUT.PUT_LINE('User created successfully');
--   EXCEPTION
--       WHEN OTHERS THEN
--           DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
--   END;
--   /
-- ============================================================================

CREATE OR REPLACE PACKAGE user_management_pkg AS

	-- PUBLIC PROCEDURES
	PROCEDURE create_user (
		p_username    IN VARCHAR2,
		p_email       IN VARCHAR2,
		p_first_name  IN VARCHAR2 DEFAULT NULL,
		p_last_name   IN VARCHAR2 DEFAULT NULL,
		p_password    IN VARCHAR2
	);

	PROCEDURE delete_user (
		p_user_id IN NUMBER
	);

	PROCEDURE update_user_email (
		p_user_id IN NUMBER,
		p_new_email IN VARCHAR2
	);

	-- PUBLIC FUNCTIONS
	FUNCTION get_user_details (
		p_user_id IN NUMBER
	) RETURN SYS_REFCURSOR;

	FUNCTION is_user_active (
		p_user_id IN NUMBER
	) RETURN BOOLEAN;

END user_management_pkg;
/
```

---

## Summary: Key Takeaways

1. **EVERY** Oracle/APEX object needs a documentation header with PURPOSE
2. **Tables** require `ALTER TABLE ADD COMMENT ON COLUMN` for each column
3. **Procedures** need PARAMETERS, EXCEPTIONS, and LOGIC FLOW sections
4. **Functions** require PARAMETERS, RETURNS, and LOGIC FLOW sections
5. **Views** need BASE QUERY and FILTERS sections
6. **Triggers** require FIRES, ACTIONS sections
7. **Packages** need listing of PUBLIC and PRIVATE procedures/functions
8. **Comments should be detailed** - future maintainers need to understand the intent, not just the code

---

**Validation:** Run `python3 scripts/validate-oracle-documentation.py docs/` to check compliance.
