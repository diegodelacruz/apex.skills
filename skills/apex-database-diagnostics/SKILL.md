---
name: apex-database-diagnostics
category: "Apex Database & Diagnostics"
order: 1
tags: ['diagnostics', 'inspection', 'oracle', 'read-only']
---

# APEX Database Diagnostics

1. Identify the requested environment, target application/page/object, and whether the request is inspection, comparison, or a proposed correction.
2. When the requested environment has a configured MCP profile, use that MCP first (`apex-mcp-test` or `apex-mcp-production`). Do not search local files or test `sqlplus`, `sqlcl`, or other clients as a substitute for an available MCP connection.
3. Validate the requested profile with a read-only MCP connection before inspection. Do not claim that an environment is unavailable until that validation actually fails. If the profile is absent, invalid, or unauthorized, report that exact limitation and stop only the requested environment flow; do not request secrets or silently substitute another environment.
4. Execute the narrow read-only metadata and source queries yourself through MCP. Do not give the user SQL to run or ask them to paste results when the requested MCP profile is available. Include executed queries and summarized evidence in the result only after running them.
5. Use local files only as supplementary evidence after database inspection, or when the requested connection validation failed. If MCP is absent, report the exact bootstrap command from `references/connection-bootstrap.md`.
6. For an existing-page error or edit, run `apex-environment-alignment-complete` before proposing a change. A two-environment comparison must validate both profiles and write `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
7. Return reproducible evidence, cause hypothesis, scope, correction plan, TEST validation, production-install artifact requirements, rollback condition, and any access limitation.
