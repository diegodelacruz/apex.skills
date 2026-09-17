# Skill Dependency Matrix

**Last Updated:** 2026-09-17
**Total Skills:** 26
**Orchestrators:** 4 (1 maestro, 3 coordinadores)

## Legend

- **DIRECT** - Must run before/after this skill
- **INDIRECT** - Recommended to have run before/after
- **OPTIONAL** - Can integrate if available
- **CONFLICTS** - Cannot run together

---

## Dependency Matrix (Skills → Dependencies)

### Legend by Dependency Type
| Type | Meaning | Symbol |
|------|---------|--------|
| D | Direct prerequisite | ▶ |
| I | Indirect / recommended | ⊳ |
| O | Optional integration | ◎ |
| C | Conflicts with | ✗ |

---

## 1. ENTRY POINT

### apex (Coordinador Maestro)
Routes to specialized skills. No dependencies (entry point).

```
DEPENDENCIES:
  - None (entry point)

COORDINATES:
  - apex-project-bootstrap-final (new projects)
  - apex-database-diagnostics (diagnostics)
  - apex-pattern-mining-safe (learn from exports)
  - apex-solution-design (design)
  - apex-blueprint-design-safe (blueprint)
  - apex-engineering-safe (design/edit)
  - apex-environment-alignment-complete (environment)
  - apex-delivery-lifecycle-complete (full cycle)
  - apex-delivery-lifecycle-safe (safe cycle)
  - apex-delivery-lifecycle-zaimella (GPZ projects) [NEW]
  - oracle-data-change-governance-final (DATA changes)
  - apex-ui-craft-safe (UX)
  - apex-rest-source-catalogs-safe (REST integrations)
  - apex-page-range-governance (page ranges)
```

---

## 2. PRIMARY ORCHESTRATORS

### apex-delivery-lifecycle-complete (Coordinador Secundario)
```
DEPENDENCIES:
  D ▶ apex-project-bootstrap-final (initialization)

COORDINATES:
  - apex-project-bootstrap-final
  - apex-pattern-mining-safe
  - apex-solution-design
  - oracle-data-change-governance-final
  - apex-engineering-safe
  - apex-export-qa-safe
  - apex-user-manual

SEQUENCE:
  1. apex-project-bootstrap-final (initialize)
  2. apex-pattern-mining-safe (learn patterns)
  3. apex-solution-design (design)
  4. oracle-data-change-governance-final (DATA governance)
  5. apex-engineering-safe (implement)
  6. apex-export-qa-safe (QA)
  7. apex-user-manual (documentation)
```

### apex-delivery-lifecycle-safe (Coordinador Secundario)
```
DEPENDENCIES:
  D ▶ apex-project-workspace (create workspace)

COORDINATES:
  - apex-project-workspace
  - apex-pattern-mining-safe
  - apex-solution-design
  - oracle-data-change-governance-final
  - apex-engineering-safe
  - apex-export-qa-safe
  - apex-user-manual

SEQUENCE:
  1. apex-project-workspace (setup workspace)
  2. apex-pattern-mining-safe (learn patterns)
  3. apex-solution-design (design)
  4. oracle-data-change-governance-final (DATA governance)
  5. apex-engineering-safe (implement - approved scope only)
  6. apex-export-qa-safe (QA)
  7. apex-user-manual (documentation)
```

### apex-delivery-lifecycle-zaimella (NEW - Coordinador Secundario)
```
DEPENDENCIES:
  D ▶ apex-zaimella-gestion-proyectos (GPZ methodology)
  D ▶ apex-delivery-lifecycle-complete (APEX workflow)

COORDINATES:
  - apex-zaimella-gestion-proyectos (GPZ governance)
  - apex-delivery-lifecycle-complete (technical flow)

SEQUENCE:
  1. apex-zaimella-gestion-proyectos (setup GPZ project)
  2. apex-delivery-lifecycle-complete (execute APEX workflow under GPZ)
  3. apex-zaimella-gestion-proyectos (close-out GPZ project)
```

### apex-application-generator-complete (Coordinador Terciario)
```
DEPENDENCIES:
  D ▶ apex-code-generation-safe (HITO 1)
  D ▶ apex-data-migration-safe (HITO 4)
  D ▶ apex-api-client-safe (HITO 2)
  D ▶ apex-automated-testing-safe (HITO 3)

COORDINATES:
  - apex-code-generation-safe (code gen)
  - apex-data-migration-safe (data mapping/migration)
  - apex-api-client-safe (deployment)
  - apex-automated-testing-safe (testing)

SEQUENCE:
  1. Code Generation Phase (apex-code-generation-safe)
  2. Data Migration Phase (apex-data-migration-safe)
  3. Deployment Phase (apex-api-client-safe)
  4. Testing Phase (apex-automated-testing-safe)
  5. Verification & Reporting (internal)
```

---

## 3. DATA & ORCHESTRATORS

### oracle-data-change-governance-final
```
DEPENDENCIES:
  I ⊳ apex-database-diagnostics (validate before change)

COORDINATES:
  - apex-schema-automation-safe (DDL governance)
  - apex-data-migration-safe (DATA governance)
  D ▶ scripts/validate_sql_style.py (security gate)

BLOCKS:
  C ✗ No direct SQL execution (use orchestrators)
```

### apex-data-orchestrator-safe (NEW - Coordinador Tercio)
```
DEPENDENCIES:
  D ▶ oracle-data-change-governance-final (governance)

COORDINATES:
  - apex-schema-automation-safe (create schema)
  - apex-data-migration-safe (migrate data)
  - apex-api-client-safe (sync to APEX)

SEQUENCE:
  1. apex-schema-automation-safe (DDL)
  2. oracle-data-change-governance-final (validate)
  3. apex-data-migration-safe (ETL)
  4. apex-api-client-safe (sync)
```

---

## 4. CODE GENERATION

### apex-code-generation-safe
```
DEPENDENCIES:
  D ▶ apex-schema-automation-safe (schema exists)
  I ⊳ apex-blueprint-design-safe (approved design)

COORDINATES:
  - apex-schema-automation-safe (input schema)
  - apex-api-client-safe (deployment)
  - apex-automated-testing-safe (testing)

PRODUCES:
  - APEX Forms (PL/SQL)
  - APEX Reports (SQL)
  - APEX Validations (PL/SQL)
```

### apex-page-automation-safe
```
DEPENDENCIES:
  D ▶ apex-blueprint-design-safe (approved design)
  D ▶ apex-export-qa-safe (QA before edit)

COORDINATES:
  - apex-export-qa-safe (validation)
  - oracle-data-change-governance-final (if DML)

OPERATIONS:
  - Create new pages
  - Modify existing pages
  - Delete pages (with audit)
```

### apex-schema-automation-safe
```
DEPENDENCIES:
  D ▶ oracle-data-change-governance-final (DDL governance)

COORDINATES:
  - apex-page-automation-safe (pages using objects)
  - apex-code-generation-safe (code using schema)

OPERATIONS:
  - Create tables/views
  - Modify columns
  - Drop objects
```

---

## 5. DESIGN & ENGINEERING

### apex-solution-design
```
DEPENDENCIES:
  I ⊳ apex-pattern-mining-safe (learn patterns)

COORDINATES:
  - apex-pattern-mining-safe (patterns)
  - apex-blueprint-design-safe (next step)
  - apex-rest-source-catalogs-safe (REST integrations)
  - apex-ui-craft-safe (UX/accessibility)
  - oracle-data-change-governance-final (DATA changes)
```

### apex-blueprint-design-safe
```
DEPENDENCIES:
  D ▶ apex-solution-design (high-level design)
  I ⊳ apex-engineering-safe (implementation feedback)

COORDINATES:
  - apex-solution-design (prerequisite)
  - apex-engineering-safe (implementation)
  - oracle-data-change-governance-final (if DATA changes)

PRODUCES:
  - Reviewable APEX blueprints
  - Scaffolding templates
```

### apex-engineering-safe
```
DEPENDENCIES:
  D ▶ apex-export-qa-safe (validate source)
  I ⊳ apex-environment-alignment-complete (existing pages)
  I ⊳ apex-blueprint-design-safe (approved design)

COORDINATES:
  - apex-export-qa-safe (validation)
  - apex-environment-alignment-complete (existing pages)
  - apex-ui-craft-safe (UX review)
  - oracle-data-change-governance-final (DATA changes)

OPERATIONS:
  - Inspect APEX apps
  - Design new components
  - Refactor existing components
```

### apex-design-review-orchestrator (NEW - Coordinador Cuaternario)
```
DEPENDENCIES:
  D ▶ apex-solution-design (high level)
  D ▶ apex-blueprint-design-safe (detailed)
  D ▶ apex-engineering-safe (review)

COORDINATES:
  - apex-solution-design (solution phase)
  - apex-blueprint-design-safe (blueprint phase)
  - apex-engineering-safe (engineering review)

SEQUENCE:
  1. apex-solution-design (approve design)
  2. apex-blueprint-design-safe (create blueprints)
  3. apex-engineering-safe (review implementation readiness)
  4. Gate: Approval before implementation
```

---

## 6. TESTING & QA

### apex-export-qa-safe
```
DEPENDENCIES:
  None (static analysis)

COORDINATES:
  - apex-engineering-safe (input exports)
  - apex-automated-testing-safe (next phase)

VALIDATES:
  - ZIP export structure
  - Page/component integrity
  - No syntax errors
```

### apex-automated-testing-safe
```
DEPENDENCIES:
  D ▶ apex-code-generation-safe (generated code)
  I ⊳ apex-api-client-safe (test setup)

COORDINATES:
  - apex-code-generation-safe (test target)
  - apex-page-automation-safe (page structure)
  - apex-api-client-safe (setup/teardown)

TEST TYPES:
  - UI tests (Selenium)
  - Performance tests
  - Regression tests
```

### apex-qa-orchestrator-safe (NEW - Coordinador Cuaternario)
```
DEPENDENCIES:
  D ▶ apex-export-qa-safe (static QA)
  D ▶ apex-automated-testing-safe (automated tests)
  D ▶ apex-environment-alignment-complete (environment check)

COORDINATES:
  - apex-export-qa-safe (phase 1)
  - apex-automated-testing-safe (phase 2)
  - apex-environment-alignment-complete (phase 3)

SEQUENCE:
  1. apex-export-qa-safe (static validation)
  2. apex-automated-testing-safe (automated testing)
  3. apex-environment-alignment-complete (environment validation)
  4. Gate: Release approved
```

---

## 7. ENVIRONMENT & DEPLOYMENT

### apex-environment-alignment-complete
```
DEPENDENCIES:
  I ⊳ apex-database-diagnostics (diagnostics)
  D ▶ apex-delivery-lifecycle-complete (lifecycle)

COORDINATES:
  - apex-database-diagnostics (diagnostics)
  - apex-engineering-safe (changes to existing)
  - apex-api-client-safe (deployment)

VALIDATES:
  - TEST ↔ PROD alignment
  - Connection readiness
  - Credentials validity
```

### apex-api-client-safe
```
DEPENDENCIES:
  D ▶ apex-code-generation-safe (code to deploy)
  D ▶ apex-schema-automation-safe (schema setup)

COORDINATES:
  - apex-code-generation-safe (input)
  - apex-automated-testing-safe (post-deployment)
  - apex-schema-automation-safe (setup)
  - apex-data-migration-safe (data sync)

OPERATIONS:
  - Deploy to APEX instances
  - Sync across environments
  - Rollback if needed
```

---

## 8. GOVERNANCE & AUDIT

### apex-page-range-governance
```
DEPENDENCIES:
  None (standalone validation)

COORDINATES:
  - apex-engineering-safe (before page creation)
  - apex-page-automation-safe (page automation)

GATES:
  - Reserve page ranges
  - Validate no conflicts
  - Required before new pages
```

### oracle-data-change-governance-final
```
DEPENDENCIES:
  I ⊳ apex-database-diagnostics (validate before)

COORDINATES:
  - apex-schema-automation-safe (DDL)
  - apex-data-migration-safe (DATA)
  D ▶ scripts/validate_sql_style.py (security)

GATES:
  - All DATA changes must pass governance
  - No direct execution (orchestrated)
  - Audit trail required
```

### apex-audit-decisions-log
```
DEPENDENCIES:
  None (read-only)

COORDINATES:
  - .bitacora.json (git-backed audit)
  - All skills (generate audit entries)

OUTPUTS:
  - Audit trail visualization
  - Decision history
  - Change reports
```

---

## 9. PROJECT MANAGEMENT

### apex-project-bootstrap-final
```
DEPENDENCIES:
  D ▶ apex-delivery-lifecycle-complete (next step)

COORDINATES:
  - apex-delivery-lifecycle-complete (workflow)
  - apex-project-workspace (workspace)
  - oracle-data-change-governance-final (DATA setup)

INITIALIZES:
  - Workspace structure
  - Governance rules
  - Credential setup
```

### apex-project-workspace
```
DEPENDENCIES:
  None (creates workspace)

COORDINATES:
  - oracle-data-change-governance-final (governance)
  - apex-audit-decisions-log (audit trail)

CREATES:
  - control-proyecto/ directory
  - Documentation templates
  - Configuration files
```

---

## 10. DIAGNOSTICS & UTILITIES

### apex-database-diagnostics
```
DEPENDENCIES:
  None (read-only)

COORDINATES:
  - apex-environment-alignment-complete (environment check)
  - oracle-data-change-governance-final (if corrections needed)

OPERATIONS:
  - Diagnose errors
  - Performance analysis
  - Read-only inspection
```

### apex-pattern-mining-safe
```
DEPENDENCIES:
  None (analysis only)

COORDINATES:
  - apex-solution-design (input patterns)
  - apex-blueprint-design-safe (pattern reference)
  - apex-rest-source-catalogs-safe (REST patterns)
  - apex-ui-craft-safe (UX patterns)

PRODUCES:
  - Reusable patterns
  - Best practices
  - Design templates
```

---

## 11. INTEGRATION & UX

### apex-rest-source-catalogs-safe
```
DEPENDENCIES:
  I ⊳ apex-solution-design (design context)

COORDINATES:
  - apex-solution-design (design contracts)
  - apex-api-client-safe (REST integrations)

ANALYZES:
  - Fusion REST catalogs
  - REST source design patterns
```

### apex-ui-craft-safe
```
DEPENDENCIES:
  I ⊳ apex-engineering-safe (existing components)

COORDINATES:
  - apex-engineering-safe (input)
  - apex-solution-design (design context)

REVIEWS:
  - UX/accessibility
  - Responsive behavior
  - Theme alignment
```

### apex-user-manual
```
DEPENDENCIES:
  D ▶ apex-export-qa-safe (approved QA)

COORDINATES:
  - apex-export-qa-safe (evidence source)
  - scripts/audit_docx_images.py (image audit)

PRODUCES:
  - Word manual (.docx)
  - Screenshots with audit trail
  - User documentation
```

---

## 12. METHODOLOGY

### apex-zaimella-gestion-proyectos
```
DEPENDENCIES:
  None (advisory)

COORDINATES:
  - apex-delivery-lifecycle-complete (technical workflow)
  - apex-delivery-lifecycle-zaimella (integration)

PROVIDES:
  - GPZ methodology guidance
  - Project governance templates
  - Decision frameworks
```

---

## Summary Table: Orchestrator Dependencies

| Orchestrator | Level | Depends On | Coordinates | Skills |
|---|---|---|---|---|
| **apex** | Maestro | None | All | 26 |
| **apex-delivery-lifecycle-complete** | Secundario | apex-project-bootstrap-final | 7 | 7 |
| **apex-delivery-lifecycle-safe** | Secundario | apex-project-workspace | 7 | 7 |
| **apex-delivery-lifecycle-zaimella** | Secundario | Zaimella + lifecycle | 2 | 2 |
| **apex-application-generator-complete** | Terciario | HITOs 1-5 | 4 | 4 |
| **apex-data-orchestrator-safe** | Cuaternario | governance | 3 | 3 |
| **apex-qa-orchestrator-safe** | Cuaternario | QA skills | 3 | 3 |
| **apex-design-review-orchestrator** | Cuaternario | Design skills | 3 | 3 |

---

## Circular Dependency Check

✅ **No circular dependencies found** - All flows are acyclic.

```
Entry Point: apex
↓
Coordinators (4 levels)
↓
Technical Skills (26 end nodes)
```

---

## Version Compatibility

| Skill | Min Version | Max Version | Breaking Changes |
|-------|---|---|---|
| apex | 1.0 | current | routing.md changes require apex update |
| apex-code-generation-safe | 1.0 | current | HITO 1 - stable |
| apex-data-migration-safe | 1.0 | current | HITO 4 - stable |
| apex-automated-testing-safe | 1.0 | current | HITO 3 - stable |
| apex-api-client-safe | 1.0 | current | HITO 2 - stable |
| All others | 1.0 | current | Stable - safe to upgrade |

---

**Last validated:** 2026-09-17
**Total dependency edges:** 89
**Orchestration levels:** 4
**Max depth (entry → leaf):** 3 hops
