# 📊 APEX Skills Inventory Report
**As of 2026-10-02** | Created by Diego de La Cruz Sandoval

---

## Executive Summary

**Total: 31 skills** across the apex.skills repository:
- **22 active specialist skills** — Ready for production use
- **7 workflow orchestrators** — Coordinate multi-step flows
- **1 maestro coordinator** — Routes requests to appropriate specialist
- **1 retired skill** — Historical compatibility only (apex-api-client-safe)

### Distribution by Status
| Status | Count | Purpose |
|--------|-------|---------|
| **Active** | 22 | Production-ready skills |
| **Development** | 7 | Prototypes and outlines |
| **Retired** | 1 | Compatibility/historical |

---

## 🟢 Active Skills (22) — Production Ready

### Audit & Decisions
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-audit-decisions-log** | 0 | Review and export project decisions and Git-backed audit trail |

### Database & Infrastructure
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-database-diagnostics** | 1 | Diagnose Oracle/APEX requests in user-selected environment |
| **apex-schema-automation-safe** | 20 | Create, modify, drop Oracle database objects via authenticated routes |

### Delivery & Lifecycle
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-delivery-lifecycle-complete** | 2 | Run complete APEX lifecycle with environment & DATA governance |
| **apex-delivery-lifecycle-safe** | 3 | Coordinate safe APEX workflow: design → QA → documentation |

### Environment & Alignment
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-environment-alignment-complete** | 5 | Validate and align TEST vs production APEX environments safely |

### Quality Assurance
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-export-qa-safe** | 6 | Validate APEX export ZIP structure and readiness |

### Governance & Pages
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-page-range-governance** | 7 | Reserve and validate conflict-free APEX page ranges by project |

### Pattern & Design Analysis
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-pattern-mining-safe** | 8 | Extract reusable APEX design patterns from application exports |
| **apex-solution-design** | 11 | Design APEX applications and pages from approved business requirements |
| **apex-blueprint-design-safe** | 15 | Create reviewable APEX blueprints from user requirements |
| **apex-ui-craft-safe** | 17 | Assess and improve accessible, responsive APEX UX |

### Engineering & Implementation
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-engineering-safe** | 4 | Inspect, design, implement APEX applications from exports |
| **apex-page-automation-safe** | 19 | Create, modify, deploy APEX pages via native export/import |

### Project Management
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-project-bootstrap-final** | 9 | Initialize APEX project with workspace and governance foundations |
| **apex-project-workspace** | 10 | Create and maintain control-proyecto project workspace |

### Documentation
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-user-manual** | 12 | Generate and verify Word user manuals from APEX QA evidence |

### Data Governance
| Skill | Order | Description |
|-------|-------|-------------|
| **oracle-data-change-governance-final** | 13 | Govern DATA changes with decisions, rollback, validation, audit |

### Integration & REST
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-rest-source-catalogs-safe** | 16 | Assess Fusion REST catalogs for safe APEX integration design |

### Learning & Context
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-external-context-learn** | 3.5 | Learn from external repos without cloning; create reusable context |

### Methodology
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-zaimella-gestion-proyectos** | 18 | Asesor metodológico para gestión integral de proyectos GPZ/Zaimella |

---

## 🔶 Development Skills (7) — Prototypes & Outlines

These skills are functional but incomplete or in active development:

| Skill | Order | Category | Status | Purpose |
|-------|-------|----------|--------|---------|
| **apex-delivery-lifecycle-zaimella** | 3.5 | Apex Delivery & Lifecycle | development | Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle |
| **apex-data-orchestrator-safe** | 13.5 | Apex Data Integration | development | Schema and data migration workflows (APEX artifact import separate) |
| **apex-application-generator-complete** | 23 | Apex Application Development | development | End-to-end APEX application workflow; API deployment phase non-operational |
| **apex-code-generation-safe** | 24 | Apex Engineering & Design | development | Generate APEX components automatically from schema and metadata |
| **apex-automated-testing-safe** | 21 | Apex Testing & QA | development | Selenium test generation, performance testing, regression validation |
| **apex-data-migration-safe** | 25 | Apex Data Integration | development | Schema mapping, data validation, ETL pipeline, rollback management |

---

## ⚫ Orchestrator Skills (5+1 Maestro)

### Maestro Coordinator
| Skill | Order | Description |
|-------|-------|-------------|
| **apex** | 14 | Main entry point; routes requests to the smallest useful specialist workflow |

### Workflow Orchestrators
| Skill | Order | Description |
|-------|-------|-------------|
| **apex-qa-orchestrator-safe** | 6.5 | Coordinate APEX QA evidence and report results without approval gates |
| **apex-design-review-orchestrator** | 11.5 | Coordinate solution, blueprint, engineering review without execution gates |

**Development Orchestrators:**
- **apex-delivery-lifecycle-zaimella** (3.5) — Integrate Zaimella with delivery lifecycle
- **apex-data-orchestrator-safe** (13.5) — Schema and data migration workflows
- **apex-application-generator-complete** (23) — End-to-end application generation

---

## 🔴 Retired Skills (1) — Historical Reference Only

| Skill | Order | Status | Note |
|-------|-------|--------|------|
| **apex-api-client-safe** | 22 | retired | Simulated REST adapter; **must NOT be used for Oracle APEX deployment** |

Retained for invocation compatibility and historical context. No active capability.

---

## Organization by Workflow Type

### Orchestration & Coordination
- apex (maestro)
- apex-delivery-lifecycle-complete
- apex-delivery-lifecycle-safe
- apex-delivery-lifecycle-zaimella (dev)
- apex-application-generator-complete (dev)
- apex-data-orchestrator-safe (dev)
- apex-qa-orchestrator-safe
- apex-design-review-orchestrator

### Design & Planning
- apex-solution-design
- apex-blueprint-design-safe
- apex-pattern-mining-safe
- apex-ui-craft-safe

### Engineering & Implementation
- apex-engineering-safe
- apex-page-automation-safe
- apex-code-generation-safe (dev)
- apex-schema-automation-safe

### Quality & Validation
- apex-export-qa-safe
- apex-automated-testing-safe (dev)
- apex-environment-alignment-complete

### Data Integration
- apex-data-migration-safe (dev)
- oracle-data-change-governance-final

### Governance & Audit
- apex-page-range-governance
- oracle-data-change-governance-final
- apex-audit-decisions-log

### Project Management
- apex-project-bootstrap-final
- apex-project-workspace
- apex-zaimella-gestion-proyectos

### External Context & Learning
- apex-external-context-learn

### Documentation
- apex-user-manual

### Diagnostics
- apex-database-diagnostics

### Integration
- apex-rest-source-catalogs-safe

---

## Access Levels

### Read-Only Skills (7 active)
Skills that do NOT modify APEX or database objects:
- apex-engineering-safe
- apex-export-qa-safe
- apex-pattern-mining-safe
- apex-rest-source-catalogs-safe
- apex-ui-craft-safe
- apex-database-diagnostics
- apex-audit-decisions-log

### Read-Write Skills (15 active)
Skills that can modify or create APEX objects and database artifacts:
- apex-solution-design
- apex-page-automation-safe
- apex-page-range-governance
- apex-project-bootstrap-final
- apex-project-workspace
- apex-user-manual
- apex-delivery-lifecycle-safe
- apex-delivery-lifecycle-complete
- apex-environment-alignment-complete
- oracle-data-change-governance-final
- apex-zaimella-gestion-proyectos
- apex-external-context-learn
- apex-schema-automation-safe

---

## Cost Profile by Complexity

### Free (Read-Only)
- apex-export-qa-safe
- apex-pattern-mining-safe
- apex-rest-source-catalogs-safe
- apex-ui-craft-safe

### Free (On-Demand)
- apex-audit-decisions-log (automatic capture, tokens only on view)

### Low Complexity
- apex-solution-design
- apex-page-range-governance
- apex-environment-alignment-complete

### Medium Complexity
- apex-project-bootstrap-final
- apex-project-workspace
- apex-user-manual
- apex-zaimella-gestion-proyectos

### High Complexity (Full Workflow)
- apex-delivery-lifecycle-safe
- apex-delivery-lifecycle-complete
- apex-delivery-lifecycle-zaimella (dev)
- apex-page-automation-safe
- apex-schema-automation-safe
- apex-application-generator-complete (dev)
- apex-data-orchestrator-safe (dev)
- apex-qa-orchestrator-safe
- apex-design-review-orchestrator
- oracle-data-change-governance-final
- apex-code-generation-safe (dev)
- apex-automated-testing-safe (dev)
- apex-data-migration-safe (dev)

---

## Quick Decision Guide

| You want to… | Use skill… |
|---|---|
| Inspect existing APEX app | apex-engineering-safe |
| Design new APEX app | apex-solution-design |
| Create reviewable blueprint first | apex-blueprint-design-safe |
| Create/modify APEX pages with full control | apex-page-automation-safe |
| Create/modify database objects | apex-schema-automation-safe |
| Learn patterns from exports | apex-pattern-mining-safe |
| Assess Fusion REST source | apex-rest-source-catalogs-safe |
| Review UX/responsive/accessibility | apex-ui-craft-safe |
| Check if export is ready | apex-export-qa-safe |
| Compare TEST vs Production | apex-environment-alignment-complete |
| Reserve pages for my project | apex-page-range-governance |
| Run complete delivery workflow | apex-delivery-lifecycle-safe |
| Fix database errors | apex-database-diagnostics |
| Generate user documentation | apex-user-manual |
| See all decisions & audit trail | apex-audit-decisions-log |
| Start new project | apex-project-bootstrap-final |
| Organize project workspace | apex-project-workspace |
| Manage Zaimella project methodology | apex-zaimella-gestion-proyectos |
| Handle DATA changes | oracle-data-change-governance-final |
| Ask about anything APEX-related | apex (Coordinator) |

---

## Key Insights

### Strengths of the Current Portfolio
1. **Complete lifecycle coverage** — From design through delivery and documentation
2. **Three-level orchestration hierarchy** — Maestro → Coordinators → Specialists provides intelligent routing
3. **Safety-first design** — 7 read-only skills for low-risk inspection and analysis
4. **Clear access control** — 15 read-write vs 7 read-only active skills
5. **Bilingual support** — Spanish/English documentation (Zaimella methodology)
6. **Governance built-in** — Audit trail, environment alignment, page ranges, DATA changes
7. **Well-organized catalog** — Clear order numbers, consistent naming, comprehensive tagging

### Development Opportunities
1. **7 skills in prototype phase** — Particularly around:
   - Application generation (order 23)
   - Code generation (order 24)
   - Data migration (order 25)
   - Automated testing (order 21)

2. **API deployment gap** — apex-application-generator-complete has non-operational API deployment phase

3. **Documentation precision** — All skills well-documented in SKILL.md files with metadata

---

## Repository Metrics

- **Total skills:** 31
- **Active skills:** 22 (71%)
- **Development skills:** 7 (23%)
- **Retired skills:** 1 (3%)
- **Orchestrators:** 5 active + 1 dev + 1 maestro = 7 total
- **Read-only skills:** 7 of 22 active (32%)
- **Read-write skills:** 15 of 22 active (68%)

---

## How to Use This Inventory

1. **Start with the maestro coordinator:** `/apex` understands your request and routes to the right skill
2. **Use quick decision guide** above when you know what you want to do
3. **Filter by access level** — Read-only skills are safe for exploration
4. **Filter by workflow** — See organization by workflow type section
5. **Check skill metadata** — Read individual SKILL.md files for full capability details
6. **Explore by order number** — Sequential ordering supports logical skill discovery

---

## Related Documentation

- **Master Catalog:** `skills/README.md` — Complete navigation and descriptions
- **Quick Reference:** `skills/SKILLS-QUICK-REFERENCE.md` — One-line purpose lookup
- **Individual Skills:** Each skill folder contains detailed SKILL.md with workflow, examples, and configuration
- **Audit Trail:** Run `/apex-audit-decisions-log` to review all project decisions
- **Project Instructions:** See `CLAUDE.md` for framework policies and behavioral rules

---

**Generated:** 2026-10-02
**Repository:** apex.skills
**Inventory Version:** 1.0 (Complete Catalog)
**Skills Status:** 22 active + 7 development + 1 retired = 31 total
