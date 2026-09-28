---
name: apex-engineering-safe
category: "Apex Engineering & Design"
order: 4
tags: ["inspection", "design", "export", "implementation"]
description: "Inspect, design, and implement APEX applications from exports within the user's environment matrix."
---

# Safe Oracle APEX Engineering

## Workflow

- Inspect an export first with `scripts/inspect_export.py <zip>`.
- Use the APEX version observed in the requested environment. Report compatibility errors returned by APEX without imposing a skill-level version or production restriction.
- At the start, verify the selected credential and actual target environment through available read-only session/context tools. Oracle and APEX capabilities follow that credential's effective grants; do not hardcode user identities or a permission matrix. Use the configured route for the requested operation and report actual errors.
- Use readable YAML for discovery and SQL for exact implementation. Preserve existing behavior and derive numeric IDs from the target.
- The reference exports use `DATA`, Spanish (Ecuador), and Universal Theme 42; treat these as patterns, not mandatory project values.
- Read `references/mcp.md` before activating MCP. Configure secrets outside version control and verify with inspection tools before any dry-run.

## Modification Handoff

When the request includes changes, use `apex-page-automation-safe` or
`apex-schema-automation-safe` as implementation references when useful. Do not
add an approval gate or stop at a handoff.

## Output

- Report export revision, affected pages/components, compatibility risk, observed evidence, and rollback plan where relevant.
