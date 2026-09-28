---
name: apex-delivery-lifecycle-complete
category: "Apex Delivery & Lifecycle"
order: 2
tags: ["lifecycle", "workflow", "release", "governance"]
description: "Run the complete APEX lifecycle with environment and DATA governance."
---

# Complete APEX Delivery Lifecycle

## Environment and execution policy

Use the credential configured for the named environment. Effective Oracle/APEX
privileges granted to that account by the DBA/APEX administrator determine
available operations; do not hardcode a permission matrix or user identity.
Verify the connected account and actual destination with read-only checks when
available. Do not add approval steps or ask the user to execute work available
to the agent. Use the relevant specialist directly for a focused request; run
the full lifecycle only when the requested scope needs it.

## Workflow

1. Start with `apex-project-bootstrap-final` and create `control-proyecto/`.
2. Use `apex-environment-alignment-complete` for environment evidence when useful; it is not a prerequisite to an edit.
3. Mine patterns, design, govern DATA changes, and engineer APEX under the user's stated requirements and observed project baseline.
4. Validate in the requested environment and package release SQL and manifest when useful. A direct user request authorizes the named environment.
5. Create the Word manual when requested; report QA and rendering evidence accurately.

## Boundaries

Use `apex-delivery-lifecycle-safe` for the detailed phases and `oracle-data-change-governance-final` for every DATA object change. Record all profile access states and environment decisions without secrets.
