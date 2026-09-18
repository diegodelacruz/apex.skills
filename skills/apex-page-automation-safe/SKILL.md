---
name: apex-page-automation-safe
category: "Apex Engineering & Design"
order: 19
tags: ["page-creation", "automation", "design", "full-stack", "approval-gated"]
description: "Create, modify, and deploy APEX pages via native export/import through SQLcl."
---

# Safe APEX Page Automation

> **Ruta de ejecución:** genera el export SQL nativo de la página APEX y lo
> despliega mediante `scripts/Deploy-ApexPage.ps1` (SQLcl). No escribe
> directamente en tablas `WWV_FLOW_*`. Requiere conexión Oracle configurada
> con `scripts/Initialize-OracleConnection.ps1`.

Activate this workflow when the user requests to create, modify, or delete one or more APEX pages with specific components, items, buttons, processes, validations, or dynamic actions.

## Modes

Choose the smallest mode that fits the request:

- **Assistant Mode**: User describes the page in natural language (e.g., "a login form with email and password"). Claude generates the JSON specification and shows it for approval before creation.
- **Expert Mode**: User provides a JSON specification or Python `ApexPageSpec` object with exact control over all properties, sequences, templates, and behaviors.
- **Hybrid Mode**: User sketches the design in natural language; Claude generates a draft specification; user refines it; approval gates creation.

## Required inputs

Require:
- Target APEX version (confirm **24.1.3** only)
- Application ID and environment (TEST or Production)
- Page number(s) and type(s) (BLANK, FORM, REPORT, DASHBOARD, etc.)
- Regions, items, buttons, processes, validations, dynamic actions (by mode)
- User roles and permissions affected
- Acceptance criteria and test plan
- Explicit approval before creation, modification, or deletion

## Workflow

### Pre-flight validation

1. Confirm APEX version: 24.1.3+ with apex-mcp configured.
2. Verify application exists and page number is available (not already in use).
3. Validate credentials: database connection, workspace access, schema authorization.
4. List existing pages to prevent collisions.
5. If modifying or deleting an existing page, capture current state for rollback.
6. **For existing applications:** call `apex_open_app(app_id)` instead of `apex_create_app()`. This starts an import session targeting the existing app without recreating it, so `apex_add_page()` and all component tools work against it.

### Specification generation (Assistant Mode)

1. Interview: page purpose, users, task flow, data, role constraints, visibility conditions.
2. Infer: regions (layout), items (data entry), buttons (actions), processes (server-side logic), validations (data quality), dynamic actions (UX flow).
3. Generate JSON specification using `ApexPageSpec` builder classes.
4. Show specification to user: page structure, item types, buttons, processes in detail.
5. Pause for approval or refinement.

### Expert Mode

1. User provides JSON spec (or Python dict matching `ApexPageSpec` schema).
2. Validate schema: required fields, data types, cross-references (regions exist before items reference them).
3. Show parsed specification to user.
4. Pause for approval or correction.

### Creation / Modification / Deletion

1. Load Oracle connection: `. scripts/Initialize-OracleConnection.ps1`.
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
6. Verify deployment: confirm exit code 0 and test the page in the browser.

### Validation and rollback

1. Post-creation: run `APEX_PAGE_EXPORT` or query `wwv_flow_steps` to confirm page exists with correct name, type, and component count.
2. If creation fails: provide error details, suggest fixes, offer rollback.
3. If user requests rollback: restore from pre-operation snapshot (database-level or application export).

## Non-negotiable safeguards

1. **No production without explicit approval.** Changes to Production require separate, documented approval step. TEST changes require less friction; Production changes require confirmation of environment before executing.
2. **Preserve existing data.** Modification mode never deletes items/regions/buttons/processes unless the user explicitly requests it. Show diff before applying.
3. **No hardcoded credentials.** All APEX connections use keyring-managed profiles (via `run_apex_mcp_with_profile.py`). Never embed passwords in specifications, logs, or scripts.
4. **Validate cross-references.** Items must reference existing regions; buttons must reference valid actions; processes must reference valid items or buttons; dynamic actions must reference existing items.
5. **Rollback on error.** If any step fails, offer to restore the snapshot or provide step-by-step manual rollback instructions.
6. **Audit trail.** Every page creation, modification, or deletion is recorded in `control-proyecto/.bitacora.json` with timestamp, user, app_id, page_id, changes, and outcome.

## Output

Return:
- Confirmation of page created/modified/deleted with ID and name.
- JSON specification (for audit and version control).
- Audit trail entry (auto-captured by pre-commit hook).
- Test plan: pages accessible? items functional? buttons work? processes execute? validations trigger? dynamic actions respond?
- Rollback instructions if creation failed.
- Acceptance checklist for user approval.

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

User approves → Page created in APEX.
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

Claude validates schema → Shows parsed spec → User approves → Page created.

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
- `scripts/controlled_capabilities.py` — Authorization and preflight checks

## Related skills

- **apex-blueprint-design-safe** — Design page structure before automation (approval gate).
- **apex-export-qa-safe** — QA and export page definitions after creation.
- **apex-engineering-safe** — Inspect existing applications and exports.
- **oracle-data-change-governance-final** — Govern data changes if processes interact with user tables.
