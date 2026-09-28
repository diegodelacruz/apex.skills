---
name: apex-blueprint-design-safe
category: "Apex Engineering & Design"
order: 15
tags: ["blueprint", "design", "scaffolding", "read-only"]
description: "Create reviewable APEX blueprints from user requirements and available metadata."
---

# Safe Oracle APEX Blueprint Design

Use this workflow to turn the user's functional requirements and read-only schema metadata into a
reviewable APEX Application Blueprint. It designs a scaffold; it does not directly modify an APEX
application, import a blueprint, or change database objects.

## Context inference

Infer the target APEX version, business objective, users and roles, environment, and
schema metadata from the conversation and the database. Only ask when genuinely ambiguous.
When using Oracle's official APEX upstream, record the branch and commit SHA in the design package.

## Workflow

1. Validate that functional requirements and schema metadata describe the same business scope.
2. Identify pages, navigation, reports, forms, charts, filters, actions, validations, and role
   boundaries. Mark each decision as user-stated, observed, or an assumption.
3. Select existing patterns only after classifying their source as **adopt**, **adapt**, or
   **reference only**. Never reuse application IDs, workspace IDs, secrets, sample data, business
   SQL, authorization schemes, or plugin dependencies without review.
4. Produce an importable Blueprint Markdown artifact and a companion design review. Use only the
   icon allowlist from the version-pinned upstream when icons are specified.
5. Identify security, data ownership, performance, and accessibility concerns; include actionable
   recommendations without requiring stakeholder sign-off as a condition to continue.
6. This skill produces design artifacts. When the user also requested implementation, hand the
   artifact to the appropriate APEX/database specialist and continue; do not ask for a second
   approval. Do not perform unrelated implementation as part of a blueprint-only request.

## Output

Deliver: source evidence; APEX version; assumptions; page and navigation map; role/authorization
model; data contract; pattern decisions; Blueprint artifact; acceptance criteria; static and
runtime test plan; import prerequisites; and rollback approach.
