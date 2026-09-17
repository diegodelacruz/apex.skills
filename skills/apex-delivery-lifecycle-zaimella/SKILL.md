---
name: apex-delivery-lifecycle-zaimella
description: Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle for comprehensive project governance
category: Apex Delivery & Lifecycle
order: 3.5
tags:
  - orchestration
  - delivery-lifecycle
  - methodology
  - gpz
  - zaimella
  - governance
  - project-management
access_level: read-write
cost: medium
created: 2026-09-17
status: development
---

# apex-delivery-lifecycle-zaimella

**Coordinator Orchestrator:** Integrate GPZ (Zaimella) methodology with APEX delivery lifecycle.

Combine comprehensive project governance (Zaimella GPZ) with technical APEX delivery workflows for enterprises requiring both methodological rigor and technical excellence.

## Overview

Execute APEX projects under GPZ (Zaimella) methodology:
- **GPZ Setup** - Establish project governance framework
- **APEX Delivery** - Execute technical workflow (lifecycle-complete)
- **GPZ Close-out** - Complete project with methodology compliance
- **Full Audit Trail** - Git-backed audit trail + GPZ governance records

## Architecture

```
┌─────────────────────────────────────────────────┐
│ apex-delivery-lifecycle-zaimella (Orchestrator) │
│                                                  │
│ ┌──────────────────────────────────────────┐   │
│ │ Phase 1: GPZ Project Setup               │   │
│ │ Delegate to: apex-zaimella-gestion-...   │   │
│ │ - Initialize project governance          │   │
│ │ - Define stakeholders & roles            │   │
│ │ - Establish review gates                 │   │
│ └──────────────────────────────────────────┘   │
│                      ↓                          │
│ ┌──────────────────────────────────────────┐   │
│ │ Phase 2: APEX Delivery Lifecycle         │   │
│ │ Delegate to: apex-delivery-lifecycle-... │   │
│ │ - Initialize bootstrap                   │   │
│ │ - Pattern mining & analysis              │   │
│ │ - Solution design                        │   │
│ │ - Data governance                        │   │
│ │ - Engineering & implementation           │   │
│ │ - QA & validation                        │   │
│ │ - User documentation                     │   │
│ └──────────────────────────────────────────┘   │
│                      ↓                          │
│ ┌──────────────────────────────────────────┐   │
│ │ Phase 3: GPZ Project Close-Out           │   │
│ │ Delegate to: apex-zaimella-gestion-...   │   │
│ │ - Capture project learnings              │   │
│ │ - Update methodology artifacts           │   │
│ │ - Archive project in GPZ portal          │   │
│ └──────────────────────────────────────────┘   │
│                      ↓                          │
│ ┌──────────────────────────────────────────┐   │
│ │ Outputs:                                  │   │
│ │ - APEX application (deployed)            │   │
│ │ - GPZ project completed                  │   │
│ │ - Audit trail (Git + GPZ)                │   │
│ │ - Lessons learned documented             │   │
│ └──────────────────────────────────────────┘   │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Capabilities

### GPZ-Governed APEX Delivery

```python
# Initialize orchestrator with GPZ context
orchestrator = ApexZaimellOrchestrator(
    project_name='ENTERPRISE_APP',
    gpz_project_id='GPZ-2026-09',
    methodology='gpz'  # GPZ governance
)

# Phase 1: Setup GPZ project
orchestrator.setup_gpz_project(
    stakeholders=['project_manager', 'technical_lead', 'business_owner'],
    review_gates=['design', 'implementation', 'qa']
)

# Phase 2: Execute APEX workflow (under GPZ governance)
result = orchestrator.execute_apex_lifecycle(
    config={
        'forms': ['EMPLOYEES', 'DEPARTMENTS'],
        'reports': ['SUMMARY'],
        'target_env': 'test'
    }
)

# Phase 3: Close out GPZ project
orchestrator.close_gpz_project(
    learnings=['pattern_1', 'pattern_2'],
    recommendations=['improve_qa', 'automate_testing']
)

# Get combined audit trail (Git + GPZ)
audit = orchestrator.get_combined_audit_trail()
```

## Workflow

### Phase 1: GPZ Project Setup

Delegate to `apex-zaimella-gestion-proyectos`:

```
1. Initialize GPZ project in Zaimella portal
   - Project ID: auto-generated
   - Methodology: GPZ
   - Stakeholders: assigned

2. Define governance framework
   - Review gates
   - Approval authorities
   - Risk categories

3. Establish communication plan
   - Escalation paths
   - Status reporting cadence
   - Decision records
```

### Phase 2: APEX Delivery Lifecycle

Delegate to `apex-delivery-lifecycle-complete`:

```
Phase 2.1: Initialize
  → apex-project-bootstrap-final (workspace setup)

Phase 2.2: Analysis
  → apex-pattern-mining-safe (learn from patterns)

Phase 2.3: Design
  → apex-solution-design (approved by GPZ gate)

Phase 2.4: Data Governance
  → oracle-data-change-governance-final (GPZ oversight)

Phase 2.5: Implementation
  → apex-engineering-safe (under GPZ scope)

Phase 2.6: QA & Testing
  → apex-export-qa-safe (GPZ sign-off)

Phase 2.7: Documentation
  → apex-user-manual (GPZ approval)
```

**Key:** All APEX phases execute under GPZ governance gates.

### Phase 3: GPZ Project Close-Out

Delegate to `apex-zaimella-gestion-proyectos`:

```
1. Capture lessons learned
   - What worked well
   - What needs improvement
   - Patterns for reuse

2. Update methodology artifacts
   - Capture patterns in repository
   - Update templates
   - Document deviations

3. Archive project
   - Close in Zaimella portal
   - Archive decision records
   - Update portfolio

4. Final audit trail review
   - Validate Git history
   - Validate GPZ records
   - Ensure compliance
```

## Integration Points

| Component | Integrates With | Purpose |
|-----------|-----------------|---------|
| **Phase 1** | `apex-zaimella-gestion-proyectos` | GPZ project initialization |
| **Phase 2** | `apex-delivery-lifecycle-complete` | APEX technical workflow |
| **Phase 3** | `apex-zaimella-gestion-proyectos` | GPZ close-out |
| **Governance** | `oracle-data-change-governance-final` | All DATA changes reviewed by GPZ |
| **Audit Trail** | Git (.bitacora.json) + GPZ portal | Combined audit trail |

## Features

### Governance

- **Methodological rigor** - GPZ gates at each phase
- **Stakeholder alignment** - Role-based approvals
- **Decision tracking** - All decisions recorded
- **Risk management** - Risk categories and escalation

### Audit Trail

- **Git-backed** - Immutable .bitacora.json
- **GPZ records** - Methodology-level audit
- **Combined reports** - Technical + methodological view
- **Compliance ready** - Full traceability

### Scalability

- **Reusable patterns** - Lessons learned captured
- **Template governance** - Consistent APEX delivery
- **Enterprise ready** - Multi-team coordination

## Configuration

Example GPZ-governed project:

```yaml
project:
  name: EMPLOYEE_MANAGEMENT_SYSTEM
  gpz_id: GPZ-2026-09
  methodology: gpz

gpz_governance:
  stakeholders:
    - role: project_manager
      name: "John Smith"
    - role: technical_lead
      name: "Jane Doe"
    - role: business_owner
      name: "Robert Johnson"

  review_gates:
    - phase: design
      authority: technical_lead
      sign_off_required: true
    - phase: implementation
      authority: project_manager
      sign_off_required: true
    - phase: qa
      authority: business_owner
      sign_off_required: true

  risk_categories:
    - data_integrity
    - performance
    - security
    - compliance

apex_delivery:
  forms: [EMPLOYEES, DEPARTMENTS, SALARIES]
  reports: [SUMMARY, DETAILED]
  target_env: production

  data_changes:
    governance: oracle-data-change-governance-final
    approver: technical_lead
```

## Error Handling

- **GPZ gate failures** → Stop, escalate to GPZ authority
- **APEX phase failures** → Escalate to project manager
- **Data governance failures** → Escalate to compliance authority
- **Rollback capability** → Full rollback to last approved gate

## Logging

Complete audit trail:

```
2026-09-17 10:00:00 - GPZ_PROJECT_SETUP - Project initialized (GPZ-2026-09)
2026-09-17 10:05:00 - STAKEHOLDERS_ASSIGNED - 3 stakeholders registered
2026-09-17 10:10:00 - REVIEW_GATES_DEFINED - Design, Implementation, QA gates
2026-09-17 10:15:00 - APEX_LIFECYCLE_START - Phase 2 begins
2026-09-17 10:20:00 - PHASE_BOOTSTRAP_COMPLETE - Workspace ready
2026-09-17 10:25:00 - PHASE_DESIGN_START - Solution design phase
2026-09-17 11:00:00 - DESIGN_GATE_REVIEW - Awaiting technical_lead approval
2026-09-17 11:30:00 - DESIGN_GATE_APPROVED - Technical lead approves
... (continues through all phases)
2026-09-17 14:00:00 - APEX_LIFECYCLE_COMPLETE - All APEX phases done
2026-09-17 14:05:00 - GPZ_CLOSEOUT_START - Phase 3 begins
2026-09-17 14:30:00 - LEARNINGS_CAPTURED - 5 patterns documented
2026-09-17 14:35:00 - GPZ_PROJECT_ARCHIVED - Project closed in Zaimella portal
```

## Performance

Typical timeline (with GPZ governance gates):

| Phase | Duration | Gate Time |
|-------|----------|-----------|
| GPZ Setup | 2-4 hours | 1 hour |
| APEX Delivery | 2-4 weeks | 3-5 days (design + QA) |
| GPZ Close-out | 2-4 hours | 1 hour |
| **Total** | **2-4 weeks** | **4-6 days** |

*Gate time includes stakeholder reviews and approvals.*

## Status

🚧 **Development** - Zaimella integration orchestrator (15% complete)

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
**Upstream Skills:**
- `apex-zaimella-gestion-proyectos` (methodology)
- `apex-delivery-lifecycle-complete` (APEX workflow)
- `oracle-data-change-governance-final` (data governance)
