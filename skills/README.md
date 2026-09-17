# 📚 APEX Skills Catalog

Complete directory of **30 skills** (26 technical + 4 orchestrators) organized by purpose and workflow:
- **26 Technical Skills:** Code generation, testing, data integration, design, QA, governance, project management
- **4 Orchestrators (NEW):** Coordinate entire workflows with approval gates
- **1 Maestro:** Central routing coordinator (apex)

Use `/skills` in Codex/Claude to see the complete list with descriptions and tags. This page provides detailed navigation and quick reference.

---

## 🎯 Quick Navigation

### Apex Audit & Decisions Log
- **[apex-audit-decisions-log](./apex-audit-decisions-log)** - View audit trail, decisions, and compliance reports
  - *Tags: audit, documentation, decisions, governance*

### Apex Database & Diagnostics
- **[apex-database-diagnostics](./apex-database-diagnostics)** - Diagnose APEX and Oracle database errors
  - *Tags: diagnostics, inspection, oracle, read-only*

### Apex Database & Schema
- **[apex-schema-automation-safe](./apex-schema-automation-safe)** - Create, modify, and drop database objects (tables, views, procedures, functions)
  - *Tags: database, schema, ddl, automation, full-stack, approval-gated*

### Apex Delivery & Lifecycle
- **[apex-delivery-lifecycle-complete](./apex-delivery-lifecycle-complete)** - Complete lifecycle with environment validation and DATA governance
  - *Tags: lifecycle, workflow, complete, governance*
- **[apex-delivery-lifecycle-safe](./apex-delivery-lifecycle-safe)** - Safe end-to-end workflow: design → dev → QA → docs
  - *Tags: lifecycle, workflow, safe, governance*
- **[apex-delivery-lifecycle-zaimella](./apex-delivery-lifecycle-zaimella)** (NEW) - Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle
  - *Tags: lifecycle, orchestration, methodology, gpz, zaimella*

### Apex Code Generation
- **[apex-code-generation-safe](./apex-code-generation-safe)** - Generate APEX components automatically from schema and metadata
  - *Tags: code-generation, apex, forms, reports, validations*

### Apex Engineering & Design
- **[apex-engineering-safe](./apex-engineering-safe)** - Safely inspect, design, and document APEX applications
  - *Tags: inspection, design, export, read-only*
- **[apex-solution-design](./apex-solution-design)** - Design new APEX apps/pages from business requirements
  - *Tags: design, architecture, planning*
- **[apex-blueprint-design-safe](./apex-blueprint-design-safe)** - Create a reviewable blueprint before implementation
  - *Tags: blueprint, design, scaffolding, read-only, approval*
- **[apex-ui-craft-safe](./apex-ui-craft-safe)** - Improve APEX UX, accessibility, responsive behavior, and visual polish
  - *Tags: ux, ui, responsive, accessibility, motion, read-only*

### Apex Page Automation
- **[apex-page-automation-safe](./apex-page-automation-safe)** - Create, modify, and delete APEX pages with full component control
  - *Tags: page-creation, automation, design, full-stack, approval-gated*

### Apex Environment & Alignment
- **[apex-environment-alignment-complete](./apex-environment-alignment-complete)** - Validate and sync TEST/production environments
  - *Tags: environment, sync, validation, governance*

### Apex Export & QA
- **[apex-export-qa-safe](./apex-export-qa-safe)** - Static QA for APEX exports before changes
  - *Tags: qa, validation, export, read-only*
- **[apex-automated-testing-safe](./apex-automated-testing-safe)** - Selenium test generation, performance testing, and regression validation
  - *Tags: testing, automation, selenium, performance*
  - *Tags: qa, validation, export, read-only*

### Apex Integration
- **[apex-api-client-safe](./apex-api-client-safe)** - REST API client for Oracle APEX deployment and environment management
  - *Tags: rest-api, deployment, environment-sync, automation*
- **[apex-rest-source-catalogs-safe](./apex-rest-source-catalogs-safe)** - Assess Fusion REST catalogs for safe APEX integration
  - *Tags: rest, fusion, integration, catalog, read-only*

### Zaimella Methodology
- **[apex-zaimella-gestion-proyectos](./apex-zaimella-gestion-proyectos)** - GPZ: Asesor metodológico para gestión integral de proyectos (RI → AD → DP → EJ → CI)
  - *Tags: zaimella, gpz, metodologia, proyectos, gestion, simon, formativo*

### Apex Page Range Governance
- **[apex-page-range-governance](./apex-page-range-governance)** - Reserve and validate page ranges by project
  - *Tags: governance, pages, validation*

### Apex Pattern Mining
- **[apex-pattern-mining-safe](./apex-pattern-mining-safe)** - Extract reusable patterns from APEX exports
  - *Tags: patterns, analysis, export, read-only*

### Apex Project Management
- **[apex-project-bootstrap-final](./apex-project-bootstrap-final)** - Initialize project with workspace and policies
  - *Tags: setup, initialization, bootstrap*
- **[apex-project-workspace](./apex-project-workspace)** - Create and maintain control-proyecto workspace
  - *Tags: workspace, organization, management*

### Apex Documentation
- **[apex-user-manual](./apex-user-manual)** - Generate Word manual from QA evidence
  - *Tags: documentation, automation, export*

### Apex Coordinators & Orchestrators

#### Maestro (Entry Point)
- **[apex](./apex)** - Main entry point: understands requests and routes to specialists
  - *Tags: coordinator, routing, gateway, orchestration*

#### Sub-Coordinators (NEW - Specialized Orchestrators)
- **[apex-application-generator-complete](./apex-application-generator-complete)** - End-to-end APEX app generation (orchestrates HITOs 1-5)
  - *Tags: orchestration, application-generation, end-to-end, automation*
- **[apex-data-orchestrator-safe](./apex-data-orchestrator-safe)** (NEW) - Coordinate schema → migration → sync
  - *Tags: orchestration, data-integration, schema, etl, automation*
- **[apex-qa-orchestrator-safe](./apex-qa-orchestrator-safe)** (NEW) - Coordinate static QA → automated testing → environment validation
  - *Tags: orchestration, qa, testing, automation, approval-gated*
- **[apex-design-review-orchestrator](./apex-design-review-orchestrator)** (NEW) - Coordinate design review with approval gates
  - *Tags: orchestration, design, review, approval-gated, governance*

### Apex Data Migration
- **[apex-data-migration-safe](./apex-data-migration-safe)** - Schema mapping, data validation, ETL pipeline, and rollback management
  - *Tags: data-migration, etl, schema-mapping, validation*

### Oracle Data Governance
- **[oracle-data-change-governance-final](./oracle-data-change-governance-final)** - Govern DATA changes with audit trail
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
| **Data Integration** | apex-data-migration-safe, apex-api-client-safe, oracle-data-change-governance-final |
| **Governance & Audit** | apex-page-range-governance, oracle-data-change-governance-final, apex-audit-decisions-log |
| **Project Management** | apex-project-bootstrap-final, apex-project-workspace |
| **Project Methodology** | apex-zaimella-gestion-proyectos |
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

1. apex (Maestro Coordinator)
2. apex-api-client-safe
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
17. apex-export-qa-safe
18. apex-page-automation-safe
19. apex-page-range-governance
20. apex-pattern-mining-safe
21. apex-project-bootstrap-final
22. apex-project-workspace
23. apex-qa-orchestrator-safe (Orchestrator)
24. apex-rest-source-catalogs-safe
25. apex-schema-automation-safe
26. apex-solution-design
27. apex-ui-craft-safe
28. apex-user-manual
29. apex-zaimella-gestion-proyectos
30. oracle-data-change-governance-final

---

**For detailed information about each skill, see the individual SKILL.md files in this directory.**
