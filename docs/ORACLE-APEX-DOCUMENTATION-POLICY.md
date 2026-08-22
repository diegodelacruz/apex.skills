# Oracle APEX Documentation Policy

**Última actualización:** 2026-08-21  
**Status:** MANDATORY for all Oracle/APEX skills  
**Validation:** Automated via `scripts/validate-oracle-documentation.py`

---

## 🎯 REGLA DE ORO

> **SIEMPRE documentar código Oracle/APEX generado.**
> 
> Documentación clara pero eficiente (no extensa).  
> Si hay duda, preguntar al usuario en el skill.

---

## 📋 ESTÁNDAR DE DOCUMENTACIÓN

### Por Tipo de Objeto

#### 1. TABLAS

**Requisito:** SQL comments inline + COMMENT ON COLUMN para cada columna (sintaxis Oracle correcta)

```sql
-- ============================================================================
-- TABLE: customers
-- ============================================================================
-- PURPOSE: Master table for customer information
-- COLUMNS:
--   - customer_id    (NUMBER)      PK, auto-increment via sequence
--   - name           (VARCHAR2)    Customer full name (required)
--   - email          (VARCHAR2)    Email address (unique)
--   - phone          (VARCHAR2)    Contact phone number
--   - created_date   (DATE)        Audit: Record creation timestamp
--   - updated_date   (DATE)        Audit: Last update timestamp
-- 
-- INDEXES:
--   - idx_customers_email (unique) for fast lookups by email
-- 
-- TRIGGERS:
--   - trg_customers_update (auto-update updated_date on modify)
-- ============================================================================

CREATE TABLE customers (
	customer_id   NUMBER PRIMARY KEY,
	name          VARCHAR2(100) NOT NULL,
	email         VARCHAR2(100) UNIQUE NOT NULL,
	phone         VARCHAR2(20),
	created_date  DATE DEFAULT SYSDATE NOT NULL,
	updated_date  DATE DEFAULT SYSDATE NOT NULL
);

-- Document each column
ALTER TABLE customers ADD COMMENT ON COLUMN customers.customer_id 
	IS 'Primary key: Unique customer identifier, auto-generated via seq_customer_id';

ALTER TABLE customers ADD COMMENT ON COLUMN customers.name 
	IS 'Customer full name (first + last). Required field. Max 100 chars.';

ALTER TABLE customers ADD COMMENT ON COLUMN customers.email 
	IS 'Email address. Unique constraint enforced. Used for login and communication.';

ALTER TABLE customers ADD COMMENT ON COLUMN customers.phone 
	IS 'Contact phone number. Optional. Format: may vary by region.';

ALTER TABLE customers ADD COMMENT ON COLUMN customers.created_date 
	IS 'Audit column: Timestamp when record was created. Set by database.';

ALTER TABLE customers ADD COMMENT ON COLUMN customers.updated_date 
	IS 'Audit column: Timestamp when record was last modified. Updated by trigger.';
```

**Checklist:**
- [ ] Table header with PURPOSE
- [ ] COLUMNS list with name, type, purpose
- [ ] INDEXES listed if any
- [ ] TRIGGERS listed if any
- [ ] ALTER TABLE COMMENT for each column (detailed)

---

#### 2. VISTAS (VIEWS)

**Requisito:** SQL comments inline + ALTER VIEW COMMENT + Document base query purpose

```sql
-- ============================================================================
-- VIEW: v_active_customers
-- ============================================================================
-- PURPOSE: List of customers with active subscriptions
-- 
-- BASE QUERY: Joins customers + subscriptions tables
-- FILTERS: subscription_status = 'ACTIVE' AND subscription_end_date >= SYSDATE
-- 
-- COLUMNS:
--   - customer_id    (NUMBER)      From customers table
--   - name           (VARCHAR2)    Customer name
--   - email          (VARCHAR2)    Customer email
--   - subscription_id(NUMBER)      Active subscription
--   - subscription_type(VARCHAR2)  Type of subscription (BASIC, PRO, ENTERPRISE)
--   - start_date     (DATE)        Subscription start date
--   - end_date       (DATE)        Subscription end date (future)
-- ============================================================================

CREATE OR REPLACE VIEW v_active_customers AS
	SELECT
		c.customer_id,
		c.name,
		c.email,
		s.subscription_id,
		s.subscription_type,
		s.start_date,
		s.end_date
	FROM
		customers c
		INNER JOIN subscriptions s ON c.customer_id = s.customer_id
	WHERE
		s.subscription_status = 'ACTIVE'
		AND s.end_date >= TRUNC(SYSDATE);

ALTER TABLE v_active_customers ADD COMMENT ON COLUMN v_active_customers.subscription_id 
	IS 'Active subscription ID. Joins to subscriptions table.';

ALTER TABLE v_active_customers ADD COMMENT ON COLUMN v_active_customers.subscription_type 
	IS 'Type of subscription: BASIC (free), PRO (paid monthly), ENTERPRISE (custom)';
```

**Checklist:**
- [ ] View header with PURPOSE
- [ ] BASE QUERY section explaining joins
- [ ] FILTERS section listing WHERE conditions
- [ ] COLUMNS list with source and purpose
- [ ] ALTER TABLE COMMENT for derived/complex columns

---

#### 3. ÍNDICES (INDEXES)

**Requisito:** SQL comments inline with purpose and usage

```sql
-- ============================================================================
-- INDEX: idx_customers_email
-- ============================================================================
-- PURPOSE: Fast lookup by email address (used in login, user search)
-- TYPE: Unique index
-- COLUMNS: email
-- ESTIMATED USAGE: High (login queries, user searches)
-- ============================================================================

CREATE UNIQUE INDEX idx_customers_email ON customers(email);
```

**Checklist:**
- [ ] Purpose documented
- [ ] Type (unique, composite, etc.)
- [ ] Columns listed
- [ ] Usage pattern documented

---

#### 4. SECUENCIAS (SEQUENCES)

**Requisito:** SQL comments explaining range and purpose

```sql
-- ============================================================================
-- SEQUENCE: seq_customer_id
-- ============================================================================
-- PURPOSE: Generate unique customer IDs
-- RANGE: 1 to 9,999,999 (7-digit max)
-- INCREMENT: 1
-- USAGE: customer_id DEFAULT seq_customer_id.NEXTVAL
-- ============================================================================

CREATE SEQUENCE seq_customer_id
	START WITH 1
	INCREMENT BY 1
	MAXVALUE 9999999
	CYCLE;
```

**Checklist:**
- [ ] Purpose documented
- [ ] Range/max value explained
- [ ] Usage pattern shown

---

#### 5. PROCEDIMIENTOS (PROCEDURES)

**Requisito:** Detailed header + Comments for complex sections + Parameter documentation

```sql
-- ============================================================================
-- PROCEDURE: calc_subscription_total
-- ============================================================================
-- PURPOSE: Calculate total subscription cost including taxes and discounts
-- 
-- PARAMETERS:
--   p_subscription_id (IN NUMBER)
--       Subscription ID to calculate. Must exist in subscriptions table.
--   p_include_tax (IN BOOLEAN DEFAULT TRUE)
--       Whether to include taxes in calculation. Default: TRUE
--   p_total_amount (OUT NUMBER)
--       Output parameter: Calculated total (base + tax - discount)
--   p_error_code (OUT VARCHAR2)
--       Output parameter: Error code if operation fails. NULL if success.
-- 
-- EXCEPTIONS:
--   -20001: Subscription not found
--   -20002: Invalid tax configuration
--   -20003: Discount exceeds total
-- 
-- LOGIC FLOW:
--   1. Validate subscription exists (raise -20001 if not)
--   2. Fetch base amount from subscriptions table
--   3. Calculate tax if p_include_tax = TRUE (use TAX_RATE from config)
--   4. Apply discount if exists (validate discount <= base amount)
--   5. Return total in p_total_amount
-- 
-- USAGE EXAMPLE:
--   DECLARE
--     v_total NUMBER;
--     v_error VARCHAR2(100);
--   BEGIN
--     calc_subscription_total(123, TRUE, v_total, v_error);
--     IF v_error IS NULL THEN
--       DBMS_OUTPUT.PUT_LINE('Total: ' || v_total);
--     ELSE
--       DBMS_OUTPUT.PUT_LINE('Error: ' || v_error);
--     END IF;
--   END;
-- ============================================================================

CREATE OR REPLACE PROCEDURE calc_subscription_total(
	p_subscription_id   IN  NUMBER,
	p_include_tax       IN  BOOLEAN DEFAULT TRUE,
	p_total_amount      OUT NUMBER,
	p_error_code        OUT VARCHAR2
)
IS
	v_base_amount    NUMBER;
	v_tax_amount     NUMBER;
	v_discount_amount NUMBER;
	v_tax_rate       NUMBER := 0.21; -- 21% standard tax rate
BEGIN
	p_error_code := NULL;
	
	-- STEP 1: Validate subscription exists
	-- Query subscriptions table; raise -20001 if not found
	SELECT base_price INTO v_base_amount
	FROM subscriptions
	WHERE subscription_id = p_subscription_id;
	
	-- STEP 2: Fetch discount if applicable
	-- Some subscriptions may have promotional discounts
	SELECT NVL(discount_amount, 0) INTO v_discount_amount
	FROM subscriptions
	WHERE subscription_id = p_subscription_id;
	
	-- STEP 3: Validate discount doesn't exceed base amount
	-- Prevent negative totals or invalid business logic
	IF v_discount_amount > v_base_amount THEN
		RAISE_APPLICATION_ERROR(-20003, 'Discount exceeds total amount');
	END IF;
	
	-- STEP 4: Calculate tax if requested
	-- Tax only applies to net amount (after discount)
	IF p_include_tax THEN
		v_tax_amount := (v_base_amount - v_discount_amount) * v_tax_rate;
	ELSE
		v_tax_amount := 0;
	END IF;
	
	-- STEP 5: Calculate final total and return
	p_total_amount := v_base_amount - v_discount_amount + v_tax_amount;
	
EXCEPTION
	WHEN NO_DATA_FOUND THEN
		p_error_code := 'SUBSCRIPTION_NOT_FOUND';
		p_total_amount := NULL;
	WHEN VALUE_ERROR THEN
		p_error_code := 'INVALID_VALUE';
		p_total_amount := NULL;
	WHEN OTHERS THEN
		p_error_code := SQLERRM;
		p_total_amount := NULL;
END calc_subscription_total;
/
```

**Checklist:**
- [ ] Purpose statement clear
- [ ] All parameters documented (type, purpose, constraints)
- [ ] EXCEPTIONS listed with codes
- [ ] LOGIC FLOW with step numbers
- [ ] Complex sections explained inline
- [ ] USAGE EXAMPLE with valid scenario

---

#### 6. FUNCIONES (FUNCTIONS)

**Requisito:** Same as procedures, plus RETURNS section

```sql
-- ============================================================================
-- FUNCTION: get_customer_discount_rate
-- ============================================================================
-- PURPOSE: Determine discount rate based on customer tenure and status
-- 
-- PARAMETERS:
--   p_customer_id (IN NUMBER)
--       Customer ID to check. Must exist in customers table.
-- 
-- RETURNS: NUMBER (0.00 to 0.50)
--   Discount rate as decimal:
--   - 0.00: New customer (< 1 month)
--   - 0.05: Regular customer (1-12 months)
--   - 0.10: Loyal customer (1-3 years)
--   - 0.20: VIP customer (> 3 years)
--   
--   Additional multipliers:
--   - If customer_status = 'PREMIUM': add 0.10
--   - If total_purchases > $10,000: add 0.05
-- 
-- EXCEPTIONS:
--   -20001: Customer not found
-- 
-- LOGIC FLOW:
--   1. Validate customer exists
--   2. Calculate tenure (SYSDATE - created_date)
--   3. Determine base rate by tenure brackets
--   4. Apply premium status multiplier
--   5. Apply purchase volume multiplier
--   6. Cap at maximum 0.50 (50% discount)
--   7. Return final discount rate
-- 
-- PERFORMANCE:
--   Execution time: < 50ms (indexed lookups)
--   Recommended max concurrent calls: 1000/sec
-- 
-- USAGE EXAMPLE:
--   DECLARE
--     v_rate NUMBER;
--   BEGIN
--     v_rate := get_customer_discount_rate(123);
--     DBMS_OUTPUT.PUT_LINE('Discount rate: ' || TO_CHAR(v_rate * 100) || '%');
--   END;
-- ============================================================================

CREATE OR REPLACE FUNCTION get_customer_discount_rate(p_customer_id IN NUMBER)
RETURN NUMBER
IS
	v_discount_rate   NUMBER := 0.00;
	v_created_date    DATE;
	v_tenure_months   NUMBER;
	v_customer_status VARCHAR2(20);
	v_total_purchases NUMBER;
BEGIN
	-- STEP 1: Validate customer exists and fetch details
	-- Single SELECT for efficiency; raises NO_DATA_FOUND if not found
	SELECT created_date, customer_status, NVL(total_purchases, 0)
	INTO v_created_date, v_customer_status, v_total_purchases
	FROM customers
	WHERE customer_id = p_customer_id;
	
	-- STEP 2: Calculate customer tenure in months
	v_tenure_months := MONTHS_BETWEEN(SYSDATE, v_created_date);
	
	-- STEP 3: Determine base discount rate by tenure brackets
	-- Logic: longer tenure = higher discount, encouraging retention
	IF v_tenure_months < 1 THEN
		v_discount_rate := 0.00;  -- New customers: no discount
	ELSIF v_tenure_months < 12 THEN
		v_discount_rate := 0.05;  -- < 1 year: 5% discount
	ELSIF v_tenure_months < 36 THEN
		v_discount_rate := 0.10;  -- 1-3 years: 10% discount
	ELSE
		v_discount_rate := 0.20;  -- 3+ years: 20% discount (loyal)
	END IF;
	
	-- STEP 4: Apply premium status multiplier
	-- Premium customers get additional 10% discount
	IF v_customer_status = 'PREMIUM' THEN
		v_discount_rate := v_discount_rate + 0.10;
	END IF;
	
	-- STEP 5: Apply purchase volume multiplier
	-- High-value customers (>$10k purchases) get additional 5% discount
	IF v_total_purchases > 10000 THEN
		v_discount_rate := v_discount_rate + 0.05;
	END IF;
	
	-- STEP 6: Cap discount at maximum 50%
	-- Safety check to prevent business logic errors (discount > base)
	IF v_discount_rate > 0.50 THEN
		v_discount_rate := 0.50;
	END IF;
	
	-- STEP 7: Return final discount rate
	RETURN v_discount_rate;
	
EXCEPTION
	WHEN NO_DATA_FOUND THEN
		RAISE_APPLICATION_ERROR(-20001, 'Customer not found: ' || p_customer_id);
	WHEN OTHERS THEN
		RAISE_APPLICATION_ERROR(-20099, 'Error in get_customer_discount_rate: ' || SQLERRM);
END get_customer_discount_rate;
/
```

**Checklist:**
- [ ] Purpose statement clear
- [ ] PARAMETERS documented
- [ ] RETURNS section with range and logic
- [ ] EXCEPTIONS listed
- [ ] LOGIC FLOW with step numbers
- [ ] Complex calculations explained
- [ ] PERFORMANCE notes (if relevant)
- [ ] USAGE EXAMPLE

---

#### 7. PAQUETES (PACKAGES)

**Requisito:** Package spec header + Each procedure/function documented

```sql
-- ============================================================================
-- PACKAGE: pkg_subscription_management
-- ============================================================================
-- PURPOSE: Central package for all subscription-related operations
--   (create, modify, cancel, calculate totals, apply discounts)
-- 
-- PUBLIC PROCEDURES:
--   - create_subscription(p_customer_id, p_type) RETURN subscription_id
--   - modify_subscription(p_subscription_id, p_new_type)
--   - cancel_subscription(p_subscription_id, p_reason)
--   - renew_subscription(p_subscription_id) RETURN new_subscription_id
-- 
-- PUBLIC FUNCTIONS:
--   - calc_total(p_subscription_id, p_include_tax) RETURN NUMBER
--   - get_discount_rate(p_customer_id) RETURN NUMBER
--   - is_subscription_active(p_subscription_id) RETURN BOOLEAN
-- 
-- PRIVATE PROCEDURES:
--   - validate_subscription_type(p_type)
--   - log_subscription_audit(p_action, p_subscription_id)
-- 
-- USAGE EXAMPLE:
--   DECLARE
--     v_sub_id NUMBER;
--   BEGIN
--     v_sub_id := pkg_subscription_management.create_subscription(123, 'PRO');
--     DBMS_OUTPUT.PUT_LINE('Created subscription: ' || v_sub_id);
--   END;
-- 
-- DEPENDENCIES:
--   - customers table
--   - subscriptions table
--   - subscription_audit table
-- ============================================================================

CREATE OR REPLACE PACKAGE pkg_subscription_management IS
	-- Public procedure: create new subscription
	PROCEDURE create_subscription(
		p_customer_id IN  NUMBER,
		p_type        IN  VARCHAR2,
		p_sub_id      OUT NUMBER
	);
	
	-- Public function: calculate subscription total
	FUNCTION calc_total(
		p_subscription_id IN NUMBER,
		p_include_tax     IN BOOLEAN DEFAULT TRUE
	) RETURN NUMBER;
	
	-- ... more public procedures and functions ...
	
END pkg_subscription_management;
/
```

**Checklist:**
- [ ] Package header with PURPOSE
- [ ] PUBLIC PROCEDURES listed with signatures
- [ ] PUBLIC FUNCTIONS listed with return types
- [ ] PRIVATE items noted (internal use only)
- [ ] USAGE EXAMPLE
- [ ] DEPENDENCIES listed

---

#### 8. TRIGGERS

**Requisito:** Purpose + When it fires + Actions documented

```sql
-- ============================================================================
-- TRIGGER: trg_customers_update
-- ============================================================================
-- PURPOSE: Auto-update 'updated_date' column when customer record is modified
-- 
-- FIRES: BEFORE UPDATE on customers table
--   For each row being updated
-- 
-- ACTIONS:
--   1. Set :NEW.updated_date := SYSDATE (current timestamp)
-- 
-- EXAMPLE SCENARIO:
--   UPDATE customers SET name = 'Jane Doe' WHERE customer_id = 1;
--   Result: updated_date automatically set to SYSDATE
-- ============================================================================

CREATE OR REPLACE TRIGGER trg_customers_update
BEFORE UPDATE ON customers
FOR EACH ROW
BEGIN
	:NEW.updated_date := SYSDATE;
END trg_customers_update;
/
```

**Checklist:**
- [ ] PURPOSE documented
- [ ] FIRES section (BEFORE/AFTER, INSERT/UPDATE/DELETE, FOR EACH ROW)
- [ ] ACTIONS numbered
- [ ] Example scenario shown

---

## ✅ VALIDATION REQUIREMENTS

### Before Every Commit

Run: `python3 scripts/validate-oracle-documentation.py`

This checks:
- ✅ All tables have comments on all columns
- ✅ All procedures have PURPOSE documented
- ✅ All functions have RETURNS documented
- ✅ No bare SQL without explanation
- ✅ Complex sections have step-by-step comments
- ✅ Examples provided where helpful

### When in Doubt

**Ask the user in the skill:**

```python
# In your skill code:
if documentation_unclear:
    ask_user("For this stored procedure, what does it do? Who calls it? What's the expected input/output?")
    document_response()
```

---

## 📐 LENGTH GUIDELINES

- **Column comments:** 1-2 sentences max
- **Procedure headers:** 5-10 lines (PURPOSE + PARAMS + EXCEPTIONS)
- **Logic flow:** Number steps, explain WHY not just WHAT
- **Complex calculations:** Explain business logic (e.g., why multiply by 1.21 for tax)

**Goal:** A new developer can understand the code in 2-3 minutes without asking questions.

---

## 🚫 Anti-Patterns (DON'T DO THIS)

```sql
-- ❌ BAD: No documentation
CREATE TABLE customers (customer_id NUMBER, name VARCHAR2(100));

-- ❌ BAD: Vague comments
-- updates the total
-- calculate stuff
-- do some logic

-- ❌ BAD: Complex logic with no explanation
SELECT ... FROM ... WHERE x > 5 AND y < 10 AND TRUNC(z) = ...
-- Why 5? Why 10? What does TRUNC(z) filter for?

-- ❌ BAD: Procedure with no explanation of inputs/outputs
CREATE OR REPLACE PROCEDURE do_stuff(p_a IN NUMBER, p_b OUT NUMBER) IS ...
```

---

## ✅ Good Examples

See examples above (TABLES, PROCEDURES, FUNCTIONS sections).

---

## 📋 CHECKLIST FOR EVERY ORACLE/APEX SKILL

Before pushing code:

- [ ] Every table has COMMENT ON COLUMN for each column (Oracle syntax)
- [ ] Every procedure has PURPOSE, PARAMETERS, EXCEPTIONS documented
- [ ] Every function has PURPOSE, PARAMETERS, RETURNS, LOGIC FLOW documented
- [ ] Complex SQL has step-by-step comments
- [ ] Business logic explained (WHY, not just WHAT)
- [ ] Validation script passes: `python3 scripts/validate-oracle-documentation.py`
- [ ] If any doubt, user was asked for clarification
- [ ] Examples provided where helpful

---

## 📞 Questions?

If documentation requirements are unclear:
1. Ask user in the skill
2. Document their response
3. Update this policy if new pattern emerges

---

**Policy Version:** 1.0  
**Last Updated:** 2026-08-21  
**Status:** MANDATORY for all Oracle/APEX skills  
**Maintained by:** Security & Code Quality Team
