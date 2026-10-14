---
name: apex-delivery-lifecycle-safe
category: "Apex Delivery & Lifecycle"
order: 3
tags: ["lifecycle", "workflow", "qa", "governance"]
description: "Coordinate a safe APEX workflow from design through QA and documentation."
---

# Canonical APEX Delivery Lifecycle

Use the credential configured for the requested environment. If omitted, resolve
the environment from task context and then the configured `DB_ENV` selector.
Effective privileges granted by the DBA/APEX administrator determine available
Oracle and APEX operations; do not hardcode a permission matrix or user identity.
Preserve the single global confirmation for every live mutation, including the
explicit backup choice. Do not add further approvals or require this full
lifecycle for a focused request that a specialist can complete directly.

Follow this order and keep evidence paths and statuses current.

## Workflow

1. Apply `apex-project-workspace` and create project records only when the user requested workspace/bootstrap or the scope requires formal tracking; punctual changes do not require a plan or change folder.
2. Apply `apex-pattern-mining-safe` to existing export ZIP files and record adopted, adapted, and rejected patterns.
3. Apply `apex-solution-design` when useful; a direct request defines scope but does not replace the global mutation confirmation.
4. If DATA objects change, apply `oracle-data-change-governance-final` for relevant conventions and evidence; preserve the one global confirmation and do not create formal records for punctual DML.
5. Apply `apex-engineering-safe` as useful and use any configured MCP or database route.
6. Apply `apex-export-qa-safe`; run runtime/functional QA when requested or useful and report its results.
7. Apply `apex-user-manual` when requested; provide generated artifacts and describe visual validation performed.

Never mark a step completed without recording its evidence and candidate/version in the project plan.
