# Cross-Skill Integration Guide

**Last Updated:** 2026-09-17
**Purpose:** Explicit documentation of inter-skill references and integration points

---

## Quick Reference: Who Calls Whom

### Entry Point
- **`apex`** → Receives all user requests, routes to appropriate skills

### Coordinators
- **`apex-delivery-lifecycle-complete`** → Coordinates 7 skills for full cycle
- **`apex-delivery-lifecycle-safe`** → Coordinates 7 skills for safe cycle
- **`apex-delivery-lifecycle-zaimella`** → Integrates GPZ + APEX workflow
- **`apex-application-generator-complete`** → Orchestrates HITOs 1-5

### Sub-Coordinators
- **`apex-data-orchestrator-safe`** → Coordinates schema → migration → sync
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

**Orchestrator:** `apex-design-review-orchestrator` coordinates these 3 with approval gates

---

### Code Generation Pipeline
**Workflow:** Schema → Code Generation → Testing → Deployment

```
apex-schema-automation-safe
├─ Requires: oracle-data-change-governance-final gate
├─ Provides: Created database objects
├─ Integrates with: apex-page-automation-safe (pages using objects)
├─ Integrates with: apex-code-generation-safe (code using schema)
└─ Output: DDL statements, object definitions

apex-code-generation-safe
├─ Requires: apex-schema-automation-safe (schema exists)
├─ Requires: apex-blueprint-design-safe (approved design)
├─ Provides: Generated APEX code (forms, reports, validations)
├─ Generates: PL/SQL packages, APEX page code
├─ Passes to: apex-api-client-safe (deployment)
├─ Passes to: apex-automated-testing-safe (testing)
└─ Integrates with: apex-delivery-lifecycle-safe (pipeline)

apex-page-automation-safe
├─ Requires: apex-blueprint-design-safe (approved design)
├─ Requires: apex-export-qa-safe (QA validation)
├─ Provides: Created/modified APEX pages
├─ Operations: Create, modify, delete pages
├─ Calls: oracle-data-change-governance-final (if DML)
└─ Works with: apex-page-range-governance (page number allocation)

apex-automated-testing-safe
├─ Consumes: Generated code from apex-code-generation-safe
├─ Works with: apex-page-automation-safe (page structure)
├─ Requires: apex-api-client-safe (test setup/teardown)
├─ Provides: Test results (UI, performance, regression)
└─ Output: Test reports with pass/fail status
```

**Orchestrator:** `apex-application-generator-complete` coordinates code gen → data migration → deployment → testing

---

### Data Pipeline
**Workflow:** Schema → Validation → Migration → Sync

```
oracle-data-change-governance-final
├─ Gates: ALL DATA changes require approval
├─ Receives: Change requests from all skills
├─ Delegates: DDL to apex-schema-automation-safe
├─ Delegates: DATA migration to apex-data-migration-safe
├─ Uses: validate_sql_style.py (security gate)
└─ Output: Approved, audited changes

apex-data-migration-safe (HITO 4)
├─ Requires: oracle-data-change-governance-final gate
├─ Requires: apex-schema-automation-safe (target schema exists)
├─ Provides: ETL pipeline, validation, rollback
├─ Components: SchemaMappingGenerator, DataValidator, ETLPipeline, RollbackManager
├─ Passes to: apex-api-client-safe (sync to APEX)
└─ Output: Migrated data with audit trail

apex-api-client-safe (HITO 2)
├─ Requires: apex-code-generation-safe (code to deploy)
├─ Requires: apex-schema-automation-safe (schema setup)
├─ Provides: Deployment to APEX, environment sync
├─ Syncs: apex-data-migration-safe (data sync)
├─ Works with: apex-environment-alignment-complete (environment validation)
└─ Output: Deployed application, synchronized data
```

**Orchestrator:** `apex-data-orchestrator-safe` coordinates schema → validation → migration → sync

---

### QA Pipeline
**Workflow:** Export → Testing → Environment

```
apex-export-qa-safe
├─ Requires: None (analyzes existing exports)
├─ Provides: Static validation (structure, syntax)
├─ Validates: ZIP integrity, component validity
├─ Input: APEX export files
├─ Passes to: apex-automated-testing-safe (after approval)
├─ Consumed by: apex-user-manual (approved evidence)
└─ Output: QA report with issues/recommendations

apex-automated-testing-safe (HITO 3)
├─ Requires: apex-export-qa-safe (static validation passed)
├─ Requires: apex-code-generation-safe (generated code)
├─ Requires: apex-api-client-safe (test environment setup)
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
└─ Gate: Release approved
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
├─ Required by: ALL DATA changes (schema, migration, changes)
├─ Gates: DATA change approval (DDL/DML)
├─ Receives: Requests from apex-schema-automation-safe, apex-data-migration-safe
├─ Output: Approved, audited changes

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
- [ ] **Has approval gates** defined if coordinating others
- [ ] **Updates routing.md** if changing entry logic
- [ ] **Updates SKILL-DEPENDENCY-MATRIX.md** with new edges
- [ ] **Notifies** all affected upstream skills of new integration

---

## Reference Tables by Category

### By Category: Apex Code Generation

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-code-generation-safe | Generated forms, reports, validations | apex-schema-automation-safe, apex-blueprint-design-safe | apex-api-client-safe, apex-automated-testing-safe |
| apex-page-automation-safe | Page creation/modification | apex-blueprint-design-safe, apex-export-qa-safe | oracle-data-change-governance-final, apex-page-range-governance |
| apex-schema-automation-safe | Database objects | oracle-data-change-governance-final | apex-page-automation-safe, apex-code-generation-safe |

### By Category: Apex Data Integration

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-data-migration-safe | ETL pipeline, data migration | oracle-data-change-governance-final, apex-schema-automation-safe | apex-api-client-safe |
| apex-api-client-safe | Deployment, REST API client | apex-code-generation-safe, apex-schema-automation-safe | apex-automated-testing-safe, apex-data-migration-safe |
| oracle-data-change-governance-final | DATA change governance | None (gates all DATA changes) | apex-schema-automation-safe, apex-data-migration-safe |

### By Category: Apex Testing & QA

| Skill | Provides | Requires | Calls |
|-------|----------|----------|-------|
| apex-export-qa-safe | Static QA validation | None | apex-automated-testing-safe, apex-user-manual |
| apex-automated-testing-safe | UI/perf/regression tests | apex-export-qa-safe, apex-code-generation-safe, apex-api-client-safe | apex-environment-alignment-complete |
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
| apex-rest-source-catalogs-safe | REST integration guidance | apex-solution-design (context) | (advisory only) |
| apex-user-manual | Documentation generation | apex-export-qa-safe (approved QA) | scripts/audit_docx_images.py |
| apex-zaimella-gestion-proyectos | Methodology guidance | None (advisory) | apex-delivery-lifecycle-zaimella |

---

## Approval Gate Dependencies

**Must Pass Before Proceeding:**

| Gate | Required By | Approver(s) |
|------|------------|-------------|
| Static QA (`apex-export-qa-safe`) | `apex-automated-testing-safe`, `apex-user-manual` | QA team |
| Automated Tests (`apex-automated-testing-safe`) | `apex-environment-alignment-complete` | QA team |
| Environment Ready (`apex-environment-alignment-complete`) | Release to PROD | Ops team |
| Solution Design (`apex-solution-design`) | `apex-blueprint-design-safe` | Business owner, IT director |
| Blueprint Design (`apex-blueprint-design-safe`) | `apex-engineering-safe` | Technical lead, architect |
| Engineering Review (`apex-engineering-safe`) | Implementation starts | Principal engineer |
| DATA Governance (`oracle-data-change-governance-final`) | Any DATA change | Database admin, security |
| Page Range (`apex-page-range-governance`) | Page creation | Project lead |

---

## Circular Dependencies Check

✅ **CONFIRMED: No circular dependencies**

All flows are acyclic:
```
Entry Point: apex
  ↓
Coordinators (4 levels)
  ↓
Technical Skills (26 leaf nodes)
  ↓
No return paths to coordinators or entry point
```

---

## Version Compatibility Matrix

**Current Versions (2026-09-17):**

| Skill | Version | Compatibility |
|-------|---------|---|
| apex | 1.0 | Stable |
| apex-code-generation-safe | 1.0 (HITO 1) | Stable - used by `apex-application-generator-complete` |
| apex-api-client-safe | 1.0 (HITO 2) | Stable - used by `apex-application-generator-complete` |
| apex-automated-testing-safe | 1.0 (HITO 3) | Stable - used by `apex-application-generator-complete` |
| apex-data-migration-safe | 1.0 (HITO 4) | Stable - used by `apex-application-generator-complete` |
| apex-application-generator-complete | 0.2.0-dev | Development - orchestrates HITOs 1-5 |
| apex-delivery-lifecycle-complete | 1.0 | Stable |
| apex-delivery-lifecycle-safe | 1.0 | Stable |
| All others | 1.0 | Stable |

**New Orchestrators (0.1.0-dev):**
- apex-delivery-lifecycle-zaimella
- apex-data-orchestrator-safe
- apex-qa-orchestrator-safe
- apex-design-review-orchestrator

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
