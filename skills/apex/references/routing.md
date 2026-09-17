# Routing table

**Updated:** 2026-09-17
**Orchestrators:** 4 maestros (1 entry point, 3 coordinators + 3 sub-coordinators)
**Skills:** 26 specialized skills

## Primary Routing (Entry Points)

| User intent | Orchestrator/Workflow | Orchestration |
| --- | --- | --- |
| **Start a new APEX project (standard)** | `apex-project-bootstrap-final` → `apex-project-workspace` → `apex-delivery-lifecycle-complete` | ✓ Coordinated |
| **Start a new APEX project (safe workflow)** | `apex-project-workspace` → `apex-delivery-lifecycle-safe` | ✓ Coordinated |
| **Start a new project under GPZ methodology** | `apex-delivery-lifecycle-zaimella` (integrates Zaimella + APEX workflow) | ✓ Coordinated (NEW) |
| **Generate complete APEX application (end-to-end)** | `apex-application-generator-complete` (orchestrates HITOs 1-5) | ✓ Coordinated |

## Specialized Workflows

### Design & Engineering
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Learn from ZIP exports | `apex-pattern-mining-safe` → `apex-solution-design` | ⊳ Recommended |
| Full design review (solution → blueprint → engineering) | `apex-design-review-orchestrator` (NEW - coordinates 3-phase review) | ✓ Coordinated |
| Design an application blueprint before implementation | `apex-blueprint-design-safe` → `apex-solution-design` | ⊳ Recommended |
| Design or edit APEX | `apex-engineering-safe`; add `apex-ui-craft-safe` for UX/responsive/accessibility; add alignment for existing pages | ◎ Optional |

### Database & Data
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Full data workflow (schema → migration → sync) | `apex-data-orchestrator-safe` (NEW - coordinates schema/ETL/sync) | ✓ Coordinated |
| DATA object change (governance required) | `oracle-data-change-governance-final` | ✓ Gated |
| Create/modify database schema | `apex-schema-automation-safe` (under `oracle-data-change-governance-final`) | ✓ Gated |
| Migrate data between environments | `apex-data-migration-safe` (under `oracle-data-change-governance-final`) | ✓ Gated |

### QA & Testing
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Full QA & testing workflow (static → automated → environment) | `apex-qa-orchestrator-safe` (NEW - coordinates 3-phase testing) | ✓ Coordinated |
| Export/static QA only | `apex-export-qa-safe` | ◎ First phase |
| Automated testing (UI/performance/regression) | `apex-automated-testing-safe` | ◎ Second phase |

### Environment & Deployment
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| TEST/production copy, release, or environment alignment | `apex-environment-alignment-complete` → `apex-delivery-lifecycle-complete` | ⊳ Recommended |
| Inspect APEX/Oracle, diagnose an error, or investigate slowness/performance | `apex-database-diagnostics`; add `apex-environment-alignment-complete` for existing-page changes | ◎ Optional |
| Optimize an Oracle object, query, or PL/SQL execution | `apex-database-diagnostics`; add `oracle-data-change-governance-final` only when a change is requested | ⊳ Recommended |

### Integration & Documentation
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Assess Fusion REST Source Catalogs or plan an APEX REST integration | `apex-rest-source-catalogs-safe` | ◎ Optional |
| Review UX, Universal Theme, accessibility, responsive behavior, or motion | `apex-ui-craft-safe`; add alignment only for an approved existing-page change | ◎ Optional |
| Final Word manual from approved QA evidence | `apex-user-manual` (requires `apex-export-qa-safe` approval) | ⊳ Recommended |

### Governance
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Application/project/page range management | `apex-page-range-governance` | ✓ Gate |
| Audit trail & decision history | `apex-audit-decisions-log` | ◎ Read-only |

### Methodology
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| GPZ (Zaimella) methodology guidance & project governance | `apex-zaimella-gestion-proyectos` (advisory, integrates with `apex-delivery-lifecycle-zaimella`) | ◎ Advisory |

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✓ Coordinated | Orchestrator coordinates multiple skills in defined sequence |
| ⊳ Recommended | Skills should run in order shown (not strict orchestration) |
| ◎ Optional | Can integrate if available; not required |
| ✗ Gated | Must pass approval/validation gate before proceeding |

---

## New Orchestrators (2026-09-17)

### 1. apex-delivery-lifecycle-zaimella (Coordinator)
**Purpose:** Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle
**Coordinates:** `apex-zaimella-gestion-proyectos` + `apex-delivery-lifecycle-complete`
**Sequence:**
1. Setup GPZ project (Zaimella)
2. Execute APEX workflow (Zaimella-governed)
3. Close-out GPZ project (Zaimella)

### 2. apex-data-orchestrator-safe (Sub-Coordinator)
**Purpose:** Coordinate schema creation → data migration → APEX sync
**Coordinates:** `apex-schema-automation-safe` → `apex-data-migration-safe` → `apex-api-client-safe`
**Governance:** Under `oracle-data-change-governance-final`

### 3. apex-qa-orchestrator-safe (Sub-Coordinator)
**Purpose:** Coordinate static QA → automated testing → environment validation
**Coordinates:** `apex-export-qa-safe` → `apex-automated-testing-safe` → `apex-environment-alignment-complete`
**Gate:** All phases must pass before release approved

### 4. apex-design-review-orchestrator (Sub-Coordinator)
**Purpose:** Coordinate design review: solution → blueprint → engineering
**Coordinates:** `apex-solution-design` → `apex-blueprint-design-safe` → `apex-engineering-safe`
**Gate:** Approval required after each phase before proceeding

---

## Explicitly named specialist skills

Take precedence when they do not conflict with safety or approval requirements.
