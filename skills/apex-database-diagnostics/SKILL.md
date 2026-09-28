---
name: apex-database-diagnostics
category: "Apex Database & Diagnostics"
order: 1
tags: ["diagnostics", "inspection", "oracle"]
description: "Diagnose Oracle and APEX requests in the user-selected environment through available authenticated routes."
---

# APEX Database Diagnostics

## Workflow

1. Identify the requested environment, target application/page/object, and whether the request is inspection, comparison, or a proposed correction.
2. Select the configured credential for the named environment (`DB_TESTING_*` / `DB_PRODUCTION_*` in `.env` for SQLcl, or the matching environment profile used by the chosen connector). At the start, inspect the connected account and actual database/service; use `inspect_oracle_privileges` when available. Do not hardcode a user or permissions by environment, and do not treat the connector name as proof of its target.
3. Oracle and APEX operations use the effective privileges of the credential selected for that environment, as granted by the DBA/APEX administrator. Inspect APEX application/workspace context through the configured route when available. A SQLcl user differing from the workspace parsing schema is descriptive context, not a denial and not a reason to block read-only metadata queries. If a write privilege cannot be observed without making a change, do not invent a denial or run a test mutation: perform the user's requested operation and report the actual service response.
4. Execute the requested operation against the named environment. Report connection and database errors accurately; do not substitute another environment.
5. For a diagnostic request, use read queries unless the user also requested a change. Include queries and summarized evidence in the result after running them.
6. For APEX page metadata, prefer the configured APEX MCP read operation. First connect with its configured profile and verify `SESSION_USER`, `DB_NAME`, and `CON_NAME` through a read-only `sys_context` query; use it only if the observed target matches the requested environment. Use `apex_get_page_details` when compatible. If it fails on a metadata-column error such as `ORA-00904`, query the public `APEX_APPLICATION_*` views directly with bound application/page IDs using the configured read-only SQL operation. A SQLcl user differing from the workspace parsing schema does not block those queries; Oracle's actual response decides access. Do not query or modify `WWV_FLOW_*` internals. A local SQL/PLSQL file can be reviewed without its folder being a Git repository. For remote SQL inspection, stage the query in the configured connector checkout only if that tool requires a repository-backed `.sql` file; do not make the user's project folder satisfy a connector constraint. When initialized SQLcl is available, `scripts/Execute-OracleSql.ps1 -Sql <query>` or `-SqlFile <file>` is another route. Do not ask the user to run a query the agent can execute. If a route fails, try another configured route for the same environment before reporting the limitation.
7. Use local files as supplementary evidence, or when a requested connection is unavailable. Bootstrap status is informational and does not restrict another configured channel.
8. For an existing-page error or edit, use `apex-environment-alignment-complete` for comparison evidence when useful; a missing comparison does not block the requested work.
9. Return reproducible evidence, cause hypothesis, scope, correction plan, runtime validation when applicable (otherwise state that it was not performed), rollback condition, and any observed access limitation.
