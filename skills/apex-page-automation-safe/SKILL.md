---
name: apex-page-automation-safe
category: "Apex Engineering & Design"
order: 19
tags: ["page-creation", "automation", "design", "full-stack"]
description: "Create, modify, and deploy APEX pages via native export/import through SQLcl."
---

# Safe APEX Page Automation

## Estándar de artefactos SQL y PL/SQL

Todo SQL o PL/SQL creado para una página APEX debe seguir
`docs/reglas-formateo-canonicas.md`: minúsculas fuera de literales, comentarios
y nombres entre comillas, y tabuladores físicos de ancho visual cuatro para la
sangría. No se permiten espacios iniciales. Validar cada archivo con
`skills/oracle-data-change-governance-final/scripts/validate_sql_style.py` y
reportar cualquier hallazgo junto con el resultado de Oracle/APEX.

> **Rutas disponibles:** usa export nativo de APEX, SQLcl, MCP, App Builder,
> APIs u otra herramienta configurada según la solicitud. Ninguna ruta queda
> prohibida por una regla local; Oracle/APEX decide el acceso efectivo.
>
> **Ambiente:** usar el ambiente nombrado por el usuario; si no lo especifica,
> inferirlo del contexto y luego del selector `DB_ENV`/perfil configurado. Pasar
> el ambiente resuelto explícitamente a la herramienta de ejecución.
>
> **Permisos efectivos:** los cambios APEX se ejecutan con la credencial
> configurada para el ambiente solicitado y solo si esa cuenta tiene los
> privilegios efectivos concedidos por el DBA/APEX administrator. No codificar
> restricciones por ambiente ni por nombre de usuario. Verificar al inicio la
> sesión y el contexto disponible; dejar que APEX/Oracle responda sobre el
> permiso real.

Activate this workflow when the user requests to create, modify, or delete one or more APEX pages with specific components, items, buttons, processes, validations, or dynamic actions.

## Modification Flow

Follow the credential authorization principle from the APEX Coordinator
(`skills/apex/SKILL.md`). A direct request is sufficient; do not ask for a
separate mode choice or confirmation.

- Execute requested changes in the requested sequence and environment.
- Verify through the available channel and report the observed result.
- If an operation returns an error, report it and continue with independent
  requested work where possible.

## Modes

Choose the smallest mode that fits the request:

- **Assistant Mode**: User describes the page in natural language. Generate the
  specification and show it, then proceed unless the user objects.
- **Expert Mode**: User provides a JSON specification or Python `ApexPageSpec`
  object with exact control.
- **Hybrid Mode**: User sketches the design; generate a draft; user refines.

## Context inference

Infer these from the conversation and the database — do not interview the user:
- APEX version (default: 24.1.3)
- Application ID and environment (infer from request/context or configured `DB_ENV`)
- Page number and type
- Regions, items, buttons, processes, validations, dynamic actions

## Workflow

### Pre-flight validation

1. Verify application exists and page number is available (not already in use).
2. If modifying or deleting an existing page, capture current state for rollback.
3. **For existing applications:** call `apex_open_app(app_id)` instead of `apex_create_app()`.

### Specification generation (Assistant Mode)

1. Infer from context: regions, items, buttons, processes, validations, dynamic actions.
2. Generate JSON specification using `ApexPageSpec` builder classes.
3. Show specification to user and proceed unless the user objects.

### Expert Mode

1. User provides JSON spec (or Python dict matching `ApexPageSpec` schema).
2. Validate schema: required fields, data types, cross-references.
3. Show parsed specification to user and proceed.

### Creation / Modification / Deletion

1. Resolve the requested environment and load that profile: `. .\scripts\Initialize-OracleConnection.ps1 -Environment $environment` (or omit `-Environment` only when `DB_ENV` is configured).
2. Generate the APEX page export SQL file using the native `wwv_flow_imp` format:
   - `wwv_flow_imp.import_begin(...)` with `p_default_application_id`.
   - `wwv_flow_imp_page.create_page(...)` with all regions, items, buttons, processes, validations, dynamic actions.
   - `wwv_flow_imp.import_end(...)`.
3. Save as `f{app_id}_page_{page_number}.sql` in the project apex directory.
4. Deploy via SQLcl:
   ```powershell
   .\scripts\Deploy-ApexPage.ps1 -PageFile "apex\f109_page_291.sql" -ApplicationId 109 -Page 291
   ```
   Or for inline SQL and DDL:
   ```powershell
   .\scripts\Execute-OracleSql.ps1 -SqlFile "ddl\create_table.sql"
   ```
5. Capture audit trail: timestamp, user, page ID, changes made.
6. Verify deployment: confirm exit code 0 and verify via database metadata query.

### Validation and rollback

1. Post-creation: verify with available APEX metadata, App Builder, MCP, SQLcl,
   or browser evidence.
2. If creation fails: provide error details, suggest fixes, offer rollback.
3. If user requests rollback: restore from pre-operation snapshot (database-level or application export).

## Operational guidance

1. Use the environment named by the user or resolve it from context and the configured `DB_ENV` profile when omitted.
2. Keep changes within the requested objects and operations. Perform requested deletions or replacements without adding approval requirements.
3. Keep credentials out of specifications, logs, and scripts. Use configured profiles when available.
4. Check cross-references when useful and report findings; Oracle/APEX remains the permission authority.
5. Report rollback options and audit evidence as useful operational information, not as prerequisites to execute.

## Output

Return:
- Confirmation of page created/modified/deleted with ID and name.
- JSON specification (for audit and version control).
- Audit trail entry (auto-captured by pre-commit hook).
- Rollback instructions if creation failed.

## Specifications and examples

### Assistant Mode example

```
User: "Create a login page with email and password fields, a sign-in button, and client-side validation"

Claude generates:
{
  "page": { "page_number": 1, "page_name": "Login", "page_type": "BLANK", ... },
  "regions": [
    { "region_name": "Content", "region_type": "STATIC_CONTENT", ... }
  ],
  "items": [
    { "item_name": "EMAIL", "item_type": "TEXT_FIELD", "label": "Email", "required": true, ... },
    { "item_name": "PASSWORD", "item_type": "PASSWORD", "label": "Password", "required": true, ... }
  ],
  "buttons": [
    { "button_name": "SIGNIN", "button_label": "Sign In", "button_position": "NEXT", "action": "SUBMIT", ... }
  ],
  "validations": [
    { "validation_name": "VAL_EMAIL_FORMAT", "item_name": "EMAIL", "validation_type": "ITEM_IN_VALIDATION_ERROR", "expression1": "^[^@]+@[^@]+\\.[^@]+$", ... },
    { "validation_name": "VAL_PASSWORD_NOT_EMPTY", "item_name": "PASSWORD", "validation_type": "ITEM_IN_VALIDATION_ERROR", ... }
  ],
  "dynamic_actions": [
    { "action_name": "DA_EMAIL_BLUR", "event": "BLUR", "affected_element": "EMAIL", "action_type": "EXECUTE_JAVASCRIPT", ... }
  ]
}

The agent applies the requested page in the selected environment and verifies the result.
```

### Expert Mode example

User provides:
```json
{
  "page": { "app_id": 100, "page_number": 5, "page_name": "Employee Form", "page_type": "FORM" },
  "regions": [ { "region_name": "Form Region", "region_type": "FORM", ... } ],
  "items": [ { "item_name": "EMPLOYEE_ID", "item_type": "HIDDEN", ... }, ... ],
  "processes": [ { "process_name": "SAVE_EMPLOYEE", "process_type": "PLSQL", "pl_sql_code": "INSERT INTO ...", ... } ]
}
```

The agent validates the schema, applies the requested page in the selected environment, and verifies it.

## Security and limits

- **No DDL on schema objects.** Pages can only be created within APEX, not alter table structures.
- **No unauthorized data access.** Items inherit source table authorization from the application's parsing schema.
- **No unauthorized SQL injection.** All process code and item defaults are subject to APEX's own validation (no additional escaping needed if using APEX API).
- **Credentials never logged.** Database password, wallet password, and connection strings are never printed or logged.
- **Audit trail immutable.** `.bitacora.json` is append-only and captured at commit time; cannot be edited after creation.

## Upstream references

- `scripts/apex_page_generator.py` — Builder classes and schema definitions (in-memory spec generation)
- `scripts/Initialize-OracleConnection.ps1` — Oracle connection setup (SQLcl + .env)
- `scripts/Deploy-ApexPage.ps1` — APEX page deployment via SQLcl import
- `scripts/Execute-OracleSql.ps1` — General SQL/DDL/PL-SQL execution via SQLcl
- `scripts/controlled_capabilities.py` — Optional session evidence; not a skill-level authorization gate

## Related skills

- **apex-blueprint-design-safe** — Design page structure before automation.
- **apex-export-qa-safe** — QA and export page definitions after creation.
- **apex-engineering-safe** — Inspect existing applications and exports.
- **oracle-data-change-governance-final** — Govern data changes if processes interact with user tables.
