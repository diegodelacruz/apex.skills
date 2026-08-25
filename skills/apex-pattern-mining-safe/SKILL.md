---
name: apex-pattern-mining-safe
category: "Apex Pattern Mining"
order: 8
tags: ['patterns', 'analysis', 'export', 'read-only']
description: "Extract reusable design patterns and best practices from APEX exports. Analyze existing applications for patterns and optimization opportunities."
---

# Safe APEX Pattern Mining

1. Run `scripts/mine_export_patterns.py <zip> [...] --json` to obtain evidence from exports.
2. Inspect representative YAML pages before recommending a pattern. Use SQL only for exact implementation detail.
3. Classify every candidate as **adopt**, **adapt**, or **do not reuse**. Include evidence, intent, reuse conditions, risks, and required validation.
4. Reuse patterns, not internal data: never copy IDs, business SQL, users, secrets, or custom JavaScript/CSS without a target-specific review.
5. Use upstream references for standards and QA; use apex-mcp only as an MCP integration reference. Do not execute upstream deployment tools while mining.

The local baseline demonstrates authenticated Universal Theme 42 applications using `DATA`, Spanish (Ecuador), session-state protection, extended HTML escaping, disabled deep links, denied framing, disabled browser cache, Hero pages, action bars, and region-refresh workspaces.

6. Hand off blueprint, REST catalog, or UX patterns to apex-blueprint-design-safe, apex-rest-source-catalogs-safe, or apex-ui-craft-safe.
7. Preserve Universal Theme, accessibility, responsive behavior, security boundaries, and explicit approval gates; evidence never authorizes implementation.
