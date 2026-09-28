---
name: apex-design-review-orchestrator
category: "Apex Engineering & Design"
order: 11.5
tags: ["design", "review", "orchestration"]
description: "Coordinate APEX solution, blueprint, and engineering review without adding execution gates."
---

# APEX Design Review Orchestrator

Coordinate solution design, APEX blueprints, and engineering review. Preserve these useful review
steps while keeping decisions advisory: a finding, missing stakeholder sign-off, or incomplete
optional artifact does not create an approval gate for work the user directly requested.

## Workflow

### Phase 1: Solution design

Use `apex-solution-design` to clarify business requirements, application scope,
data structures, integrations, constraints, assumptions, and candidate
architecture. Preserve traceability from each requirement to the proposed
solution and identify open decisions without inventing answers.

### Phase 2: Blueprint design

Use `apex-blueprint-design-safe` to turn the selected solution into reviewable
page structure, wireframes, regions, items, processes, validations, data
bindings, navigation, dependencies, and implementation scaffolding. Include
acceptance criteria and useful validation steps for the requested work.

### Phase 3: Engineering review

Use `apex-engineering-safe` to assess APEX/database compatibility, object and
plugin dependencies, security, performance, accessibility, maintainability,
and implementation risks. Record concrete findings and recommendations, then
report readiness and any unresolved decisions. This review supports the direct
request; it does not add a separate approval gate or block requested work.

Keep the three phases distinct and coordinate existing specialist skills
instead of duplicating their design or review. Record decisions and evidence
when the task creates or changes project artifacts.

1. Identify the business objective, users, target environment, application/pages, constraints, and
   acceptance outcomes from the request and available evidence. Record assumptions separately;
   ask only for information needed to choose or build the requested solution.
2. Coordinate `apex-solution-design` to outline page/navigation structure, data entities, access
   model, integrations, and key decisions when solution design is in scope.
3. Coordinate `apex-blueprint-design-safe` to create page-level wireframes/specifications,
   components, bindings, validations, and an implementation scaffold when a blueprint is useful.
   The blueprint may define acceptance criteria and a test plan; it does not execute QA.
4. Coordinate `apex-engineering-safe` to inspect exports and assess APEX-version compatibility,
   technical feasibility, dependencies, security, performance, accessibility, and implementation
   risks. Keep observed evidence distinct from assumptions and recommendations.
5. Record material design choices with `apex-audit-decisions-log` when a project decision trail is
   requested or already in use. Avoid duplicating project setup, export QA, automated testing, or
   database-change governance; use those specialist skills only for their own scope.
6. If the user requested implementation, continue through `apex-page-automation-safe`,
   `apex-schema-automation-safe`, or the relevant specialist, using the credential configured for
   the named environment. Do not stop at a handoff or wait for stakeholder approval.
7. If the request was design/review only, return the findings and the next implementation steps.

## Reporting

Include the requested scope, evidence reviewed, assumptions, solution and page structure,
compatibility/dependency findings, material risks, decisions, and useful validation steps. Mark
which checks were run and which are recommendations. A missing profile, unavailable comparison,
unresolved review finding, or absent stakeholder approval does not block a direct user request.
Protect credentials and report actual connectivity, tool, or Oracle/APEX errors accurately.
