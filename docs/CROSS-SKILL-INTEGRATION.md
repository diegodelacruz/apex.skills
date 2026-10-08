# Cross-Skill Integration Guide

**Purpose:** Explicit documentation of inter-skill references and integration points
**Audit state:** Legacy integration map; API-client edges below are unresolved and are not operational routes.

`apex-api-client-safe` is retired. Replace APEX component deployment references
with native APEX export/import or the configured App Builder/MCP route described
in `docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`. This guide's dependent-flow
remaining tables are a legacy map and do not prove full graph or cycle
compatibility. Direct edges assigning work to the retired adapter have been
removed from active dependent workflows; its row below is historical only.

> **Policy update (2026-09-28):** Direct requests define action, environment, and scope. Use the
> credential configured for that environment; effective Oracle/APEX grants determine available
> operations. Skills do not hardcode users or per-environment permission matrices, add approval
> steps, or ask the user to run work available to the agent. A connector's surface does not grant
> privileges, and its label does not prove the connected target.

---

## Quick Reference: Who Calls Whom

### Entry Point
- **`apex`** → Receives all user requests, routes to appropriate skills
- **Live change** → retains a completed diagnostic context and routes one
  confirmed object/component mutation to the relevant specialist

### Coordinators
- **`apex-delivery-lifecycle-complete`** → Coordinates 7 skills for full cycle
- **`apex-delivery-lifecycle-safe`** → Coordinates 7 skills for safe cycle
- **`apex-delivery-lifecycle-zaimella`** → Integrates GPZ + APEX workflow
- **`apex-application-generator-complete`** → Development prototype; not an executable deployment pipeline

### Sub-Coordinators
- **`apex-data-orchestrator-safe`** → Development outline for schema → migration; no APEX sync implementation
- **`apex-qa-orchestrator-safe`** → Coordinates static QA → automated testing → environment
- **`apex-design-review-orchestrator`** → Coordinates solution → blueprint → engineering

---

## Skill Integration Pairs

### Design Skills
**Workflow:** `apex-solution-design` → `apex-blueprint-design-safe` → `apex-engineering-safe`

```
apex-solution-design
├─ Provides: Business requirements, high-level architecture
├─ Consumes: Patterns from apex-pattern-mining-safe
├─ Reviews: REST integrations via apex-rest-source-catalogs-safe
├─ Considers: UX/accessibility via apex-ui-craft-safe
└─ Next: apex-blueprint-design-safe (blueprint creation)

apex-blueprint-design-safe
├─ Requires: Solution design (prerequisite)
├─ Provides: Detailed blueprints, scaffolding
├─ Consumes: Solution design decisions
├─ Uses: apex-engineering-safe feedback
└─ Next: apex-engineering-safe (implementation review)

apex-engineering-safe
├─ Requires: Blueprint design (prerequisite)
├─ Provides: Implementation feasibility, technical sign-off
├─ Validates: APEX best practices
├─ Reviews: UX via apex-ui-craft-safe
├─ Modifies: Existing pages (with apex-environment-alignment-complete)
├─ Works with: apex-export-qa-safe (validation before changes)
└─ Calls: oracle-data-change-governance-final (if DATA changes)
```

**Orchestrator:** `apex-design-review-orchestrator` coordinates these 3 as an advisory review

---

### Code Generation Pipeline
**Workflow:** Schema → Code Generation → Testing; APEX import is a separate operation

```
apex-schema-automation-safe
├─ Related guidance: oracle-data-change-governance-final (when DATA governance is in scope)
├─ Provides: Created database objects
├─ Integrates with: apex-page-automation-safe (pages using objects)
├─ Integrates with: apex-code-generation-safe (code using schema)
└─ Output: DDL statements, object definitions

For a diagnosed correction, the coordinator, schema skill and page skill share
the same `change.json` protocol. It is not a new specialist edge and does not
replace the complete delivery workflows above.

apex-code-generation-safe
├─ Requires: apex-schema-automation-safe (schema exists)
├─ Uses: apex-blueprint-design-safe (design context, when available)
├─ Provides: Generated APEX code (forms, reports, validations)
├─ Generates: PL/SQL packages, APEX page code
├─ Artifact import: `apex-page-automation-safe` and configured native APEX route (separate operation)
├─ Passes to: apex-automated-testing-safe (testing)
└─ Integrates with: apex-delivery-lifecycle-safe (pipeline)

apex-page-automation-safe
├─ Uses: apex-blueprint-design-safe (design context, when available)
├─ Can use: apex-export-qa-safe (static validation, when requested)
├─ Provides: Created/modified APEX pages
├─ Operations: Create, modify, delete pages
├─ Calls: oracle-data-change-governance-final (if DML)
└─ Works with: apex-page-range-governance (page number allocation)

apex-automated-testing-safe
├─ Consumes: Generated code from apex-code-generation-safe
├─ Works with: apex-page-automation-safe (page structure)
├─ Uses: configured target application and credentials (no setup/teardown API dependency)
├─ Provides: Test results (UI, performance, regression)
└─ Output: Test reports with pass/fail status
```

**Prototype:** `apex-application-generator-complete` describes a development workflow; its retired API deployment phase is not operational.

---

### Data Pipeline
**Workflow:** Schema → Validation → Migration; APEX artifact import is a separate operation

```
oracle-data-change-governance-final
├─ Provides: DATA change governance guidance and validation resources
├─ Related skills: apex-schema-automation-safe, apex-data-migration-safe
├─ Uses: validate_sql_style.py for applicable SQL style checks
└─ Does not add a user approval gate or replace the requested Oracle route

apex-data-migration-safe
├─ Related: oracle-data-change-governance-final and apex-schema-automation-safe
├─ Uses the target schema when the requested migration requires one
├─ Provides: ETL pipeline, validation, rollback
├─ Components: SchemaMappingGenerator, DataValidator, ETLPipeline, RollbackManager
└─ Output: Migrated data with audit trail

Optional APEX artifact import
├─ Uses: apex-page-automation-safe and the configured native APEX route
├─ Scope: APEX components only; it does not synchronize migrated Oracle data
└─ Evidence: verify the requested target and imported components
```

**Prototype:** `apex-data-orchestrator-safe` outlines schema → validation → migration; it does not implement APEX synchronization.

---

### QA Pipeline
**Workflow:** Export → Testing → Environment

```
apex-export-qa-safe
├─ Requires: None (analyzes existing exports)
├─ Provides: Static validation (structure, syntax)
├─ Validates: ZIP integrity, component validity
├─ Input: APEX export files
├─ Can inform: apex-automated-testing-safe when testing is requested
├─ Can provide evidence to: apex-user-manual
└─ Output: QA report with issues/recommendations

apex-automated-testing-safe
├─ Can use: apex-export-qa-safe (static findings)
├─ Can use: apex-code-generation-safe (generated artifacts)
├─ Uses: an existing configured test application; no API setup/teardown dependency
├─ Provides: UI tests (Selenium), performance tests, regression tests
├─ Components: SeleniumTestGenerator, PerformanceTestGenerator, RegressionTestValidator
├─ Uses: apex-page-automation-safe (page structure for testing)
├─ Output: Test results (pass/fail), coverage report
└─ Passes to: apex-environment-alignment-complete (environment validation)

apex-environment-alignment-complete
├─ Requires: apex-automated-testing-safe (tests pass)
├─ Uses: apex-database-diagnostics (diagnostics)
├─ Works with: apex-delivery-lifecycle-complete (release readiness)
├─ Validates: TEST ↔ PROD alignment, connectivity, credentials
├─ Output: Environment readiness report
└─ Output: environment alignment evidence for the requested scope
```

**Orchestrator:** `apex-qa-orchestrator-safe` coordinates export QA → automated testing → environment validation

---

### Project Management & Governance

```
apex-project-bootstrap-final
├─ Initializes: Workspace and governance
├─ Leads to: apex-delivery-lifecycle-complete (next step)
├─ Requires: oracle-data-change-governance-final (DATA setup)
├─ Uses: apex-project-workspace (workspace creation)
├─ Output: Project ready for delivery cycle

apex-project-workspace
├─ Creates: control-proyecto/ directory
├─ Integrates with: oracle-data-change-governance-final (governance)
├─ Used by: apex-delivery-lifecycle-safe (workspace prerequisite)
├─ Output: Workspace structure ready

apex-page-range-governance
├─ Used by: apex-engineering-safe (reserve page numbers)
├─ Used by: apex-page-automation-safe (create new pages)
├─ Validates: No page number conflicts
├─ Output: Reserved page ranges

oracle-data-change-governance-final
├─ Related to: apex-schema-automation-safe, apex-data-migration-safe
├─ Provides: DATA change governance guidance when requested
├─ Does not gate direct user-requested Oracle execution

apex-audit-decisions-log
├─ Reads: .bitacora.json (git-backed audit trail)
├─ Shows: Decision history for all skills
├─ Output: Audit trail visualization, reports

apex-zaimella-gestion-proyectos
├─ Provides: GPZ methodology guidance
├─ Integrated by: apex-delivery-lifecycle-zaimella
├─ Overlays: Governance on apex-delivery-lifecycle-complete
└─ Output: GPZ project governance
```

---

## Integration Checklist for New Skills

When creating a new skill, verify it:

- [ ] **Documents upstream dependencies** in SKILL.md
- [ ] **Documents downstream consumers** ("Used by..." section)
- [ ] **Has explicit entry point** (router → coordinator → skill)
- [ ] **References related skills** in "Integration" section
- [ ] **Lists prerequisite skills** if any
- [ ] **Lists blocking skills** (cannot run concurrently)
- [ ] **Names direct skill edges** and their current operational evidence
- [ ] **Updates routing.md** if changing entry logic
- [ ] **Updates SKILL-DEPENDENCY-MATRIX.md** with new edges
- [ ] **Notifies** all affected upstream skills of new integration

---

## Reference Tables by Category

### By Category: Apex Code Generation

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-code-generation-safe | Generated forms, reports, validations | apex-schema-automation-safe, apex-blueprint-design-safe | apex-automated-testing-safe; native import is separate |
| apex-page-automation-safe | Page creation/modification | apex-blueprint-design-safe, apex-export-qa-safe | oracle-data-change-governance-final, apex-page-range-governance |
| apex-schema-automation-safe | Database objects | oracle-data-change-governance-final | apex-page-automation-safe, apex-code-generation-safe |

### By Category: Apex Data Integration

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-data-migration-safe | ETL pipeline, data migration | oracle-data-change-governance-final, apex-schema-automation-safe | None; APEX import is separate |
| apex-api-client-safe | Retired simulated REST adapter; non-operational | None | Historical compatibility references only |
| oracle-data-change-governance-final | DATA change governance guidance | None | apex-schema-automation-safe, apex-data-migration-safe |

### By Category: Apex Testing & QA

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-export-qa-safe | Static QA validation | None | apex-automated-testing-safe, apex-user-manual |
| apex-automated-testing-safe | UI/perf/regression test generation | apex-export-qa-safe, apex-code-generation-safe | apex-environment-alignment-complete |
| apex-environment-alignment-complete | Environment readiness | apex-automated-testing-safe, apex-database-diagnostics | apex-delivery-lifecycle-complete |

### By Category: Apex Design & Engineering

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-solution-design | High-level architecture | apex-pattern-mining-safe (optional) | apex-blueprint-design-safe |
| apex-blueprint-design-safe | Detailed specifications | apex-solution-design | apex-engineering-safe, apex-code-generation-safe, apex-page-automation-safe |
| apex-engineering-safe | Feasibility, sign-off | apex-export-qa-safe, apex-environment-alignment-complete (existing pages) | apex-ui-craft-safe, oracle-data-change-governance-final (DATA) |
| apex-ui-craft-safe | UX review | apex-engineering-safe (optional) | (advisory only) |

### By Category: Apex Project Management

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-project-bootstrap-final | Project initialization | apex-delivery-lifecycle-complete | apex-project-workspace, oracle-data-change-governance-final |
| apex-project-workspace | Workspace setup | None | oracle-data-change-governance-final, apex-audit-decisions-log |
| apex-page-range-governance | Page range allocation | None | (consulted by other skills) |
| apex-pattern-mining-safe | Pattern extraction | None | apex-solution-design, apex-blueprint-design-safe |

### By Category: Apex Infrastructure & Utilities

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-database-diagnostics | Diagnostics, analysis | None (read-only) | oracle-data-change-governance-final (if corrections) |
| apex-audit-decisions-log | Audit visualization | None (read-only) | (displays .bitacora.json) |
| apex-external-context-learn | Saved external-repository context | None declared | scripts/external_repo_scanner.py, scripts/external_repo_indexer.py |
| apex-rest-source-catalogs-safe | REST integration guidance | apex-solution-design (context) | (advisory only) |
| apex-user-manual | Documentation generation | available QA evidence | (upstream: zaimella-skill audit_docx_images.py) |
| apex-zaimella-gestion-proyectos | Methodology guidance | None (advisory) | apex-delivery-lifecycle-zaimella |

---

## Historical approval assignments

The former approver table is removed because it was unsupported and conflicted
with current direct-scope routing. This guide does not assign approvers or add
execution gates; follow the user's request and the configured system's actual
permissions.

---

## Circular Dependencies Check

**Not verified:** this legacy guide does not establish an acyclic graph. See the
current edge and cycle limitations in `ORCHESTRATOR-AUDIT.md`.

```
Cycle status: pending complete edge extraction and review.
```

---

## Runtime compatibility

This static integration map does not certify runtime compatibility. Check each
skill's current metadata status and the configured target before claiming that
an operation ran.

---

## Contact & Questions

For integration questions:
1. Check this file first (Cross-Skill Integration)
2. Consult `docs/SKILL-DEPENDENCY-MATRIX.md` (detailed matrix)
3. Check `skills/apex/references/routing.md` (entry points)
4. Review individual SKILL.md files (specific skill details)

---

**Document Version:** 1.0
**Last Reviewed:** 2026-09-17
**Maintained By:** Repository Stewards
