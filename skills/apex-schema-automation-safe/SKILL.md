---
name: apex-schema-automation-safe
category: "Apex Database & Schema"
order: 20
tags: ["database", "schema", "ddl", "automation", "full-stack"]
description: "Create, modify, and drop Oracle database objects via SQLcl with governance and authorization checks."
---

# Safe Oracle Schema Automation

> **Ruta de ejecución:** genera archivos SQL versionables y los ejecuta mediante
> `scripts/Execute-OracleSql.ps1` (SQLcl). La conexión se configura con
> `scripts/Initialize-OracleConnection.ps1`. Para PL/SQL usa `-ShowErrors`.
>
> **Ambiente por defecto: TEST.** Si el usuario no especifica ambiente, usar
> `--environment test`. Solo usar production cuando el usuario lo solicite
> explícitamente.

Activate this workflow when the user requests to create, modify, or drop Oracle database objects: tables, views, indexes, sequences, procedures, functions, or packages.

## Estándar de artefactos SQL

Antes de ejecutar o entregar cada archivo SQL/PLSQL, aplicar
`docs/reglas-formateo-canonicas.md`: código no literal en minúsculas y
tabuladores físicos (ancho visual cuatro) para toda sangría; nunca espacios al
inicio. Conservar literalmente comentarios, literales y nombres entre comillas.
Ejecutar `skills/oracle-data-change-governance-final/scripts/validate_sql_style.py`
sobre el archivo: `STYLE_FAIL` bloquea la ejecución y la entrega.

## Modification Flow

Follow the **Modification Mode Policy** and **Fluency Policy** from the APEX
Coordinator (`skills/apex/SKILL.md`).

- In step-by-step: for each DDL change, provide the exact SQL statement, explain
  what it does, and wait for the user to confirm execution.
- After each confirmed step, verify via database query
  (`ALL_OBJECTS`, `ALL_TAB_COLUMNS`, `ALL_CONSTRAINTS`, `ALL_ERRORS`).
- If the user reports an error (ORA-*, PLS-*), request the full error text,
  diagnose, and guide the correction before advancing.

## Modes

Choose the smallest mode that fits the request:

- **Assistant Mode**: User describes the schema in natural language. Generate the
  DDL specification, show it, and proceed unless the user objects.
- **Expert Mode**: User provides a JSON specification or Python `ApexSchemaSpec`
  object with exact control.
- **Hybrid Mode**: User sketches the schema; generate a draft DDL; user refines.

## Context inference

Infer these from the conversation and the database — do not interview the user:
- Oracle database version (default: 19c+)
- Environment (default: TEST)
- Schema owner (default: connected user)
- Object types, columns, constraints, data types

## Workflow

### Pre-flight validation

1. Check if target objects already exist (for CREATE, must not exist; for ALTER/DROP, must exist).
2. List existing objects in schema to prevent naming collisions.

### Specification generation (Assistant Mode)

1. Infer from context: columns, data types, constraints, indexes, views, procedures.
2. Generate DDL specification using `ApexSchemaSpec` builder classes.
3. Show DDL to user and proceed unless the user objects.

### Expert Mode

1. User provides JSON spec (or Python dict matching `ApexSchemaSpec` schema).
2. Validate schema: required fields, data types, constraints, foreign key targets.
3. Show parsed DDL to user and proceed.

### Creation / Modification / Deletion

1. Load Oracle connection: `. scripts/Initialize-OracleConnection.ps1`.
2. Generate SQL files in dependency order:
   - **Create objects**: Tables → Indexes → Views → Sequences → Procedures → Functions → Packages.
   - **Modify objects**: ALTER TABLE (add/drop columns), ALTER CONSTRAINT, etc.; preserve existing data unless explicitly dropping.
   - **Drop objects**: Sequences → Packages → Functions → Procedures → Views → Indexes → Tables (reverse order, handle FK dependencies).
3. Execute each SQL file via SQLcl:
   ```powershell
   .\scripts\Execute-OracleSql.ps1 -SqlFile "ddl\001_create_table_employees.sql"
   .\scripts\Execute-OracleSql.ps1 -SqlFile "ddl\002_create_pkg_body.sql" -ShowErrors
   ```
4. Capture audit trail: timestamp, user, object names, DDL executed.
5. Verify execution: query data dictionary via SQLcl to confirm objects exist and are VALID.

### Validation and rollback

1. Post-execution: run data dictionary queries to confirm object existence and structure.
2. If execution fails: provide error details (constraint violation, insufficient privileges, invalid SQL), suggest fixes, offer rollback to pre-operation snapshot.
3. If user requests rollback: restore from database backup or provide step-by-step manual rollback instructions.

## Non-negotiable safeguards

1. **Production requires environment confirmation.** Confirm the target is production once before executing. TEST changes proceed without extra friction.
2. **Preserve existing data.** Modification mode never drops columns/indexes/views unless the user explicitly requests it. Show diff before applying.
3. **No hardcoded credentials.** All database connections use keyring-managed profiles (via `run_apex_mcp_with_profile.py`). Never embed passwords in DDL, logs, or scripts.
4. **Validate permissions.** If permission denied, show clear error and do NOT attempt workarounds.
5. **Handle constraints and dependencies.** Tables with FK must create parent table first; dropping a table with FK requires CASCADE or explicit FK removal first. Procedures/functions must reference existing tables; views must reference existing tables/views.
6. **Rollback on error.** If any DDL statement fails, roll back the entire transaction (wrapped in COMMIT/ROLLBACK). Provide rollback instructions to user.
7. **Audit trail.** Every DDL execution is recorded in `.bitacora.json` with timestamp, user, schema, object names, DDL statements, success/failure status, and user roles.

## Output

Return:
- Confirmation of objects created/modified/dropped with names and types.
- DDL statements executed (for audit and version control).
- Data dictionary verification (e.g., "Table EMPLOYEES created with 10 columns, 2 indexes, 1 FK constraint").
- Audit trail entry (auto-captured by pre-commit hook).
- Rollback instructions if execution failed.

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
- **Row limits on large operations.** Very large tables (>100M rows): warn about impact before TRUNCATE/DROP.

## Upstream references

- `scripts/apex_schema_generator.py` — Builder classes and DDL generation (in-memory spec)
- `scripts/Initialize-OracleConnection.ps1` — Oracle connection setup (SQLcl + .env)
- `scripts/Execute-OracleSql.ps1` — SQL/DDL/PL-SQL execution via SQLcl
- `scripts/controlled_capabilities.py` — Authorization, preflight, and DDL execution checks
- Oracle 19c+ Data Dictionary views: `ALL_TABLES`, `ALL_VIEWS`, `ALL_INDEXES`, `ALL_PROCEDURES`, `ALL_FUNCTIONS`, `ALL_OBJECTS`

## Related skills

- **apex-page-automation-safe** — Create APEX pages that use these database objects.
- **oracle-data-change-governance-final** — Govern DML (INSERT/UPDATE/DELETE) changes after schema is created.
- **apex-environment-alignment-complete** — Sync schema structures between TEST and Production.
- **apex-database-diagnostics** — Diagnose database performance and errors.
