---
name: apex-database-diagnostics
category: "Apex Database & Diagnostics"
order: 1
tags: ["diagnostics", "inspection", "oracle", "read-only"]
description: "Diagnose Oracle and APEX errors with read-only TEST or production inspection."
---

# APEX Database Diagnostics

## Workflow

1. Identify the requested environment, target application/page/object, and whether the request is inspection, comparison, or a proposed correction.
2. The full `apex-mcp` upstream is not an approved diagnostic connection. Do not register, start, or rely on it; use only an explicitly authorized, technically constrained connection when one exists.
3. If the request requires database inspection, validate the requested profile through the permitted read-only path. If it is absent, invalid, or unauthorized, report that exact limitation and stop only the requested database flow; do not request secrets or silently substitute another environment. A static review of supplied local SQL/PLSQL does not require a database profile or connection.
4. Execute only narrow read-only queries through an authorized connection when database inspection is requested. Include executed queries and summarized evidence in the result only after running them.
5. A local SQL/PLSQL file can be reviewed without its folder being a Git repository. Do not require `.git`, `git status`, or repository metadata for static inspection; use Git only when the user asks for history, branch, or change provenance. Treat the supplied file as evidence and state when database/runtime validation was not performed. This permission covers static inspection only; execution or deployment still requires its separate authorized workflow and controls.
6. Use local files as supplementary evidence, or when the requested connection validation failed. For bootstrap limits, refer to `references/connection-bootstrap.md`.
7. For an existing-page error or edit, run `apex-environment-alignment-complete` before proposing a change. A two-environment comparison must validate both profiles and write `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
8. Return reproducible evidence, cause hypothesis, scope, correction plan, TEST/runtime validation when applicable (otherwise state that it was not performed), production-install artifact requirements when applicable, rollback condition, and any access limitation.
