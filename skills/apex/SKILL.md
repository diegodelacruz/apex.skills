---
name: apex
category: "Apex Coordinator"
order: 14
tags: ["coordinator", "routing", "governance"]
description: "Route Oracle and APEX requests to the smallest useful specialist workflow."
---

# APEX Coordinator

Before modifying this repository, follow `../../docs/POLITICA-EVOLUCION-ECOSISTEMA.md`.

## Credential Authorization Principle

A direct user request defines the requested action, environment, and scope. The
effective capabilities come from the credential selected for that environment
in the repository-root `.env` and the privileges granted to that account by
the DBA. Local scripts and MCP adapters must not fall back to process
environment variables or credential stores. Do not hardcode a user's
name or a permission matrix by environment. Do not infer access from a profile's
presence, tool label, role name, or prior run.

For a simple read request, verify the actual account and database/service once
for the selected environment before reading object contents. Reuse verified
evidence for the same live session; if it is not yet verified, make one minimal
session check and then run the narrow query immediately. Do not delay a read
with a broad environment inventory, privilege
enumeration, or workspace diagnostic unless the target or route needs it. For
writes, do not inspect privileges as a prerequisite or follow-up validation.
Execute the confirmed operation with the configured credential and report the
actual Oracle/APEX result, including any privilege error. Inspect grants only
when the user requests that information or asks to diagnose an observed access
error. Never substitute another environment silently.

Past-session notes are context and search hints, not current access decisions.
Connection, runtime, workspace, tool, and privilege failures can change: verify
the selected credential and route for this request, then try an available
same-environment route if one fails. A historical failure alone never blocks
the requested work. Do not repeat a known failed probe unless its inputs or
conditions changed; report a blocker only when the current attempt reproduces
it.

Keep the user's requested scope exact. Credentials do not authorize additional
changes beyond the request. Protect credentials from output, source files, and
version control.

## Fluency Policy

- A request to review, inspect, query, or show Oracle/APEX object data or
  specifications is implicitly read-only. Resolve its environment and target,
  make one minimal identity/destination check only if it has not already been
  verified on the live connection, then run the requested read immediately.
  Do not insert a change workflow, broad validation, inventory, privilege scan,
  workspace check, or approval step into a simple read.
- Before any requested mutation, present one concise confirmation containing
  the resolved environment, target, and exact action, and ask whether to
  proceed and whether a backup is wanted. Do not execute until the user has
  explicitly answered both decisions. If either answer is missing or ambiguous,
  ask only for that missing decision and wait; never infer "no backup" from
  silence. Treat the complete answer as the single confirmation; do not ask
  again unless scope changes. If backup is declined, create no backup,
  snapshot, or temporary backup artifact. Create a scoped backup only after an
  explicit yes.
- Do not make a preliminary row-count query a standard prerequisite for any
  transaction, including INSERT, UPDATE, DELETE, and MERGE. Count only when
  the user requests it or when a concrete ambiguity makes it necessary to
  determine the requested scope; ask about that ambiguity instead of silently
  expanding the operation.
- Execute confirmed requests within the selected credential's effective
  privileges; do not precheck or recheck grants before, during, or after the
  operation. Report any authorization error returned by Oracle/APEX. Inspect
  grants only when explicitly requested or when diagnosing an observed error.
  Do not ask the user to choose a skill, workflow, or execution mode.
- Infer application, page, schema, and environment when clear. Ask only for
  information that is genuinely ambiguous or necessary to identify the target.
- Use database metadata, App Builder, MCP, SQLcl, exports, or the browser as
  available and applicable. Prefer direct evidence from the requested environment.
- For a diagnostic request, inspect without making unrequested changes. For a
  requested write, obtain the one confirmation above, then perform the write
  and report its result.

## Live changes

For a conversation that moves from inspection to an explicitly confirmed
change, follow [the live-change protocol](references/live-change-protocol.md).
Keep the verified target, observed definition, impact explanation, proposed
change, rollback and validation context alive for this request. Do not restart
discovery, reload broad guidance, or create a formal project plan merely
because the user confirmed a narrow change. Use the direct path for a focused
change; do not add a preflight when the target and intended operation are
already clear. Use a change bundle and its fingerprint preflight only when the
fingerprint materially protects an existing correction or multiple objects
must be coordinated.

## Environment Policy

Use the environment named by the user. When omitted, infer it from the current
task; otherwise use the configured `DB_ENV` selector/profile. Pass the resolved
environment explicitly to tools that accept it. Never silently change
environments. A failed profile or connection is a technical result; it does not
authorize substituting another environment.

## Oracle object owner default

For every Oracle request that creates, changes, or drops schema objects, use owner
`DATA` when the user did not explicitly name an owner or schema. This default
applies even when the connected account or `CURRENT_SCHEMA` is different.
Qualify object names in generated DDL and any related DML with the selected
owner. If the user explicitly specifies another owner, use that owner. Follow
specific governance exceptions (such as backup objects in the connected user's
schema). If Oracle rejects the selected owner, report the Oracle error and do
not retry under the connected user's schema.

## Workflow

1. Classify the request by its Oracle/APEX task and interpret `<application>.<page>` as two
   identifiers when the context supports it.
2. Delegate to the smallest set of specialist skills needed, without letting their local
   approval or access rules veto the direct user request.
3. Connect using the configured credential for that environment. For a simple
   read, reuse the identity/destination check already verified for this live
   connection; otherwise make one minimal check, confirm the target, and
   immediately query the requested object. Never read object contents before
   confirming the requested destination. Skip broad environment
   inventories, privilege scans, and unrelated workspace checks. Use those diagnostics only when they resolve a
   concrete ambiguity or a failed route. For APEX metadata, a SQLcl session
   user differing from the workspace parsing schema is not itself an access
   denial; query public `APEX_APPLICATION_*` metadata views directly when the
   page-detail helper is incompatible. If a channel fails, try another
   configured channel for the same environment before concluding access is
   unavailable; never treat a tool name as proof of its target environment.
4. Report observed evidence, errors, and limitations accurately. Do not claim
   that a skill's policy restriction is an Oracle/APEX permission denial.
5. For SQL/PLSQL artifacts, use repository style and audit guidance as quality
   support. A style or governance result is not an Oracle/APEX authorization
   decision. Keep credentials out of the artifact and output.

## Response-time and prior-session evidence

For a direct request to inspect a table, database object, or APEX page, route to
the focused diagnostic skill and make the smallest useful read promptly. Avoid
serial preflight calls that do not answer the request. Historical memory may
help identify the likely object, query shape, or a past failure mode, but never
turns a past failure into a current restriction. Revalidate time-sensitive
facts on the selected credential and current route; do not repeat failed
historical steps without a changed condition. If current access fails, keep
trying configured routes for that same environment and report the actual
current error.

For a complete page review, use `execute_readonly_batch` with the verified
snapshot queries so page identity and metadata share one SQLcl connection. Keep
`execute_readonly_query` for one targeted SELECT; a separate identity call is
not needed when the batch includes identity.

Requests to show object data or specifications are simple reads: retrieve the
requested information directly after the minimal destination check, without
running a diagnostic-report workflow unless the user asks for analysis or the
initial read reveals a specific issue to investigate.
