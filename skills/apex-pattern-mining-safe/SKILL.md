---
name: apex-pattern-mining-safe
description: Mine reusable Oracle APEX design, security, navigation, component, template, plugin, LOV, JavaScript, CSS, and page-flow patterns from split-export ZIP files. Use when learning from existing APEX applications such as Finanzas (109) and Compras (130), comparing exports, or preparing a knowledge base for future development without modifying an application.
---

# Safe APEX Pattern Mining

1. Run `scripts/mine_export_patterns.py <zip> [...] --json` to obtain evidence from exports.
2. Inspect representative YAML pages before recommending a pattern. Use SQL only for exact implementation detail.
3. Classify every candidate as **adopt**, **adapt**, or **do not reuse**. Include evidence, intent, reuse conditions, risks, and required validation.
4. Reuse patterns, not internal data: never copy IDs, business SQL, users, secrets, or custom JavaScript/CSS without a target-specific review.
5. Use Zaimella upstream references for standards and QA; use apex-mcp only as an MCP integration reference. Do not execute upstream deployment tools while mining.

The local baseline contains authenticated, Universal Theme 42 applications using `DATA`, Spanish (Ecuador), session-state protection, extended HTML escaping, disabled deep links, denied framing, and disabled browser cache. Finanzas uses a Hero home pattern; Compras includes a Zaimella action-bar and region-refresh workspace pattern.
