# Routing table

**Inventory:** 31 entries: 1 entry coordinator, 7 workflow-orchestrator roles, 22 active specialists, and 1 retired compatibility entry.
**Classification:** Coordinators route requests; orchestrators coordinate a multi-skill workflow; specialists perform one domain task.

## Primary Routing (Entry Points)

| User intent | Orchestrator/Workflow | Orchestration |
| --- | --- | --- |
| **Start a new APEX project (standard)** | `apex-project-bootstrap-final` → `apex-project-workspace` → `apex-delivery-lifecycle-complete` | ✓ Coordinated |
| **Start a new APEX project (safe workflow)** | `apex-project-workspace` → `apex-delivery-lifecycle-safe` | ✓ Coordinated |
| **Start a new project under GPZ methodology** | `apex-delivery-lifecycle-zaimella` (integrates Zaimella + APEX workflow) | ✓ Coordinated |
| **Build and deliver an APEX application** | `apex-delivery-lifecycle-complete` → relevant design, generation, page-import, QA, and documentation specialists | ✓ Workflow coordinated; report each operation's actual evidence |
| **Review the application-generation prototype** | `apex-application-generator-complete` | △ Development outline; its deployment phase is not operational |
| **Learn from an external repository** | `apex-external-context-learn` | ◎ Specialist |
| **Generate APEX forms, reports, validations, or components** | `apex-code-generation-safe` | ◎ Specialist |
| **Create or modify APEX pages** | `apex-page-automation-safe` using native export/import and configured APEX tools | ◎ Specialist |

## Specialized Workflows

### Design & Engineering
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Learn from ZIP exports | `apex-pattern-mining-safe` → `apex-solution-design` | ⊳ Recommended |
| Full design review (solution → blueprint → engineering) | `apex-design-review-orchestrator` (coordinates three phases) | ✓ Coordinated |
| Design an application blueprint before implementation | `apex-blueprint-design-safe` → `apex-solution-design` | ⊳ Recommended |
| Design or edit APEX | `apex-engineering-safe`; add `apex-ui-craft-safe` for UX/responsive/accessibility; alignment is optional evidence | ◎ Optional |

### Database & Data
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| **Plan schema and Oracle data migration work** | `apex-data-orchestrator-safe` | △ Development outline; no end-to-end executor |
| **Import APEX component artifacts** | `apex-page-automation-safe` using the configured native import route | ◎ Specialist; separate from Oracle data migration |
| DATA object change (governance guidance) | `oracle-data-change-governance-final` | ⊳ Advisory |
| Create/modify database schema (owner defaults to DATA) | `apex-schema-automation-safe` | ⊳ Advisory |

For a request that follows a completed diagnosis with an explicit change
confirmation, retain the diagnostic context and use the common
`live-change-protocol.md`; route only the implementation to the matching
specialist. A fingerprint mismatch returns to diagnosis before any apply step.
| Migrate data between environments | `apex-data-migration-safe` | ⊳ Advisory |

For requested Oracle schema object creation or changes, default the owner to
`DATA` unless the user explicitly names another schema. Qualify
the DDL and related DML with that owner; the connected account's schema is
never an implicit fallback. Preserve specific governance exceptions such as
backup objects in the connected user's schema.

### QA & Testing
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Full QA & testing workflow (static → automated → environment) | `apex-qa-orchestrator-safe` (coordinates three phases) | ✓ Coordinated |
| Export/static QA only | `apex-export-qa-safe` | ◎ First phase |
| Automated testing (UI/performance/regression) | `apex-automated-testing-safe` | ◎ Second phase |

### Environment & Deployment
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| TEST/production copy, release, or environment alignment | `apex-environment-alignment-complete` → `apex-delivery-lifecycle-complete`; use native import/App Builder instead of the retired simulated REST adapter | ⊳ Recommended |
| Inspect APEX/Oracle, diagnose an error, or investigate slowness/performance | `apex-database-diagnostics`; add `apex-environment-alignment-complete` for existing-page changes | ◎ Optional |
| Optimize an Oracle object, query, or PL/SQL execution | `apex-database-diagnostics`; add `oracle-data-change-governance-final` only when a change is requested | ⊳ Recommended |

### Integration & Documentation
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Assess Fusion REST Source Catalogs or plan an APEX REST integration | `apex-rest-source-catalogs-safe` | ◎ Optional |
| Review UX, Universal Theme, accessibility, responsive behavior, or motion | `apex-ui-craft-safe`; alignment findings are optional evidence and do not gate implementation | ◎ Optional |
| Final Word manual from available QA evidence | `apex-user-manual` (QA evidence is input, not an approval gate) | ⊳ Recommended |

### Governance
| User intent | Specialist workflow | Coordination |
| --- | --- | --- |
| Application/project/page range management | `apex-page-range-governance` | ⊳ Advisory |
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
| ✗ Gated | Legacy workflow label; not an authorization or execution requirement |

---

## Orchestrator Map

| Workflow role | Current status and scope |
|---|---|
| `apex-delivery-lifecycle-complete` | Broad lifecycle workflow; follow its current `SKILL.md` and target evidence |
| `apex-delivery-lifecycle-safe` | Broad lifecycle workflow; follow its current `SKILL.md` and target evidence |
| `apex-delivery-lifecycle-zaimella` | Development status; GPZ and APEX coordination |
| `apex-application-generator-complete` | Development prototype; deployment phase is unavailable through the retired API adapter |
| `apex-data-orchestrator-safe` | Development outline; APEX component import is separate |
| `apex-qa-orchestrator-safe` | QA evidence workflow; does not add an approval gate |
| `apex-design-review-orchestrator` | Advisory design workflow; implementation continues when requested |

### 1. apex-delivery-lifecycle-zaimella (Coordinator)
**Purpose:** Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle
**Coordinates:** `apex-zaimella-gestion-proyectos` + `apex-delivery-lifecycle-complete`
**Sequence:**
1. Setup GPZ project (Zaimella)
2. Execute APEX workflow (Zaimella-governed)
3. Close-out GPZ project (Zaimella)

### 2. apex-data-orchestrator-safe (L2 focused workflow outline)
**Purpose:** Outline schema, validation, and Oracle data migration work.
**Coordinates:** `apex-schema-automation-safe` → `apex-data-migration-safe`.
APEX component import is a separate optional operation via the configured
native route; this outline does not implement end-to-end synchronization.

### 3. apex-qa-orchestrator-safe (L2 focused workflow orchestrator)
**Purpose:** Coordinate static QA → automated testing → environment validation
**Coordinates:** `apex-export-qa-safe` → `apex-automated-testing-safe` → `apex-environment-alignment-complete`
**Sequence:** Review phases inform the requested release; service permissions determine execution.

### 4. apex-design-review-orchestrator (L2 focused workflow orchestrator)
**Purpose:** Coordinate design review: solution → blueprint → engineering
**Coordinates:** `apex-solution-design` → `apex-blueprint-design-safe` → `apex-engineering-safe`
**Sequence:** Review phases are advisory; proceed within the user's stated scope.

---

## Explicitly named specialist skills

Route by the user's requested outcome and available evidence. Skills do not add approval gates.
