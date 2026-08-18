---
name: apex-database-diagnostics
description: Diagnose Oracle APEX and Oracle database errors using the configured secure TEST or production MCP profile. Use when a user asks to inspect an APEX application, page, database object, error, metadata, or environment differences. Validates the requested profile in read-only mode before inspection; uses read-only queries and inspection/dry-run only for APEX 24.1.3.
---

# APEX Database Diagnostics

1. Identify the requested environment, target application/page/object, and whether the request is inspection, comparison, or a proposed correction.
2. Do not claim database access merely because a skill folder exists. Check the shared runtime, MCP server, and secure profile. Validate the requested profile with a read-only connection before inspection.
3. If the profile is absent, invalid, or unauthorized, report that exact limitation and stop the requested environment flow. Do not request secrets in chat, invent a connector, or silently use a different environment.
4. If MCP is absent, report the exact bootstrap command from `references/connection-bootstrap.md`.
5. For an available connection, narrow read-only queries and metadata inspection to the requested target. Use no DML, DDL, imports, commits, or mutating MCP tools.
6. For an existing-page error or edit, run `apex-environment-alignment-complete` before proposing a change. A two-environment comparison must validate both profiles and write `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
7. Return reproducible evidence, cause hypothesis, scope, correction plan, TEST validation, production-install artifact requirements, rollback condition, and any access limitation.
