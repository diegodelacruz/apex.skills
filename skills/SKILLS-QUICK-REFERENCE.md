# ⚡ APEX Skills Quick Reference

> **Policy update (2026-09-28):** Use the credential configured for the requested environment;
> Oracle/APEX privileges granted by the DBA determine available operations. Skills do not hardcode
> user identities or permission matrices, add approval gates, or delegate work available to the agent.

One-line descriptions for rapid lookup.

| Skill | Purpose |
|-------|---------|
| **apex-audit-decisions-log** | Review and export project decisions and the Git-backed audit trail. |
| **apex-database-diagnostics** | Diagnose Oracle and APEX requests in the user-selected environment through available authenticated routes. |
| **apex-schema-automation-safe** | Create, modify, and drop Oracle database objects through available authenticated routes. |
| **apex-delivery-lifecycle-complete** | Run the complete APEX lifecycle with environment and DATA governance. |
| **apex-delivery-lifecycle-safe** | Coordinate a safe APEX workflow from design through QA and documentation. |
| **apex-engineering-safe** | Inspect, design, and implement APEX applications from exports within the user's environment matrix. |
| **apex-environment-alignment-complete** | Validate and align TEST and production APEX environments safely. |
| **apex-export-qa-safe** | Validate APEX export ZIP structure and readiness before changes. |
| **apex-page-automation-safe** | Create, modify, and deploy APEX pages via native export/import through SQLcl. |
| **apex-page-range-governance** | Reserve and validate conflict-free APEX page ranges by project. |
| **apex-pattern-mining-safe** | Extract reusable APEX design patterns from application exports safely. |
| **apex-project-bootstrap-final** | Initialize an APEX project with workspace and governance foundations. |
| **apex-project-workspace** | Create and maintain the control-proyecto project workspace. |
| **apex-solution-design** | Design APEX applications and pages from approved business requirements. |
| **apex-blueprint-design-safe** | Create reviewable APEX blueprints from user requirements and available metadata. |
| **apex-rest-source-catalogs-safe** | Assess Fusion REST catalogs for safe APEX integration design. |
| **apex-ui-craft-safe** | Assess and improve accessible, responsive APEX UX with Universal Theme. |
| **apex-user-manual** | Generate and verify Word user manuals from approved APEX QA evidence. |
| **apex-zaimella-gestion-proyectos** (GPZ) | Asesor metodológico para gestión integral de proyectos Zaimella (RI → AD → DP → EJ → CI) |
| **apex** (Coordinator) | Main entry point: understands requests and routes to skills |
| **apex-application-generator-complete** | Development prototype for an end-to-end APEX application workflow; its API deployment phase is non-operational |
| **apex-data-orchestrator-safe** | Development outline for schema and data migration workflows; APEX artifact import is separate |
| **apex-qa-orchestrator-safe** | Coordinate APEX QA evidence and report results without approval gates. |
| **apex-design-review-orchestrator** | Coordinate APEX solution, blueprint, and engineering review without adding execution gates. |
| **apex-delivery-lifecycle-zaimella** | Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle for comprehensive project governance |
| **apex-external-context-learn** | Learn from external repositories (GitHub or local) without cloning. Create persistent, reusable reference context for APEX engineering workflows. |
| **apex-code-generation-safe** | Generate APEX components automatically from schema and metadata |
| **apex-api-client-safe** | Retired simulated REST adapter; it must not be used for Oracle APEX deployment. |
| **apex-automated-testing-safe** | Selenium test generation, performance testing, and regression validation framework |
| **apex-data-migration-safe** | Schema mapping, data validation, ETL pipeline, and rollback management framework |
| **oracle-data-change-governance-final** | Govern DATA changes with decisions, rollback, validation, and audit evidence. |

---

## 🎯 Quick Decisions

**"I want to..."** → **Use this skill:**

| Goal | Skill |
|------|-------|
| Inspect an existing APEX app | apex-engineering-safe |
| Design a new APEX app | apex-solution-design |
| Create a reviewable blueprint first | apex-blueprint-design-safe |
| Create or modify APEX pages with full control | apex-page-automation-safe |
| Create or modify database objects (tables, views, procedures) | apex-schema-automation-safe |
| Learn patterns from existing exports | apex-pattern-mining-safe |
| Assess a Fusion REST source catalog | apex-rest-source-catalogs-safe |
| Review UX or responsive/accessibility behavior | apex-ui-craft-safe |
| Check if export is ready | apex-export-qa-safe |
| Compare TEST vs Production | apex-environment-alignment-complete |
| Reserve pages for my project | apex-page-range-governance |
| Run complete delivery workflow | apex-delivery-lifecycle-safe |
| Fix DATABASE errors | apex-database-diagnostics |
| Generate user documentation | apex-user-manual |
| See all decisions and audit trail | apex-audit-decisions-log |
| Start a new project | apex-project-bootstrap-final |
| Organize project workspace | apex-project-workspace |
| Manage Zaimella project methodology (GPZ) | apex-zaimella-gestion-proyectos |
| Handle DATA changes | oracle-data-change-governance-final |
| Ask about anything APEX-related | apex (Coordinator) |
| Review the application-generation workflow prototype | apex-application-generator-complete |
| Plan schema and data migration work (APEX import is separate) | apex-data-orchestrator-safe |
| Coordinate full QA workflow (static → automated → environment) | apex-qa-orchestrator-safe |
| Coordinate design review (solution → blueprint → engineering) | apex-design-review-orchestrator |
| Generate APEX components from schema (forms, reports) | apex-code-generation-safe |
| Deploy APEX pages using native export/import and configured tools | apex-page-automation-safe |
| Run automated testing suite (Selenium, performance) | apex-automated-testing-safe |
| Execute data migration and ETL pipelines | apex-data-migration-safe |
| Run APEX delivery with Zaimella governance | apex-delivery-lifecycle-zaimella |

---

## 📊 Skills by Token Cost

| Cost | Skills |
|------|--------|
| **Free (Read-only)** | apex-export-qa-safe, apex-pattern-mining-safe, apex-rest-source-catalogs-safe, apex-ui-craft-safe |
| **Free (On-demand)** | apex-audit-decisions-log (automatic capture, tokens only on view) |
| **Low (Typical)** | apex-solution-design, apex-page-range-governance, apex-environment-alignment-complete |
| **Medium (Complex)** | apex-project-bootstrap-final, apex-project-workspace, apex-user-manual, apex-zaimella-gestion-proyectos |
| **High (Full workflow)** | apex-delivery-lifecycle-safe, apex-delivery-lifecycle-complete, apex-delivery-lifecycle-zaimella, apex-page-automation-safe, apex-schema-automation-safe, apex-application-generator-complete, apex-data-orchestrator-safe, apex-qa-orchestrator-safe, apex-design-review-orchestrator, oracle-data-change-governance-final, apex-code-generation-safe, apex-automated-testing-safe, apex-data-migration-safe |

---

**Tip:** Use `/apex` (Coordinator) to let it decide which skill to use based on your request.
