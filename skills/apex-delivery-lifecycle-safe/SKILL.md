---
name: apex-delivery-lifecycle-safe
category: "Apex Delivery & Lifecycle"
order: 3
tags: ["lifecycle", "workflow", "qa", "governance"]
description: "Coordinate a safe APEX workflow from design through QA and documentation."
---

# Canonical APEX Delivery Lifecycle

Follow this order and keep evidence paths and statuses current.

## Workflow

1. Apply `apex-project-workspace`; create the global decisions record and master plan in `control-proyecto/`.
2. Apply `apex-pattern-mining-safe` to existing export ZIP files and record adopted, adapted, and rejected patterns.
3. Apply `apex-solution-design`; obtain user approval before implementation.
4. If DATA objects change, apply `oracle-data-change-governance-final`; create a decision record and implementation plan before executable SQL.
5. Apply `apex-engineering-safe` only within the approved scope and use MCP only when configured and authorized.
6. Apply `apex-export-qa-safe`; complete runtime/functional QA when acceptance criteria require it.
7. After approved QA evidence exists, apply `apex-user-manual`; capture real flows, generate DOCX, audit images, render to PNG, inspect every page, and deliver only after the render gate passes.

Never mark a step completed without recording its evidence and candidate/version in the project plan.
