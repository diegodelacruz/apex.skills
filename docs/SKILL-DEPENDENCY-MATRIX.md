# Skill Dependency Matrix

> **Policy update (2026-09-28):** Use the credential configured for the requested environment;
> effective Oracle/APEX grants determine available operations. Skills do not hardcode users or
> permission matrices, add approval gates, or ask the user to perform work available to the agent.

**Source inventory:** 31 `skills/*/SKILL.md` files
**Role counts:** 1 entry coordinator, 7 workflow-orchestrator roles, 22 active specialists, 1 retired compatibility entry
**Audit state:** Dependency edges below are a legacy working map and have not been fully revalidated. Do not use this document alone as proof of current dependencies or cycle freedom.

`apex-api-client-safe` is retired and non-operational. Any edge below that assigns it deployment, sync, connectivity, or test setup work is unresolved and must not be treated as an available capability. Native APEX export/import or configured App Builder/MCP routes are documented in `docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`.

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

### apex (L0 Entry Coordinator)
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
  - apex-delivery-lifecycle-zaimella (GPZ projects)
  - oracle-data-change-governance-final (DATA changes)
  - apex-ui-craft-safe (UX)
  - apex-rest-source-catalogs-safe (REST integrations)
  - apex-page-range-governance (page ranges)
```

---

## 2. PRIMARY ORCHESTRATORS

### apex-delivery-lifecycle-complete (L1 Workflow Orchestrator)
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

### apex-delivery-lifecycle-safe (L1 Workflow Orchestrator)
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
  5. apex-engineering-safe (implementation when requested)
  6. apex-export-qa-safe (QA)
  7. apex-user-manual (documentation)
```

### apex-delivery-lifecycle-zaimella (L1 Workflow Orchestrator)
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

### apex-application-generator-complete (L1 Workflow Orchestrator)
```
DEPENDENCIES:
  D ▶ apex-code-generation-safe (generation phase)
  D ▶ apex-data-migration-safe (migration phase)
  D ▶ apex-automated-testing-safe (testing phase)

COORDINATES:
  - apex-code-generation-safe (code gen)
  - apex-data-migration-safe (data mapping/migration)
  - apex-automated-testing-safe (testing)

SEQUENCE:
  1. Code Generation Phase (apex-code-generation-safe)
  2. Data Migration Phase (apex-data-migration-safe)
  3. Testing Phase (apex-automated-testing-safe)
  4. Verification & Reporting (design outline, not an executable full pipeline)
```

APEX artifact import, when requested, is a separate operation through
`apex-page-automation-safe` and the configured native route. The prototype
does not deploy through an API client.

---

## 3. DATA & ORCHESTRATORS

### oracle-data-change-governance-final
```
DEPENDENCIES:
  I ⊳ apex-database-diagnostics (validate before change)

COORDINATES:
  - apex-schema-automation-safe (DDL governance)
  - apex-data-migration-safe (DATA governance)
  - SQL style validator: `skills/oracle-data-change-governance-final/scripts/validate_sql_style.py`

This governance skill documents controls; it does not prohibit the user-requested
direct Oracle route or require an orchestrator.
```

### apex-data-orchestrator-safe (L2 Focused Workflow Outline; not operational end-to-end)
```
DEPENDENCIES:
  D ▶ oracle-data-change-governance-final (governance)

COORDINATES:
  - apex-schema-automation-safe (create schema)
  - apex-data-migration-safe (migrate data)

SEQUENCE:
  1. apex-schema-automation-safe (DDL)
  2. oracle-data-change-governance-final (validate)
  3. apex-data-migration-safe (ETL)
  4. Optional APEX artifact import via `apex-page-automation-safe` and the configured native route; this is not data synchronization and is not implemented by this prototype.
```

### apex-data-migration-safe (specialist)
```
SKILL-DECLARED ADJACENCIES:
  - apex-api-client-safe: explicitly retired; not a prerequisite or execution route
  - apex-code-generation-safe: related generated-object migration context
  - apex-schema-automation-safe: related schema-creation context
  - apex-delivery-lifecycle-safe: optional lifecycle context

OPERATIONAL STATUS:
  - See the skill's current frontmatter and implementation evidence; this map does not certify Oracle execution.
```

### apex-external-context-learn (specialist)
```
SKILL DEPENDENCIES: None declared.
SKILL COORDINATORS: None declared.
SUPPORTING CODE: scripts/external_repo_scanner.py and scripts/external_repo_indexer.py
OUTPUT: Saved external-repository context for later use when requested.
```

---

## 4. CODE GENERATION

### apex-code-generation-safe
```
DEPENDENCIES:
  D ▶ apex-schema-automation-safe (schema exists)
  I ⊳ apex-blueprint-design-safe (optional design context)

COORDINATES:
  - apex-schema-automation-safe (input schema)
  - apex-automated-testing-safe (testing)

PRODUCES:
  - APEX Forms (PL/SQL)
  - APEX Reports (SQL)
  - APEX Validations (PL/SQL)
```

### apex-page-automation-safe
```
DEPENDENCIES:
  D ▶ apex-blueprint-design-safe (design input, not an approval gate)
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
  I ⊳ apex-blueprint-design-safe (optional design context)

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

### apex-design-review-orchestrator (L2 Focused Orchestrator)
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

COORDINATES:
  - apex-code-generation-safe (test target)
  - apex-page-automation-safe (page structure)
  - Configured target application and credentials (not a skill dependency)

TEST TYPES:
  - UI tests (Selenium)
  - Performance tests
  - Regression tests
```

### apex-qa-orchestrator-safe (L2 Focused Orchestrator)
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
  4. Provide environment alignment evidence for the requested scope
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
  - `apex-page-automation-safe` and configured native route for component imports

VALIDATES:
  - TEST ↔ PROD alignment
  - Connection readiness
  - Credentials validity
```

### apex-api-client-safe
```
Status: retired; compatibility name and invocation entry retained.
Operational dependencies, coordination edges, and deployment/synchronization
capabilities: none. The remaining body of its SKILL.md is historical context.
For APEX component import use `apex-page-automation-safe` and the configured
native route in `docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`.
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

WHEN USED:
  - Reserve and validate page ranges when the requested work needs allocation.
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
  - REST source design only; no APEX deployment dependency

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
  D ▶ apex-export-qa-safe (QA evidence, when available)

COORDINATES:
  - apex-export-qa-safe (evidence source)
  - upstream: zaimella-skill audit_docx_images.py (image audit)

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
| **apex** | L0 Entry coordinator | Routes by request | Specialist and workflow routes | 1 |
| **apex-delivery-lifecycle-complete** | L1 Workflow orchestrator | Project bootstrap | Lifecycle specialists | 7* |
| **apex-delivery-lifecycle-safe** | L1 Workflow orchestrator | Project workspace | Lifecycle specialists | 7* |
| **apex-delivery-lifecycle-zaimella** | L1 Workflow orchestrator | GPZ method | Lifecycle workflow | 2* |
| **apex-application-generator-complete** | L1 Workflow prototype | Application generation | 3 declared skill edges; deployment route is separate | 3 |
| **apex-data-orchestrator-safe** | L2 Workflow outline | Data governance | 2 declared skill edges; APEX import is separate |
| **apex-qa-orchestrator-safe** | L2 Focused orchestrator | QA evidence | 3 declared skills |
| **apex-design-review-orchestrator** | L2 Focused orchestrator | Design review | 3 declared skills |

`*` Counts are legacy declarations and need edge-by-edge evidence before use.

---

## Circular Dependency Check

**Not verified.** The legacy graph has not been reconstructed from all active skill files; no acyclic-graph claim is made.

```
L0: apex entry coordinator
L1: four broad workflow orchestrators
L2: three focused workflow orchestrators
L3: 22 active domain specialists (the retired API compatibility entry is excluded)
```

---

## Runtime compatibility

This static dependency map does not certify runtime compatibility. Check the
skill's current frontmatter and the configured target before claiming execution.

---

**Full edge count, cycle status, and maximum depth:** pending revalidation.
