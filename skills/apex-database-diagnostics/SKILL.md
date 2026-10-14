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
2. Select the requested profile from the repository-root `.env` (`DB_TESTING_*` / `DB_PRODUCTION_*`). Use a repository-managed MCP route only when its launcher loads that same profile; do not substitute a connector-specific profile or process environment as another credential source. Before reading object contents, confirm the actual account and destination with one minimal session check unless they were already verified on this live connection. Then query the requested object immediately. Do not run `inspect_environment`, `inspect_oracle_privileges`, or a separate workspace diagnostic unless a concrete ambiguity or failure makes it useful. Do not hardcode a user or permissions by environment, and do not treat the connector name as proof of its target. If identity or destination does not match, do not query the object or use/present results from that route.
3. Oracle and APEX operations use the effective privileges of the credential selected for that environment, as granted by the DBA/APEX administrator. Do not inspect grants before, during, or after a requested operation; submit it and report the actual service response, including privilege errors. Inspect grants only when the user explicitly requests them or asks to diagnose an observed access error. Inspect APEX application/workspace context only when the requested read or selected route requires it. A SQLcl user differing from the workspace parsing schema is descriptive context, not a denial and not a reason to block read-only metadata queries.
4. Execute the requested operation against the named environment. Report connection and database errors accurately; do not substitute another environment.
5. Treat requests to review, inspect, or show data or specifications as read-only. Run the requested read immediately after the minimal destination check in step 2; do not run a change, QA, inventory, privilege, workspace, or general validation workflow for a simple read. Include the requested result and concise evidence. If the user asks to diagnose a problem, use the additional analysis steps needed to answer that diagnosis.
6. For APEX page metadata, reuse the identity/destination check from step 2 for the selected live connection, then query the requested page promptly. Use the fastest configured same-environment route that can answer the question; do not make both an inventory call and a context call as routine preflight. `apex_get_page_details` is useful when compatible. If it fails on a metadata-column error such as `ORA-00904`, query the public `APEX_APPLICATION_*` views directly with bound application/page IDs using `apex-controlled-mcp.execute_readonly_query` (one physical-line SELECT; no repository SQL artifact required), or the configured same-environment APEX SQL route. Keep each query on one line because SQLcl also accepts client commands. A SQLcl user differing from the workspace parsing schema does not block those queries; Oracle's actual response decides access. Do not query or modify `WWV_FLOW_*` internals. An `ORA-20987`/invalid security group from the context-inspection helper is a failure of that helper, not proof that the metadata query failed: continue through the direct query tool, which does not depend on that helper, and report the query's actual result.

   `apex-controlled-mcp.execute_readonly_query` accepts one SELECT with integer binds and runs it in an Oracle read-only transaction; use it for inline metadata reads without creating a file. `execute_sql_file` accepts only an existing `.sql` file inside the MCP server checkout (`apex.skills`), with a path relative to that checkout; use it for DDL/DML/PLSQL. For write artifacts, if the user's project is elsewhere, create a temporary file in the MCP checkout (for example `.codex-tmp/<name>.sql`) and pass that relative path; do not retry an absolute path outside the checkout. Remove temporary files after capturing results unless requested as saved evidence. If a route fails, try another configured route for the same environment before reporting the limitation. Do not ask the user to run a query the agent can execute.
7. Use local files as supplementary evidence, or when the `.env`-backed requested connection is unavailable. Bootstrap status is informational and does not change the credential source.
8. For an existing-page error or edit, use `apex-environment-alignment-complete` for comparison evidence when useful; a missing comparison does not block the requested work.
9. For a simple read or object/specification display, return the requested information, observed destination, and any actual access limitation; do not generate a correction plan, rollback discussion, or change artifacts. For an error/performance diagnosis or a requested correction, return evidence and analysis relevant to that task. When a correction is plausible, retain compact live-change context so it can be reused if the user confirms the change. Do not create files or modify the target during diagnosis.

## Historical memory and current blockers

Use memory from earlier tasks as context or a query hint only. A previous
`RUNTIME_NOT_INSTALLED`, workspace-context error, SQL runner rejection,
connection failure, or privilege result is not evidence that the same condition
still exists. Check current capability once on the selected route; if a route
fails, try a configured route for the same environment. Do not repeat expensive
historical probes when their inputs have not changed, and do not stop based
only on a past failure. Call the task blocked only after the current supported
routes fail; state which current attempt produced that result.
