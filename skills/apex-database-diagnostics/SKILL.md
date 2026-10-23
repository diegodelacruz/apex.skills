---
name: apex-database-diagnostics
category: "Apex Database & Diagnostics"
order: 1
tags: ["diagnostics", "inspection", "oracle"]
description: "Diagnose Oracle and APEX requests, including data present at a source but missing or wrong downstream, in the user-selected environment through available authenticated routes."
---

# APEX Database Diagnostics

## Workflow

1. Identify the requested environment, target application/page/object, and whether the request is inspection, comparison, or a proposed correction.
2. Select the requested profile from the repository-root `.env` (`DB_TESTING_*` / `DB_PRODUCTION_*`). Use a repository-managed MCP route only when its launcher loads that same profile; do not substitute a connector-specific profile or process environment as another credential source. Before reading object contents, confirm the actual account and destination with one minimal session check unless they were already verified on this live connection. For a complete page review, `execute_readonly_batch` includes session/schema/service identity by default in the same connection as the page reads, so do not make a separate identity call first. Then query the requested object immediately. Do not run `inspect_environment`, `inspect_oracle_privileges`, or a separate workspace diagnostic unless a concrete ambiguity or failure makes it useful. Do not hardcode a user or permissions by environment, and do not treat the connector name as proof of its target. If identity or destination does not match, do not query the object or use/present results from that route.
3. Oracle and APEX operations use the effective privileges of the credential selected for that environment, as granted by the DBA/APEX administrator. Do not inspect grants before, during, or after a requested operation; submit it and report the actual service response, including privilege errors. Inspect grants only when the user explicitly requests them or asks to diagnose an observed access error. Inspect APEX application/workspace context only when the requested read or selected route requires it. A SQLcl user differing from the workspace parsing schema is descriptive context, not a denial and not a reason to block read-only metadata queries.
4. Execute the requested operation against the named environment. Report connection and database errors accurately; do not substitute another environment.
5. Treat requests to review, inspect, or show data or specifications as read-only. Run the requested read immediately after the minimal destination check in step 2; do not run a change, QA, inventory, privilege, workspace, or general validation workflow for a simple read. Include the requested result and concise evidence. If the user asks to diagnose a problem, use the additional analysis steps needed to answer that diagnosis.
6. For a complete APEX page review, send the verified one-line SELECT statements in `references/page-snapshot-queries.md` together in one `apex-controlled-mcp.execute_readonly_batch` call, with the explicit environment, `application_id` and `page_id` integer binds, and `include_identity=true` (the default). This returns identity and one independently marked result per query from one SQLcl session. The batch validates every query before connecting, runs one read-only transaction, and reports an Oracle error per query while continuing the remaining reads. It accepts at most 25 SELECT statements and 100000 total query characters. For a single targeted read, continue to use `execute_readonly_query`. `apex_get_page_details` remains useful when compatible. Use the public `APEX_APPLICATION_*` views; do not query or modify `WWV_FLOW_*` internals. A SQLcl user differing from the workspace parsing schema does not block these reads. If a helper fails with `ORA-00904` or `ORA-20987`, report that helper error and rely on the direct query's actual result.

   `apex-controlled-mcp.execute_readonly_batch` accepts up to 25 one-line SELECT statements with a total of at most 100000 characters, shared integer binds, and optional identity; use it for a full page snapshot. `execute_readonly_query` remains the single-SELECT route. Both use an Oracle read-only transaction and require no SQL file. `execute_sql_file` accepts only an existing `.sql` file inside the MCP server checkout (`apex.skills`), with a path relative to that checkout; use it for DDL/DML/PLSQL. For write artifacts, if the user's project is elsewhere, create a temporary file in the MCP checkout (for example `.codex-tmp/<name>.sql`) and pass that relative path; do not retry an absolute path outside the checkout. Remove temporary files after capturing results unless requested as saved evidence. If a route fails, try another configured route for the same environment before reporting the limitation. Do not ask the user to run a query the agent can execute.
7. Use local files as supplementary evidence, or when the `.env`-backed requested connection is unavailable. Bootstrap status is informational and does not change the credential source.
8. For an existing-page error or edit, use `apex-environment-alignment-complete` for comparison evidence when useful; a missing comparison does not block the requested work.
9. For a simple read or object/specification display, return the requested information, observed destination, and any actual access limitation; do not generate a correction plan, rollback discussion, or change artifacts. For an error/performance diagnosis or a requested correction, return evidence and analysis relevant to that task. When a correction is plausible, retain compact live-change context so it can be reused if the user confirms the change. Do not create files or modify the target during diagnosis.

## Data discrepancies: Trazabilidad End-to-End

When a record exists at a source but is missing, duplicated, or wrong at a
screen, report, process, interface, file, or target table ("no aparece", "no
cuadra", "en A sí y en B no"), follow [the domain-agnostic TE2E method](references/trazabilidad-end-to-end.md).
Use [the Oracle/APEX adapter](references/trazabilidad-adaptador-oracle-apex.md)
for the read-only probes and [the trace-map template](assets/mapa-trazabilidad.template.md)
for the deliverable. Fix a witness record and a control record, verify both
ends, discover the real flow from both directions, and locate the first stage
where the witness diverges before naming a cause. Classify the result with
codes D0–D7 or DX. Do not declare configuration, filters, or permissions the
cause until that mechanism has been evaluated against the witness record.
Flows with at most two stages use the lightweight mode. The method is a
diagnosis: it runs immediately, stays read-only, never re-runs processes, and
hands any confirmed correction to the live-change protocol with its trace
context intact. It does not apply to simple reads, execution errors without a
data discrepancy, or performance work.

## Historical memory and current blockers

Use memory from earlier tasks as context or a query hint only. A previous
`RUNTIME_NOT_INSTALLED`, workspace-context error, SQL runner rejection,
connection failure, or privilege result is not evidence that the same condition
still exists. Check current capability once on the selected route; if a route
fails, try a configured route for the same environment. Do not repeat expensive
historical probes when their inputs have not changed, and do not stop based
only on a past failure. Call the task blocked only after the current supported
routes fail; state which current attempt produced that result.
