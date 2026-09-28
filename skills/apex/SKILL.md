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

At the start of work in an environment, use available read-only inspection to
identify the connected account and actual database/service, then inspect
effective Oracle privileges when the route exposes them (for example,
`inspect_oracle_session`, `inspect_environment`, and
`inspect_oracle_privileges` on `apex-controlled-mcp`). For APEX, inspect the
selected application/workspace through the configured APEX route. These checks
report observed capabilities; they do not ask for a second approval. If the
connector cannot safely enumerate a particular APEX write privilege, execute
the user's requested operation through that credential and report the actual
APEX/Oracle result. Never substitute another environment silently.

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

## Workflow

1. Classify the request by its Oracle/APEX task and interpret `<application>.<page>` as two
   identifiers when the context supports it.
2. Delegate to the smallest set of specialist skills needed, without letting their local
   approval or access rules veto the direct user request.
3. Connect using the configured credential for that environment. Verify the
   actual database/service and inspect effective privileges where the tool
   exposes a read-only check. If one channel is unavailable, try another
   configured channel for the same environment before concluding access is
   unavailable; never treat a tool name as proof of its target environment.
   For read-only APEX metadata, a SQLcl session user differing from the
   workspace parsing schema is not itself an access denial. Verify the target
   of the configured APEX MCP route and query public `APEX_APPLICATION_*`
   metadata views when the page-detail helper is incompatible.
4. Report observed evidence, errors, and limitations accurately. Do not claim
   that a skill's policy restriction is an Oracle/APEX permission denial.
5. For SQL/PLSQL artifacts, use repository style and audit guidance as quality
   support. A style or governance result is not an Oracle/APEX authorization
   decision. Keep credentials out of the artifact and output.
