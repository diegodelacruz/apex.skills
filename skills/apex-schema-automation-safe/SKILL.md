---
name: apex-schema-automation-safe
category: "Apex Database & Schema"
order: 20
tags: ["database", "schema", "ddl", "automation", "full-stack", "approval-gated"]
description: "Create, modify, and drop Oracle database objects (tables, views, indexes, procedures, functions, packages) with full control and governance."
---

# Safe Oracle Schema Automation

Activate this workflow when the user requests to create, modify, or drop Oracle database objects: tables, views, indexes, sequences, procedures, functions, or packages—in TEST or Production, with permission-aware execution.

## Modes

Choose the smallest mode that fits the request:

- **Assistant Mode**: User describes the schema in natural language (e.g., "create an employees table with id, name, salary, and hire date"). Claude generates the DDL specification and shows it for approval before execution.
- **Expert Mode**: User provides a JSON specification or Python `ApexSchemaSpec` object with exact control over all column properties, constraints, data types, and behaviors.
- **Hybrid Mode**: User sketches the schema; Claude generates a draft DDL; user refines it; approval gates execution.

## Required inputs

Require:
- Target Oracle database version (19c, 21c, 23c+)
- Environment (TEST or Production) — **Production requires separate approval**
- Schema owner (user running the DDL, default: SCOTT)
- Object type(s): tables, views, indexes, sequences, procedures, functions, packages
- Columns, constraints, data types, column defaults (by mode)
- User roles and permissions (schema owner must have CREATE/ALTER/DROP privileges)
- Acceptance criteria and test plan
- Explicit approval before execution, modification, or deletion

## Workflow

### Pre-flight validation

1. Confirm Oracle version: 19c+ with oracledb driver configured.
2. Verify credentials and connection to target database.
3. Validate schema owner has required privileges (CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE SEQUENCE, CREATE INDEX).
4. Check if target objects already exist (for CREATE, must not exist; for ALTER/DROP, must exist).
5. For Production: confirm separate authorization (not just TEST approval).
6. List existing objects in schema to prevent naming collisions.

### Specification generation (Assistant Mode)

1. Interview: business purpose, data structure, relationships, constraints, performance requirements, retention policy.
2. Infer: columns, data types, constraints (PK, FK, CHECK, UNIQUE, NOT NULL), indexes, views for common queries, procedures for frequent operations.
3. Generate DDL specification using `ApexSchemaSpec` builder classes.
4. Show DDL to user: table structure, indexes, views, procedures with estimated size and complexity.
5. Pause for approval or refinement.

### Expert Mode

1. User provides JSON spec (or Python dict matching `ApexSchemaSpec` schema).
2. Validate schema: required fields, data types, constraints exist, column references, foreign key targets.
3. Show parsed DDL to user.
4. Pause for approval or correction.

### Creation / Modification / Deletion

1. Connect to Oracle database via oracledb (credentials from keyring, never hardcoded).
2. Execute DDL in order:
   - **Create objects**: Tables → Indexes → Views → Sequences → Procedures → Functions → Packages (dependency order).
   - **Modify objects**: ALTER TABLE (add/drop columns), ALTER CONSTRAINT, etc.; preserve existing data unless explicitly dropping.
   - **Drop objects**: Sequences → Packages → Functions → Procedures → Views → Indexes → Tables (reverse order, handle FK dependencies).
3. Capture audit trail: timestamp, user, object names, DDL executed, row counts affected.
4. Verify execution: query data dictionary (ALL_TABLES, ALL_VIEWS, ALL_PROCEDURES, etc.) to confirm objects exist.

### Validation and rollback

1. Post-execution: run data dictionary queries to confirm object existence and structure.
2. If execution fails: provide error details (constraint violation, insufficient privileges, invalid SQL), suggest fixes, offer rollback to pre-operation snapshot.
3. If user requests rollback: restore from database backup or provide step-by-step manual rollback instructions.

## Non-negotiable safeguards

1. **No Production without explicit approval.** Changes to Production require separate, documented approval step outside this workflow. TEST changes require less friction; Production changes require confirmation of environment AND separate authorization before executing.
2. **Preserve existing data.** Modification mode never drops columns/indexes/views unless the user explicitly requests it. Show diff before applying.
3. **No hardcoded credentials.** All database connections use keyring-managed profiles (via `run_apex_mcp_with_profile.py`). Never embed passwords in DDL, logs, or scripts.
4. **Validate permissions.** Check that schema owner has CREATE/ALTER/DROP on target objects. If permission denied, show clear error and do NOT attempt workarounds.
5. **Handle constraints and dependencies.** Tables with FK must create parent table first; dropping a table with FK requires CASCADE or explicit FK removal first. Procedures/functions must reference existing tables; views must reference existing tables/views.
6. **Rollback on error.** If any DDL statement fails, roll back the entire transaction (wrapped in COMMIT/ROLLBACK). Provide rollback instructions to user.
7. **Audit trail.** Every DDL execution is recorded in `.bitacora.json` with timestamp, user, schema, object names, DDL statements, success/failure status, and user roles.

## Output

Return:
- Confirmation of objects created/modified/dropped with names and types.
- DDL statements executed (for audit and version control).
- Data dictionary verification (e.g., "Table EMPLOYEES created with 10 columns, 2 indexes, 1 FK constraint").
- Audit trail entry (auto-captured by pre-commit hook).
- Test plan: objects accessible? constraints enforced? procedures/functions callable? indexes present? indexes used by optimizer?
- Rollback instructions if execution failed.
- Acceptance checklist for user approval.

## Specifications and examples

### Assistant Mode example

```
User: "Create an employees table in TEST with columns: id (number, PK), name (varchar 100, not null),
salary (number, 2 decimals), department (varchar 50), hire_date (date with default today).
Add an index on hire_date. Create a view for employees hired in last 30 days."

Claude generates:
{
  "schema": { "owner": "SCOTT" },
  "tables": [
    {
      "table_name": "employees",
      "columns": [
        { "name": "emp_id", "type": "NUMBER", "nullable": false },
        { "name": "emp_name", "type": "VARCHAR2(100)", "nullable": false },
        { "name": "salary", "type": "NUMBER(10,2)" },
        { "name": "department", "type": "VARCHAR2(50)" },
        { "name": "hire_date", "type": "DATE", "default": "TRUNC(SYSDATE)" }
      ],
      "constraints": [
        { "name": "pk_emp", "type": "PRIMARY KEY", "columns": ["emp_id"] }
      ]
    }
  ],
  "indexes": [
    { "name": "idx_hire_date", "table": "employees", "columns": ["hire_date"] }
  ],
  "views": [
    { "name": "v_recent_hires", "query": "SELECT * FROM employees WHERE hire_date >= TRUNC(SYSDATE) - 30" }
  ]
}

User approves → DDL generated and executed in TEST.
```

### Expert Mode example

User provides JSON:
```json
{
  "schema": { "owner": "SCOTT" },
  "tables": [{
    "table_name": "orders",
    "columns": [
      { "name": "order_id", "type": "NUMBER", "precision": 10, "nullable": false },
      { "name": "customer_id", "type": "NUMBER", "nullable": false },
      { "name": "order_date", "type": "DATE", "default": "SYSDATE" },
      { "name": "total_amount", "type": "NUMBER", "precision": 12, "scale": 2 }
    ],
    "constraints": [
      { "name": "pk_orders", "type": "PRIMARY KEY", "columns": ["order_id"] },
      { "name": "fk_customer", "type": "FOREIGN KEY", "columns": ["customer_id"], "references": "customers(customer_id)", "on_delete": "CASCADE" }
    ]
  }],
  "procedures": [{
    "name": "create_order",
    "params": [
      { "name": "p_customer_id", "mode": "IN", "type": "NUMBER" },
      { "name": "p_amount", "mode": "IN", "type": "NUMBER" }
    ],
    "code": "BEGIN INSERT INTO orders (customer_id, total_amount) VALUES (p_customer_id, p_amount); COMMIT; END;"
  }]
}
```

Claude validates schema → Shows parsed DDL → User approves → Objects created.

## Security and limits

- **No DDL on system tables.** SYS, SYSTEM, SYSAUX objects cannot be modified.
- **No data as DDL.** Procedures/functions can insert/update data, but only via DML inside the stored code, never via raw INSERT in DDL.
- **No unauthorized privilege grants.** Users cannot grant CONNECT/RESOURCE/DBA to others; only schema-level operations.
- **Credentials never logged.** Database password and connection strings are never printed or logged.
- **Audit trail immutable.** `.bitacora.json` is append-only and captured at commit time; cannot be edited after creation.
- **Row limits on large operations.** Very large tables (>100M rows) must be approved separately; TRUNCATE/DROP on large tables requires extra confirmation.

## Upstream references

- `scripts/apex_schema_generator.py` — Builder classes and DDL generation
- `scripts/run_apex_mcp_with_profile.py` — Keyring-managed credential loading
- `.upstreams/managed/apex-mcp/` — Oracle APEX MCP (Model Context Protocol)
- Oracle 19c+ Data Dictionary views: `ALL_TABLES`, `ALL_VIEWS`, `ALL_INDEXES`, `ALL_PROCEDURES`, `ALL_FUNCTIONS`, `ALL_OBJECTS`

## Related skills

- **apex-page-automation-safe** — Create APEX pages that use these database objects.
- **oracle-data-change-governance-final** — Govern DML (INSERT/UPDATE/DELETE) changes after schema is created.
- **apex-environment-alignment-complete** — Sync schema structures between TEST and Production.
- **apex-database-diagnostics** — Diagnose database performance and errors.
