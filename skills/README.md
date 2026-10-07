# 📚 APEX Skills Catalog

Complete directory of **31 skills** organized by role and workflow:
- **22 active specialist skills:** Technical, data, design, QA, governance, and project support
- **1 retired compatibility entry:** `apex-api-client-safe`; invocation name retained, capability unavailable
- **7 workflow-orchestrator roles:** Four broad lifecycle/application flows and three focused sub-workflows; development outlines are identified in metadata
- **1 Entry coordinator:** Routes requests to the smallest useful workflow (`apex`)

Use `/skills` in Codex/Claude to see the complete list with descriptions and tags. This page provides detailed navigation and quick reference.

---

## Canonical metadata inventory

This table is derived from every `skills/*/SKILL.md` frontmatter. The source files remain authoritative.

| Directory | Name | Category | Order | Status | Tags | Description |
|---|---|---|---:|---|---|---|
| apex | apex | Apex Coordinator | 14 | active | coordinator, routing, governance | Route Oracle and APEX requests to the smallest useful specialist workflow. |
| apex-api-client-safe | apex-api-client-safe | Apex Integration | 22 | retired | retired, compatibility, historical | Retired simulated REST adapter; it must not be used for Oracle APEX deployment. |
| apex-application-generator-complete | apex-application-generator-complete | Apex Application Development | 23 | development | application-generation, orchestration, end-to-end, automation, deployment, testing, migration | Development prototype for an end-to-end APEX application workflow; its API deployment phase is non-operational |
| apex-audit-decisions-log | apex-audit-decisions-log | Apex Audit & Decisions | 0 | active | audit, documentation, decisions, governance, read-only | Review and export project decisions and the Git-backed audit trail. |
| apex-automated-testing-safe | apex-automated-testing-safe | Apex Testing & QA | 21 | development | testing, automation, selenium, performance, regression, qa | Selenium test generation, performance testing, and regression validation framework |
| apex-blueprint-design-safe | apex-blueprint-design-safe | Apex Engineering & Design | 15 | active | blueprint, design, scaffolding, read-only | Create reviewable APEX blueprints from user requirements and available metadata. |
| apex-code-generation-safe | apex-code-generation-safe | Apex Engineering & Design | 24 | development | code-generation, apex, forms, reports, automation, read-only | Generate APEX components automatically from schema and metadata |
| apex-data-migration-safe | apex-data-migration-safe | Apex Data Integration | 25 | development | data-migration, etl, schema-mapping, validation, rollback, data-sync | Schema mapping, data validation, ETL pipeline, and rollback management framework |
| apex-data-orchestrator-safe | apex-data-orchestrator-safe | Apex Data Integration | 13.5 | development | orchestration, data-integration, schema, etl, migration, automation | Development outline for schema and data migration workflows; APEX artifact import is separate |
| apex-database-diagnostics | apex-database-diagnostics | Apex Database & Diagnostics | 1 | active | diagnostics, inspection, oracle | Diagnose Oracle and APEX requests in the user-selected environment through available authenticated routes. |
| apex-delivery-lifecycle-complete | apex-delivery-lifecycle-complete | Apex Delivery & Lifecycle | 2 | active | lifecycle, workflow, release, governance | Run the complete APEX lifecycle with environment and DATA governance. |
| apex-delivery-lifecycle-safe | apex-delivery-lifecycle-safe | Apex Delivery & Lifecycle | 3 | active | lifecycle, workflow, qa, governance | Coordinate a safe APEX workflow from design through QA and documentation. |
| apex-delivery-lifecycle-zaimella | apex-delivery-lifecycle-zaimella | Apex Delivery & Lifecycle | 3.5 | development | orchestration, delivery-lifecycle, methodology, gpz, zaimella, governance, project-management | Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle for comprehensive project governance |
| apex-design-review-orchestrator | apex-design-review-orchestrator | Apex Engineering & Design | 11.5 | active | design, review, orchestration | Coordinate APEX solution, blueprint, and engineering review without adding execution gates. |
| apex-engineering-safe | apex-engineering-safe | Apex Engineering & Design | 4 | active | inspection, design, export, implementation | Inspect, design, and implement APEX applications from exports within the user's environment matrix. |
| apex-environment-alignment-complete | apex-environment-alignment-complete | Apex Environment & Alignment | 5 | active | environment, alignment, validation, governance | Validate and align TEST and production APEX environments safely. |
| apex-export-qa-safe | apex-export-qa-safe | Apex Export & QA | 6 | active | qa, validation, export, read-only | Validate APEX export ZIP structure and readiness before changes. |
| apex-external-context-learn | apex-external-context-learn | Apex External Context & Learning | 3.5 | active | external-context, learning, no-clone, reference, read-only, discovery | Learn from external repositories (GitHub or local) without cloning. Create persistent, reusable reference context for APEX engineering workflows. |
| apex-page-automation-safe | apex-page-automation-safe | Apex Engineering & Design | 19 | active | page-creation, automation, design, full-stack | Create, modify, and deploy APEX pages via native export/import through SQLcl. |
| apex-page-range-governance | apex-page-range-governance | Apex Page Range Governance | 7 | active | governance, pages, validation | Reserve and validate conflict-free APEX page ranges by project. |
| apex-pattern-mining-safe | apex-pattern-mining-safe | Apex Pattern Mining | 8 | active | patterns, analysis, export, read-only | Extract reusable APEX design patterns from application exports safely. |
| apex-project-bootstrap-final | apex-project-bootstrap-final | Apex Project Management | 9 | active | setup, initialization, bootstrap, governance | Initialize an APEX project with workspace and governance foundations. |
| apex-project-workspace | apex-project-workspace | Apex Project Management | 10 | active | workspace, organization, documentation | Create and maintain the control-proyecto project workspace. |
| apex-qa-orchestrator-safe | apex-qa-orchestrator-safe | Apex QA | 6.5 | active | qa, validation, orchestration | Coordinate APEX QA evidence and report results without approval gates. |
| apex-rest-source-catalogs-safe | apex-rest-source-catalogs-safe | Apex Integration | 16 | active | rest, fusion, integration, catalog, read-only | Assess Fusion REST catalogs for safe APEX integration design. |
| apex-schema-automation-safe | apex-schema-automation-safe | Apex Database & Schema | 20 | active | database, schema, ddl, automation, full-stack | Create, modify, and drop Oracle database objects through available authenticated routes. |
| apex-solution-design | apex-solution-design | Apex Engineering & Design | 11 | active | design, architecture, planning | Design APEX applications and pages from approved business requirements. |
| apex-ui-craft-safe | apex-ui-craft-safe | Apex UX Craft | 17 | active | ux, accessibility, responsive, motion, read-only | Assess and improve accessible, responsive APEX UX with Universal Theme. |
| apex-user-manual | apex-user-manual | Apex Documentation | 12 | active | documentation, automation, export | Generate and verify Word user manuals from approved APEX QA evidence. |
| apex-zaimella-gestion-proyectos | apex-zaimella-gestion-proyectos | Zaimella Methodology | 18 | active | zaimella, gpz, metodologia, proyectos, gestion, formativo | Asesor metodológico y operativo para gestión integral de proyectos bajo Metodología GPZ (Gestión de Proyectos Zaimella). |
| oracle-data-change-governance-final | oracle-data-change-governance-final | Oracle Data Governance | 13 | active | database, governance, audit | Govern DATA changes with decisions, rollback, validation, and audit evidence. |

## 🎯 Quick Navigation

### Apex Audit & Decisions Log
- **[apex-audit-decisions-log](./apex-audit-decisions-log)** - Review and export project decisions and the Git-backed audit trail.
  - *Tags: audit, documentation, decisions, governance, read-only*

### Apex Database & Diagnostics
- **[apex-database-diagnostics](./apex-database-diagnostics)** - Diagnose Oracle and APEX requests in the user-selected environment through available authenticated routes.
  - *Tags: diagnostics, inspection, oracle*

### Apex Database & Schema
- **[apex-schema-automation-safe](./apex-schema-automation-safe)** - Create, modify, and drop Oracle database objects through available authenticated routes.
  - *Tags: database, schema, ddl, automation, full-stack*

### Apex Delivery & Lifecycle
- **[apex-delivery-lifecycle-complete](./apex-delivery-lifecycle-complete)** - Run the complete APEX lifecycle with environment and DATA governance.
  - *Tags: lifecycle, workflow, release, governance*
- **[apex-delivery-lifecycle-safe](./apex-delivery-lifecycle-safe)** - Coordinate a safe APEX workflow from design through QA and documentation.
  - *Tags: lifecycle, workflow, qa, governance*
- **[apex-delivery-lifecycle-zaimella](./apex-delivery-lifecycle-zaimella)** - Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle for comprehensive project governance
  - *Tags: orchestration, delivery-lifecycle, methodology, gpz, zaimella, governance, project-management*

### Apex External Context & Learning
- **[apex-external-context-learn](./apex-external-context-learn)** - Learn from external repositories (GitHub or local) without cloning. Create persistent, reusable reference context for APEX engineering workflows.
  - *Tags: external-context, learning, no-clone, reference, read-only, discovery*

### Apex Code Generation
- **[apex-code-generation-safe](./apex-code-generation-safe)** - Generate APEX components automatically from schema and metadata
  - *Tags: code-generation, apex, forms, reports, automation, read-only*

### Apex Engineering & Design
- **[apex-engineering-safe](./apex-engineering-safe)** - Inspect, design, and implement APEX applications from exports within the user's environment matrix.
  - *Tags: inspection, design, export, implementation*
- **[apex-solution-design](./apex-solution-design)** - Design APEX applications and pages from approved business requirements.
  - *Tags: design, architecture, planning*
- **[apex-blueprint-design-safe](./apex-blueprint-design-safe)** - Create reviewable APEX blueprints from user requirements and available metadata.
  - *Tags: blueprint, design, scaffolding, read-only*
- **[apex-ui-craft-safe](./apex-ui-craft-safe)** - Assess and improve accessible, responsive APEX UX with Universal Theme.
  - *Tags: ux, accessibility, responsive, motion, read-only*

### Apex Page Automation
- **[apex-page-automation-safe](./apex-page-automation-safe)** - Create, modify, and deploy APEX pages via native export/import through SQLcl.
  - *Tags: page-creation, automation, design, full-stack*

### Apex Environment & Alignment
- **[apex-environment-alignment-complete](./apex-environment-alignment-complete)** - Validate and align TEST and production APEX environments safely.
  - *Tags: environment, alignment, validation, governance*

### Apex Export & QA
- **[apex-export-qa-safe](./apex-export-qa-safe)** - Validate APEX export ZIP structure and readiness before changes.
  - *Tags: qa, validation, export, read-only*
- **[apex-automated-testing-safe](./apex-automated-testing-safe)** - Selenium test generation, performance testing, and regression validation framework
  - *Tags: testing, automation, selenium, performance, regression, qa*
  - *Tags: qa, validation, export, read-only*

### Retired compatibility entry
- **[apex-api-client-safe](./apex-api-client-safe)** - Retired simulated REST adapter; it must not be used for Oracle APEX deployment.
  - *Status: retired; retained for historical context and invocation compatibility*

### Apex Integration
- **[apex-rest-source-catalogs-safe](./apex-rest-source-catalogs-safe)** - Assess Fusion REST catalogs for safe APEX integration design.
  - *Tags: rest, fusion, integration, catalog, read-only*

### Zaimella Methodology
- **[apex-zaimella-gestion-proyectos](./apex-zaimella-gestion-proyectos)** - Asesor metodológico y operativo para gestión integral de proyectos bajo Metodología GPZ (Gestión de Proyectos Zaimella).
  - *Tags: zaimella, gpz, metodologia, proyectos, gestion, formativo*

### Apex Page Range Governance
- **[apex-page-range-governance](./apex-page-range-governance)** - Reserve and validate conflict-free APEX page ranges by project.
  - *Tags: governance, pages, validation*

### Apex Pattern Mining
- **[apex-pattern-mining-safe](./apex-pattern-mining-safe)** - Extract reusable APEX design patterns from application exports safely.
  - *Tags: patterns, analysis, export, read-only*

### Apex Project Management
- **[apex-project-bootstrap-final](./apex-project-bootstrap-final)** - Initialize an APEX project with workspace and governance foundations.
  - *Tags: setup, initialization, bootstrap, governance*
- **[apex-project-workspace](./apex-project-workspace)** - Create and maintain the control-proyecto project workspace.
  - *Tags: workspace, organization, documentation*

### Apex Documentation
- **[apex-user-manual](./apex-user-manual)** - Generate and verify Word user manuals from approved APEX QA evidence.
  - *Tags: documentation, automation, export*

### Apex Coordinators & Orchestrators

#### Entry coordinator
- **[apex](./apex)** - Route Oracle and APEX requests to the smallest useful specialist workflow.
  - *Tags: coordinator, routing, governance*

#### Workflow orchestrators
- **[apex-application-generator-complete](./apex-application-generator-complete)** - Development prototype for an end-to-end APEX application workflow; its API deployment phase is non-operational
  - *Tags: application-generation, orchestration, end-to-end, automation, deployment, testing, migration*
- **[apex-data-orchestrator-safe](./apex-data-orchestrator-safe)** - Development outline for schema and data migration workflows; APEX artifact import is separate
  - *Tags: orchestration, data-integration, schema, etl, migration, automation*
- **[apex-qa-orchestrator-safe](./apex-qa-orchestrator-safe)** - Coordinate APEX QA evidence and report results without approval gates.
  - *Tags: qa, validation, orchestration*
- **[apex-design-review-orchestrator](./apex-design-review-orchestrator)** - Coordinate APEX solution, blueprint, and engineering review without adding execution gates.
  - *Tags: design, review, orchestration*

### Apex Data Migration
- **[apex-data-migration-safe](./apex-data-migration-safe)** - Schema mapping, data validation, ETL pipeline, and rollback management framework
  - *Tags: data-migration, etl, schema-mapping, validation, rollback, data-sync*

### Oracle Data Governance
- **[oracle-data-change-governance-final](./oracle-data-change-governance-final)** - Govern DATA changes with decisions, rollback, validation, and audit evidence.
  - *Tags: database, governance, audit*

---

## 📊 Skills by Category

### By Workflow Type
| Workflow | Skills |
|----------|--------|
| **Orchestration & Coordination** | apex, apex-delivery-lifecycle-complete, apex-delivery-lifecycle-safe, apex-delivery-lifecycle-zaimella, apex-application-generator-complete, apex-data-orchestrator-safe, apex-qa-orchestrator-safe, apex-design-review-orchestrator |
| **Design & Planning** | apex-solution-design, apex-blueprint-design-safe, apex-pattern-mining-safe, apex-ui-craft-safe |
| **Engineering & Implementation** | apex-engineering-safe, apex-page-automation-safe, apex-code-generation-safe, apex-schema-automation-safe |
| **Quality & Validation** | apex-export-qa-safe, apex-automated-testing-safe, apex-environment-alignment-complete |
| **Data Integration** | apex-data-migration-safe, oracle-data-change-governance-final |
| **Governance & Audit** | apex-page-range-governance, oracle-data-change-governance-final, apex-audit-decisions-log |
| **Project Management** | apex-project-bootstrap-final, apex-project-workspace |
| **Project Methodology** | apex-zaimella-gestion-proyectos |
| **External Context & Learning** | apex-external-context-learn |
| **Documentation** | apex-user-manual |
| **Diagnostics** | apex-database-diagnostics |
| **Integration** | apex-rest-source-catalogs-safe |

### By Access Level
| Access | Skills |
|--------|--------|
| **Read-only** | apex-engineering-safe, apex-export-qa-safe, apex-pattern-mining-safe, apex-rest-source-catalogs-safe, apex-ui-craft-safe, apex-database-diagnostics, apex-audit-decisions-log |
| **Read-write** | apex-solution-design, apex-page-automation-safe, apex-page-range-governance, apex-project-bootstrap-final, apex-project-workspace, apex-user-manual, apex-delivery-lifecycle-safe, apex-delivery-lifecycle-complete, apex-environment-alignment-complete, oracle-data-change-governance-final, apex-zaimella-gestion-proyectos |

---

## 🚀 Getting Started

1. **New Project?** Start with `/apex-project-bootstrap-final`
2. **Need Help?** Use `/apex` (coordinator) - it understands your request
3. **Want to Audit?** Use `/apex-audit-decisions-log` to see all decisions

---

## 📋 All Skills (Alphabetical)

1. apex (Entry Coordinator)
2. apex-api-client-safe (Retired compatibility name)
3. apex-application-generator-complete (Orchestrator)
4. apex-audit-decisions-log
5. apex-automated-testing-safe
6. apex-blueprint-design-safe
7. apex-code-generation-safe
8. apex-data-migration-safe
9. apex-data-orchestrator-safe (Orchestrator)
10. apex-database-diagnostics
11. apex-delivery-lifecycle-complete
12. apex-delivery-lifecycle-safe
13. apex-delivery-lifecycle-zaimella (Orchestrator)
14. apex-design-review-orchestrator (Orchestrator)
15. apex-engineering-safe
16. apex-environment-alignment-complete
17. apex-external-context-learn
18. apex-export-qa-safe
19. apex-page-automation-safe
20. apex-page-range-governance
21. apex-pattern-mining-safe
22. apex-project-bootstrap-final
23. apex-project-workspace
24. apex-qa-orchestrator-safe (Orchestrator)
25. apex-rest-source-catalogs-safe
26. apex-schema-automation-safe
27. apex-solution-design
28. apex-ui-craft-safe
29. apex-user-manual
30. apex-zaimella-gestion-proyectos
31. oracle-data-change-governance-final

---

**For detailed information about each skill, see the individual SKILL.md files in this directory.**
