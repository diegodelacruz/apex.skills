---
name: apex-environment-alignment-complete
category: "Apex Environment & Alignment"
order: 5
tags: ['environment', 'sync', 'validation', 'governance']
description: "Validate and synchronize TEST and production APEX environments. Ensure alignment and consistency across deployment targets."
---

# Complete APEX Environment Alignment

- Use `scripts/manage_apex_credentials.py` to set, check, or validate per-user secure profiles. Never request users to paste credentials into chat, source files, Markdown, or Git.
- On project start, check TEST/production profile status. Validate only with a read-only connection when authorized. Record profile name/state only.
- Before an existing-page edit, compare TEST and production and write `control-proyecto/cambios/<id>/evidencia/environment-diff.md`.
- When differences exist, recommend production-to-TEST synchronization and wait for explicit authorization. Record an accepted unsynchronized baseline if declined.
- After QA, export TEST SQL and a production installation manifest to `control-proyecto/cambios/<id>/release/`. Production installation requires separate explicit authorization and an authorized profile/operator.
- APEX 24.2 MCP tools remain inspection/dry-run only for APEX 24.1.3 until an approved TEST compatibility result exists.
