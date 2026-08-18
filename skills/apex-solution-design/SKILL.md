---
name: apex-solution-design
description: Design new Oracle APEX 24.1.3 applications or pages from a business request, schema inspection, and an APEX pattern catalogue. Use before creating an application or changing pages when a safe architecture, page map, navigation, authorization model, component choices, validation plan, and rollout plan are required. Complements APEX pattern mining, engineering, QA, and MCP tooling without executing database or APEX changes.
---

# APEX Solution Design

## Inputs

Require the business objective, environment, target schema, users/roles, data objects, integrations, expected pages, acceptance criteria, and whether an existing application is affected. If a pattern catalogue exists, use it as input rather than inventing conventions.

## Workflow

1. Inspect the target schema and existing export in read-only mode.
2. Classify patterns from `apex-pattern-mining` as **adopt**, **adapt**, or **do not reuse**. Do not copy IDs, business SQL, secrets, or custom code blindly.
3. Produce a page map with page ID ranges, purpose, navigation entry, mode, regions, items, actions, validations, processes, authorization, and evidence needed.
4. Design data access with explicit columns, bind variables, least privilege, validation boundaries, and transaction/rollback behaviour.
5. Define a test plan: static export validation, role tests, happy path, invalid input, navigation, integration failure, and performance-sensitive queries.
6. Stop before implementation. Request approval of the design and scope.

## Output

Deliver a concise design package: assumptions, architecture, page map, pattern decisions, data/API contract, security model, implementation increments, acceptance criteria, test matrix, and rollback approach.
