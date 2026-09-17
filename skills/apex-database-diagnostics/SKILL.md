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
3. Validate the requested profile through the permitted read-only path before inspection. If it is absent, invalid, or unauthorized, report that exact limitation and stop only the requested environment flow; do not request secrets or silently substitute another environment.
4. Execute only narrow read-only queries through an authorized connection. Include executed queries and summarized evidence in the result only after running them.
5. Use local files as supplementary evidence, or when the requested connection validation failed. For bootstrap limits, refer to `references/connection-bootstrap.md`.
6. For an existing-page error or edit, run `apex-environment-alignment-complete` before proposing a change. A two-environment comparison must validate both profiles and write `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
7. Return reproducible evidence, cause hypothesis, scope, correction plan, TEST validation, production-install artifact requirements, rollback condition, and any access limitation.
