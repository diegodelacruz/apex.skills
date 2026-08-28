---
name: apex-engineering-safe
category: "Apex Engineering & Design"
order: 4
tags: ["inspection", "design", "export", "read-only"]
description: "Inspect and design APEX applications from exports with safe boundaries."
---

# Safe Oracle APEX Engineering

## Workflow

- Inspect an export first with `scripts/inspect_export.py <zip>`.
- Target APEX 24.1.3. Never assume components or internal APIs from another release are compatible.
- Keep production read-only: no DDL, DML, imports, deploys, user creation, or mutating MCP tool calls without explicit approval.
- Use readable YAML for discovery and SQL for exact implementation. Preserve existing behavior and derive numeric IDs from the target.
- The reference exports use `DATA`, Spanish (Ecuador), and Universal Theme 42; treat these as patterns, not mandatory project values.
- Read `references/mcp.md` before activating MCP. Configure secrets outside version control and verify with inspection tools before any dry-run.

## Output

- Report export revision, affected pages/components, compatibility risk, read-only evidence, and rollback plan.
