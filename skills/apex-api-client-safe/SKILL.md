---
name: apex-api-client-safe
description: Retired compatibility entry; it does not provide an operational APEX API client.
category: Apex Integration
order: 22
tags:
  - retired
  - compatibility
created: 2026-09-17
status: retired
---

# apex-api-client-safe

> **Retired.** This compatibility entry is retained so existing references
> resolve, but it has no operational export, import, deployment, or sync
> capability. Do not use it to perform APEX changes.

For supported APEX page export/import work, follow
[`apex-page-automation-safe`](../apex-page-automation-safe/SKILL.md). For
Oracle schema or data work, use the matching supported specialist. Repository
managed Oracle credentials are read from the root `.env` by the selected
launcher; do not pass credentials through this retired adapter.
