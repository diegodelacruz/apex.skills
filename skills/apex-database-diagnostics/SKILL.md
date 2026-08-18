---
name: apex-database-diagnostics
description: Diagnose Oracle APEX and Oracle database errors using the configured secure TEST or production MCP profile. Use when a user asks to analyze an APEX/Oracle error, inspect database metadata, compare environments, or prepare a correction. Verifies runtime, secure profile, and MCP availability first; uses read-only queries and inspection/dry-run only for APEX 24.1.3.
---

# APEX Database Diagnostics

1. Do not claim database access merely because a skill folder exists. Check that the shared skills runtime, upstreams, secure profile, and client MCP server are available.
2. If MCP is absent, report the exact bootstrap command from `references/connection-bootstrap.md`; do not invent a local database connector.
3. For an available connection, start with status and environment identification, then narrow read-only queries/metadata inspection. Use no DML, DDL, imports, commits, or mutating MCP tools.
4. For an existing-page error, run `apex-environment-alignment-complete` before proposing an edit.
5. Return reproducible evidence, cause hypothesis, scope, correction plan, TEST validation, production-install artifact requirements, and rollback condition.
