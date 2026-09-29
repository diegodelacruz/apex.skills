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
in `.env` or the configured credential store used by the selected connector,
and the privileges granted to that account by the DBA. Do not hardcode a user's
name or a permission matrix by environment. Do not infer access from a profile's
presence, tool label, role name, or prior run.

For a simple read request, verify the actual account and database/service once
for the selected environment before reading object contents. Reuse verified
evidence for the same live session; if it is not yet verified, make one minimal
session check and then run the narrow query immediately. Do not delay a read
with a broad environment inventory, privilege
enumeration, or workspace diagnostic unless the target or route needs it. For
writes, inspect effective Oracle privileges when the route exposes them (for example,
`inspect_oracle_session` or `inspect_oracle_privileges`); the operation itself
is still decided by Oracle/APEX. These checks report observed capabilities;
they do not ask for a second approval. Never substitute another environment
silently.

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

- Act on requests immediately within the selected credential's effective
  privileges. Do not ask for
  permission to perform operations the user requested, or ask them to choose a
  skill, workflow, or execution mode.
- Infer application, page, schema, and environment when clear. Ask only for
  information that is genuinely ambiguous or necessary to identify the target.
- Use database metadata, App Builder, MCP, SQLcl, exports, or the browser as
  available and applicable. Prefer direct evidence from the requested environment.
- For a diagnostic request, inspect without making unrequested changes. For a
  requested write, perform that write and report its result.

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
