---
name: apex-engineering-safe
description: Safely inspect, design, or document Oracle APEX 24.1.3 applications using ZIP, SQL, or YAML exports. Use for APEX pages, regions, items, processes, LOVs, navigation, authorization, PL/SQL integration, and portable MCP activation. Uses Finanzas (109) and Compras (130) as source patterns and limits production access to read-only operations.
---

# Safe Oracle APEX Engineering

- Inspect an export first with `scripts/inspect_export.py <zip>`.
- Target APEX 24.1.3. Never assume components or internal APIs from another release are compatible.
- Keep production read-only: no DDL, DML, imports, deploys, user creation, or mutating MCP tool calls without explicit approval.
- Use readable YAML for discovery and SQL for exact implementation. Preserve existing behavior and derive numeric IDs from the target.
- Finanzas is application 109 / `FINZ`; Compras is 130 / `COMP`. Both use `DATA`, Spanish (Ecuador), and Universal Theme 42.
- Read `references/mcp.md` before activating MCP. Configure secrets outside version control and verify with inspection tools before any dry-run.
- Report export revision, affected pages/components, compatibility risk, read-only evidence, and rollback plan.
