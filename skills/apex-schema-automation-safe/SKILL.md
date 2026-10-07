---
name: apex-schema-automation-safe
category: "Apex Database & Schema"
order: 20
tags: ["database", "schema", "ddl", "automation", "full-stack"]
description: "Create, modify, and drop Oracle database objects through available authenticated routes."
---

# Safe Oracle Schema Automation

> **Ruta de ejecución:** genera archivos SQL versionables y los ejecuta mediante
> `scripts/Execute-OracleSql.ps1` (SQLcl). La conexión se configura con
> `scripts/Initialize-OracleConnection.ps1`. Para PL/SQL usa `-ShowErrors`.
>
> Usa el ambiente indicado por el usuario; si no se indicó, resuélvelo desde el
> contexto y `DB_ENV` configurado. Pasa el ambiente resuelto explícitamente al
> ejecutor. Las operaciones disponibles dependen de los permisos efectivos de
> la credencial seleccionada.

Activate this workflow when the user requests any Oracle schema-object DDL, including CREATE, ALTER, DROP, and CREATE OR REPLACE for tables, views, indexes, sequences, triggers, synonyms, materialized views, types, procedures, functions, and packages.

## Estándar de artefactos SQL

Antes de ejecutar o entregar cada archivo SQL/PLSQL, aplicar
`docs/reglas-formateo-canonicas.md`: código no literal en minúsculas y
tabuladores físicos (ancho visual cuatro) para toda sangría; nunca espacios al
inicio. Conservar literalmente comentarios, literales y nombres entre comillas.
Ejecutar `skills/oracle-data-change-governance-final/scripts/validate_sql_style.py`
sobre el archivo y reportar los hallazgos junto con el resultado de Oracle.

## Modification Flow

Follow the credential authorization principle from the APEX Coordinator
(`skills/apex/SKILL.md`). Execute requested SQL directly in the named
environment. Do not add confirmation or permission gates. Verify through
available data dictionary queries and report Oracle's result.

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
- Environment (infer from request/context or configured `DB_ENV`)
- Schema owner (default: `DATA`; use another owner only when the user explicitly names it)
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
2. Set the target owner to `DATA` unless the user explicitly named another schema. Follow the specific governance exception that backup objects belong in the connected user's schema. This rule applies to every other request, including natural-language requests with misspelled or shorthand type names. Qualify every object name referenced by DDL (CREATE, ALTER, DROP, and CREATE OR REPLACE) and related INSERT/UPDATE/DELETE in DML (for example, `create table data.<name> ...` and `insert into data.<name> ...`) so the session user's schema cannot become an accidental default. Verify `SESSION_USER` and `CURRENT_SCHEMA` for context, but do not treat either as a reason to change the requested owner. If Oracle denies the selected owner for a non-backup object, report the actual error; never retry the operation under the connected user's schema.
3. Generate SQL files in dependency order:
   - **Create objects**: Tables → Indexes → Views → Sequences → Procedures → Functions → Packages.
   - **Modify objects**: ALTER TABLE (add/drop columns), ALTER CONSTRAINT, etc.; preserve existing data unless explicitly dropping.
   - **Drop objects**: Sequences → Packages → Functions → Procedures → Views → Indexes → Tables (reverse order, handle FK dependencies).
4. Execute each SQL file via SQLcl:
   ```powershell
   .\scripts\Execute-OracleSql.ps1 -SqlFile "ddl\001_create_table_employees.sql"
   .\scripts\Execute-OracleSql.ps1 -SqlFile "ddl\002_create_pkg_body.sql" -ShowErrors
   ```
5. Capture audit trail: timestamp, connected user, target owner, object names, DDL executed.
6. Verify execution: query data dictionary via SQLcl to confirm objects exist under the requested owner and are VALID.

### Validation and rollback

1. Post-execution: run data dictionary queries to confirm object existence and structure.
2. If execution fails: provide error details (constraint violation, insufficient privileges, invalid SQL), suggest fixes, offer rollback to pre-operation snapshot.
3. If user requests rollback: restore from database backup or provide step-by-step manual rollback instructions.

## Non-negotiable safeguards

1. Use the environment named by the user or resolve it from context and the configured `DB_ENV` profile when omitted. Oracle operations use the selected account's effective grants.
2. Keep changes within the requested objects and operations.
3. **No hardcoded credentials.** All database connections read the selected profile from the ignored repository-root `.env` (via `run_apex_mcp_with_profile.py`). Never embed passwords in DDL, logs, or scripts.
4. **Report permission results.** Oracle decides the grants for the connected account; report a returned denial and continue independent requested work.
5. **Handle constraints and dependencies.** Tables with FK must create parent table first; dropping a table with FK requires CASCADE or explicit FK removal first. Procedures/functions must reference existing tables; views must reference existing tables/views.
6. **Rollback information.** Explain rollback options when relevant. Oracle DDL may commit implicitly.
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
  "schema": { "owner": "DATA" },
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

The requested DDL is generated and executed in TEST, then verified.
```

### Expert Mode example

User provides JSON:
```json
{
  "schema": { "owner": "DATA" },
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

The agent validates the schema, applies the requested DDL in the named environment, and verifies the objects.

## Reporting and credential handling

- **Oracle enforces privileges and statement semantics.** Submit the requested operation as written and report Oracle's response; do not impose an object, statement-category, or grant allowlist in the skill.
- **Credentials never logged.** Database password and connection strings are never printed or logged.
- **Audit trail immutable.** `.bitacora.json` is append-only and captured at commit time; cannot be edited after creation.
- **Row limits on large operations.** Very large tables (>100M rows): warn about impact before TRUNCATE/DROP.

## Upstream references

- `scripts/apex_schema_generator.py` — Builder classes and DDL generation (in-memory spec)
- `scripts/Initialize-OracleConnection.ps1` — Oracle connection setup (SQLcl + .env)
- `scripts/Execute-OracleSql.ps1` — SQL/DDL/PL-SQL execution via SQLcl
- `scripts/controlled_capabilities.py` — Optional session evidence and Oracle execution helper; not an authorization gate
- Oracle 19c+ Data Dictionary views: `ALL_TABLES`, `ALL_VIEWS`, `ALL_INDEXES`, `ALL_PROCEDURES`, `ALL_FUNCTIONS`, `ALL_OBJECTS`

## Related skills

- **apex-page-automation-safe** — Create APEX pages that use these database objects.
- **oracle-data-change-governance-final** — Govern DML (INSERT/UPDATE/DELETE) changes after schema is created.
- **apex-environment-alignment-complete** — Sync schema structures between TEST and Production.
- **apex-database-diagnostics** — Diagnose database performance and errors.
