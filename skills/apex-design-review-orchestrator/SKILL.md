---
name: apex-design-review-orchestrator
description: Orchestrate design review workflow - solution design, blueprint creation, engineering review
category: Apex Engineering & Design
order: 11.5
tags:
  - orchestration
  - design
  - review
  - architecture
  - approval
  - governance
access_level: read-write
cost: medium
created: 2026-09-17
status: development
---

# apex-design-review-orchestrator

**Sub-Coordinator Orchestrator:** Coordinate design review - solution → blueprint → engineering.

Ensure rigorous design governance from high-level solution through detailed blueprints to engineering review, with explicit approval gates at each phase before implementation.

## Overview

Execute design review process systematically:
- **Solution Design** - High-level application architecture and requirements
- **Blueprint Design** - Detailed component specifications and scaffolding
- **Engineering Review** - Implementation readiness assessment
- **Approval Gates** - Sign-off required before proceeding to implementation
- **Design Documentation** - Complete design artifacts for future reference

## Architecture

```
┌────────────────────────────────────────────────────┐
│ apex-design-review-orchestrator (Sub-Coordinator) │
│                                                     │
│ ┌──────────────────────────────────────────────┐  │
│ │ Phase 1: Solution Design                     │  │
│ │ Delegate to: apex-solution-design            │  │
│ │ - Gather business requirements              │  │
│ │ - Define high-level architecture            │  │
│ │ - Identify data structures                  │  │
│ │ - Plan integrations                         │  │
│ │ - Document assumptions                      │  │
│ │ - Create solution proposal                  │  │
│ └──────────────────────────────────────────────┘  │
│      GATE: Solution approved by stakeholders ✓    │
│                      ↓                             │
│ ┌──────────────────────────────────────────────┐  │
│ │ Phase 2: Blueprint Design                    │  │
│ │ Delegate to: apex-blueprint-design-safe      │  │
│ │ - Create page wireframes                    │  │
│ │ - Define form/report structures             │  │
│ │ - Specify validation rules                  │  │
│ │ - Design data bindings                      │  │
│ │ - Plan component relationships              │  │
│ │ - Create implementation scaffolding         │  │
│ └──────────────────────────────────────────────┘  │
│      GATE: Blueprint reviewed & approved ✓        │
│                      ↓                             │
│ ┌──────────────────────────────────────────────┐  │
│ │ Phase 3: Engineering Review                  │  │
│ │ Delegate to: apex-engineering-safe           │  │
│ │ - Assess implementation feasibility         │  │
│ │ - Review technical architecture             │  │
│ │ - Validate against APEX best practices      │  │
│ │ - Identify technical risks                  │  │
│ │ - Recommend optimizations                   │  │
│ │ - Generate engineering sign-off             │  │
│ └──────────────────────────────────────────────┘  │
│      GATE: Engineering approved ✓                 │
│                      ↓                             │
│ ┌──────────────────────────────────────────────┐  │
│ │ Outputs:                                      │  │
│ │ - Solution design approved                  │  │
│ │ - Blueprints approved                       │  │
│ │ - Engineering sign-off                      │  │
│ │ - READY FOR IMPLEMENTATION ✓                │  │
│ │ - Design documentation complete             │  │
│ └──────────────────────────────────────────────┘  │
│                                                     │
└────────────────────────────────────────────────────┘
```

## Capabilities

### Rigorous Design Governance

```python
# Initialize orchestrator
design_orchestrator = DesignReviewOrchestrator(
    project_name='EMPLOYEE_MANAGEMENT_SYSTEM'
)

# Phase 1: Solution Design
solution = design_orchestrator.execute_solution_design(
    business_requirements=[
        'Manage employee records',
        'Track department hierarchies',
        'Generate salary reports'
    ],
    stakeholders=['business_owner', 'it_director'],
    patterns=['employee_hierarchy', 'audit_trail']
)
# Result: {'status': 'in_review', 'solution_doc': '...'}

# GATE: Require stakeholder approval
solution_approval = design_orchestrator.gate_solution_approval(
    approvers=['business_owner', 'it_director'],
    threshold=2  # Require 2/2 approvals
)
if not solution_approval['approved']:
    raise Exception("Solution not approved - revisions needed")

# Phase 2: Blueprint Design
blueprints = design_orchestrator.execute_blueprint_design(
    solution_ref=solution,
    components=[
        'employee_form',
        'department_form',
        'salary_report'
    ]
)
# Result: {'status': 'reviewed', 'blueprints': [...]}

# GATE: Require blueprint review
blueprint_approval = design_orchestrator.gate_blueprint_approval(
    reviewers=['technical_lead', 'solutions_architect'],
    threshold=2  # Require 2/2 reviews
)
if not blueprint_approval['approved']:
    raise Exception("Blueprints rejected - revisions needed")

# Phase 3: Engineering Review
engineering = design_orchestrator.execute_engineering_review(
    blueprints=blueprints,
    checklist=[
        'feasibility',
        'best_practices',
        'performance',
        'security'
    ]
)
# Result: {'status': 'approved', 'risks': [], 'recommendations': [...]}

# GATE: Require engineering sign-off
engineering_approval = design_orchestrator.gate_engineering_approval(
    approvers=['principal_engineer'],
    threshold=1
)
if not engineering_approval['approved']:
    raise Exception("Engineering concerns - address risks first")

# Get complete design documentation
design_doc = design_orchestrator.generate_design_documentation()
print(f"Design Status: {design_doc['approval_status']}")  # APPROVED
print(f"Ready for Implementation: {design_doc['implementation_ready']}")  # True
```

## Workflow

### Phase 1: Solution Design

Delegate to `apex-solution-design`:

```
1. Gather requirements:
   - Business requirements review
   - Stakeholder interviews
   - Scope definition
   - Success criteria

2. Define architecture:
   - High-level application structure
   - Page organization
   - Data flow diagrams
   - Integration points

3. Plan data structures:
   - Entity definitions
   - Relationship diagrams
   - Key identifiers
   - Derived data

4. Identify integrations:
   - External systems
   - REST/SOAP endpoints
   - Data synchronization
   - Third-party services

5. Document solution:
   - Executive summary
   - Architecture diagrams
   - Requirements traceability
   - Assumptions and constraints

6. Create proposal:
   - Solution overview
   - Benefits
   - Resource estimates
   - Timeline estimate
```

**Gate:** Require explicit stakeholder approval (e.g., business owner, IT director) before proceeding to blueprints.

### Phase 2: Blueprint Design

Delegate to `apex-blueprint-design-safe`:

```
1. Create page wireframes:
   - Page hierarchy
   - Layout sketches
   - Navigation flow
   - Region placement

2. Define component structures:
   - Form fields and types
   - Report columns and grouping
   - Validation rules per field
   - Default values

3. Specify bindings:
   - Form-to-table bindings
   - Report source queries
   - Parameter bindings
   - Dynamic control references

4. Plan relationships:
   - Master-detail relationships
   - Cross-page navigation
   - Process flow sequencing
   - Conditional visibility

5. Design scaffolding:
   - Page template structure
   - Component templates
   - SQL templates
   - PL/SQL function stubs

6. Create blueprint artifacts:
   - Wireframe diagrams
   - Data binding specifications
   - SQL skeleton queries
   - Component specifications
```

**Gate:** Require technical lead and solutions architect review before proceeding to engineering review.

### Phase 3: Engineering Review

Delegate to `apex-engineering-safe`:

```
1. Assess feasibility:
   - APEX version requirements
   - Plugin dependencies
   - Database object needs
   - Performance viability

2. Review architecture:
   - Application layering
   - Naming conventions
   - Code organization
   - Module separation

3. Validate best practices:
   - APEX design patterns
   - Security patterns
   - Performance patterns
   - Accessibility patterns

4. Identify risks:
   - Performance risks
   - Security risks
   - Scalability risks
   - Maintenance risks

5. Recommend optimizations:
   - Caching strategies
   - Query optimization
   - Component reuse
   - Code generation opportunities

6. Generate sign-off:
   - Feasibility verdict
   - Risk assessment
   - Recommendations
   - Engineering approval
```

**Gate:** Require principal engineer or technical lead sign-off before design approval.

## Integration Points

| Phase | Orchestrates | Purpose |
|-------|--------------|---------|
| **Phase 1** | `apex-solution-design` | Solution architecture |
| **Phase 2** | `apex-blueprint-design-safe` | Detailed specifications |
| **Phase 3** | `apex-engineering-safe` | Implementation readiness |
| **Audit** | Git (.bitacora.json) | Design decision trail |

## Features

### Governance

- **Multi-phase review** - Solution → Blueprint → Engineering
- **Approval gates** - Explicit sign-off at each phase
- **Stakeholder involvement** - Business owner in phase 1, technical in phase 3
- **Risk assessment** - Technical risks identified early
- **Documented decisions** - Design decisions traceable

### Quality

- **Alignment** - Business requirements ↔ Technical design
- **Completeness** - All components planned before implementation
- **Best practices** - APEX patterns and guidelines enforced
- **Reusability** - Component templates for consistency

### Efficiency

- **Parallel work** - Teams can plan while design is approved
- **Clear scope** - Implementation scope defined upfront
- **Risk mitigation** - Technical risks addressed before coding
- **Less rework** - Clear specifications reduce implementation changes

## Configuration

Example design review project:

```yaml
orchestration:
  project_name: EMPLOYEE_MANAGEMENT_SYSTEM

phase_1_solution_design:
  stakeholders:
    - role: business_owner
      name: "Jane Smith"
    - role: it_director
      name: "Bob Johnson"

  requirements:
    - "Manage employee records"
    - "Track departments"
    - "Generate salary reports"

  approval_threshold: 2  # All stakeholders must approve
  review_deadline: "2026-09-20"

phase_2_blueprint_design:
  reviewers:
    - role: technical_lead
      name: "Alice Chen"
    - role: solutions_architect
      name: "David Lee"

  components:
    - name: employee_form
      type: form
      features: [create, edit, delete]
    - name: salary_report
      type: report
      features: [filter, export]

  approval_threshold: 2  # All reviewers must approve
  review_deadline: "2026-09-22"

phase_3_engineering_review:
  approvers:
    - role: principal_engineer
      name: "Charlie Wong"

  checklist:
    - feasibility
    - best_practices
    - performance
    - security
    - scalability

  approval_threshold: 1
  review_deadline: "2026-09-23"
```

## Error Handling

- **Phase 1 (Solution) rejection** → Gather feedback, revise, resubmit
- **Phase 2 (Blueprint) rejection** → Update blueprints based on feedback, resubmit
- **Phase 3 (Engineering) issues** → Identify risks, propose mitigations, get approval
- **Approval timeout** → Escalate to stakeholder management

**Process:** Do not proceed to implementation without all approvals. Require explicit sign-off, not implied acceptance.

## Logging

Complete design review trail:

```
2026-09-17 09:00:00 - DESIGN_REVIEW_START - EMPLOYEE_MANAGEMENT_SYSTEM
2026-09-17 09:05:00 - PHASE_1_START - Solution Design

2026-09-17 09:30:00 - REQUIREMENTS_GATHERED - 5 requirements documented
2026-09-17 10:00:00 - ARCHITECTURE_DEFINED - 8 pages planned
2026-09-17 10:30:00 - DATA_STRUCTURES_PLANNED - 6 entities identified
2026-09-17 11:00:00 - INTEGRATIONS_IDENTIFIED - 3 REST endpoints
2026-09-17 11:30:00 - SOLUTION_DOCUMENTED - Solution proposal complete
2026-09-17 12:00:00 - PHASE_1_COMPLETE - Solution Design: READY FOR REVIEW

2026-09-17 13:00:00 - GATE_1_REVIEW - Solutions submitted for approval
2026-09-17 14:00:00 - GATE_1_APPROVAL_1 - business_owner: APPROVED
2026-09-17 14:30:00 - GATE_1_APPROVAL_2 - it_director: APPROVED
2026-09-17 14:35:00 - GATE_1_COMPLETE - Solution approved ✓

2026-09-17 15:00:00 - PHASE_2_START - Blueprint Design

2026-09-17 15:30:00 - WIREFRAMES_CREATED - 8 pages wireframed
2026-09-17 16:00:00 - FORMS_SPECIFIED - 3 forms designed
2026-09-17 16:30:00 - REPORTS_SPECIFIED - 2 reports designed
2026-09-17 17:00:00 - BINDINGS_PLANNED - 25 data bindings
2026-09-17 17:30:00 - SCAFFOLDING_CREATED - Blueprints ready
2026-09-17 18:00:00 - PHASE_2_COMPLETE - Blueprint Design: READY FOR REVIEW

2026-09-17 18:30:00 - GATE_2_REVIEW - Blueprints submitted for review
2026-09-17 19:30:00 - GATE_2_REVIEW_1 - technical_lead: APPROVED
2026-09-17 20:00:00 - GATE_2_REVIEW_2 - solutions_architect: APPROVED
2026-09-17 20:05:00 - GATE_2_COMPLETE - Blueprints approved ✓

2026-09-17 20:30:00 - PHASE_3_START - Engineering Review

2026-09-17 21:00:00 - FEASIBILITY_ASSESSED - VIABLE
2026-09-17 21:15:00 - ARCHITECTURE_REVIEWED - SOUND
2026-09-17 21:30:00 - BEST_PRACTICES_CHECKED - COMPLIANT
2026-09-17 21:45:00 - RISKS_IDENTIFIED - 2 performance risks identified
2026-09-17 22:00:00 - OPTIMIZATIONS_RECOMMENDED - Caching strategy proposed
2026-09-17 22:15:00 - PHASE_3_COMPLETE - Engineering Review: APPROVED

2026-09-17 22:30:00 - GATE_3_REVIEW - Engineering review submitted
2026-09-17 23:00:00 - GATE_3_APPROVAL - principal_engineer: APPROVED WITH RECOMMENDATIONS
2026-09-17 23:05:00 - GATE_3_COMPLETE - Engineering approved ✓

2026-09-17 23:30:00 - DESIGN_DOCUMENTATION_GENERATED - Complete design package
2026-09-17 23:35:00 - DESIGN_REVIEW_COMPLETE - READY FOR IMPLEMENTATION ✓
```

## Performance

Typical design review timeline:

| Phase | Duration | Key Activity |
|-------|----------|---|
| Solution Design | 2-5 days | Requirements, architecture planning |
| Solution Review | 2-3 days | Stakeholder approval |
| Blueprint Design | 3-7 days | Detailed specifications |
| Blueprint Review | 2-3 days | Technical review |
| Engineering Review | 1-2 days | Feasibility assessment |
| **Total** | **10-20 days** | Full design review cycle |

*Actual timing depends on project complexity and stakeholder availability.*

## Status

🚧 **Development** - Design review orchestrator (20% complete)

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
**Upstream Skills:**
- `apex-solution-design` (solution architecture)
- `apex-blueprint-design-safe` (detailed design)
- `apex-engineering-safe` (feasibility review)
