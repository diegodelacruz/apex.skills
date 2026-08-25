---
name: apex-solution-design
category: "Apex Engineering & Design"
order: 11
tags: ['design', 'architecture', 'planning']
description: "Design new APEX applications or pages from business requirements. Create architecture and design specifications for new features."
---

# APEX Solution Design

Use apex-blueprint-design-safe before implementation scaffolding, apex-rest-source-catalogs-safe for Fusion REST contracts, and apex-ui-craft-safe for Universal Theme, accessibility, responsive, or motion decisions. This workflow stops for explicit approval before implementation.

## Inputs

Require the business objective, environment, target schema, users/roles, data objects, integrations, expected pages, acceptance criteria, and whether an existing application is affected. If a pattern catalogue exists, use it as input rather than inventing conventions.

## Workflow

1. Inspect the target schema and existing export in read-only mode.
2. Classify patterns from `apex-pattern-mining` as **adopt**, **adapt**, or **do not reuse**. Do not copy IDs, business SQL, secrets, or custom code blindly.
3. Produce a page map with page ID ranges, purpose, navigation entry, mode, regions, items, actions, validations, processes, authorization, and evidence needed.
4. Design data access with explicit columns, bind variables, least privilege, validation boundaries, and transaction/rollback behaviour.
5. Define a test plan: static export validation, role tests, happy path, invalid input, navigation, integration failure, and performance-sensitive queries.
6. Apply Universal Theme and accessibility constraints: keyboard and focus flow, contrast, narrow/typical/wide viewports, touch, reduced motion, and screen-reader semantics.
7. Stop before implementation. Request approval of the design and scope.

## Output

Deliver a concise design package: assumptions, architecture, page map, pattern decisions, data/API contract, security model, implementation increments, acceptance criteria, test matrix, and rollback approach.
