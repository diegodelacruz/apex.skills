---
name: apex-application-generator-complete
description: Development prototype for an end-to-end APEX application workflow; its API deployment phase is non-operational
category: Apex Application Development
order: 23
tags:
  - application-generation
  - orchestration
  - end-to-end
  - automation
  - deployment
  - testing
  - migration
access_level: read-write
cost: high
created: 2026-09-17
status: active
---

# apex-application-generator-complete

> **Desarrollo; no es un flujo operativo de despliegue.** La descripción y los
> ejemplos de orquestación de este archivo son un diseño/prototipo; la fase de
> despliegue usa el antiguo `apex-api-client-safe` y no está disponible como
> integración operativa. Para importar artefactos APEX, sigue la ruta
> autenticada y nativa documentada en
> `docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md` y
> `apex-page-automation-safe`. No informes que este pipeline completo se ejecutó.

## Environment and execution policy

Use the credential configured for the named environment. Effective Oracle/APEX
privileges granted to that account by the DBA/APEX administrator determine
available operations; do not hardcode a permission matrix or user identity.
Verify the connected account and actual destination with read-only checks when
available. Preserve the single global confirmation for live mutations,
including the explicit backup choice; do not add further approvals or ask the
user to run work the agent can perform.

Development prototype describing how code generation, data migration, testing, and APEX import could be coordinated. The full pipeline is not executable as documented.

## Overview

Describe a possible APEX application workflow; this prototype is not an
end-to-end executor, and its data-migration phase cannot load or restore Oracle
data. The migration skill provides mapping/validation helpers only.
- Generate application code (forms, reports, validations)
- Define database schema and data mappings
- Describe an APEX import phase; use the configured native route separately
- Execute automated tests
- Describe data-migration mapping and validation; live Oracle migration is not implemented
- Track changes and verify integrity

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  ApplicationGenerationOrchestrator (HITO 5)            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. Code Generation Phase (HITO 1)               │  │
│  │    - ApexFormGenerator                          │  │
│  │    - ApexReportGenerator                        │  │
│  │    - ApexValidationGenerator                    │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 2. Schema & Data Phase (HITO 4)                 │  │
│  │    - SchemaMappingGenerator                     │  │
│  │    - DataValidator                              │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 3. Native APEX import (separate operation)      │  │
│  │    - Not executed by this prototype             │  │
│  │    - Use the configured native APEX route       │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 4. Testing Phase (HITO 3)                       │  │
│  │    - SeleniumTestGenerator                      │  │
│  │    - PerformanceTestGenerator                   │  │
│  │    - RegressionTestValidator                    │  │
│  └──────────────────────────────────────────────────┘  │
│                      ↓                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 5. Verification & Reporting                     │  │
│  │    - ChangeTracker                              │  │
│  │    - Audit Trail                                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Capabilities

### ApplicationGenerationOrchestrator

Master orchestrator coordinating entire pipeline:

```python
from apex_application_generator import ApplicationGenerationOrchestrator

orchestrator = ApplicationGenerationOrchestrator(
    project_name='EMPLOYEE_SYSTEM',
    apex_instance='https://apex.example.com',
    source_schema='SOURCE_DB',
    target_schema='TARGET_DB'
)

# Execute full pipeline
result = orchestrator.execute_full_generation(
    config={
        'forms': ['EMPLOYEES', 'DEPARTMENTS'],
        'reports': ['EMPLOYEE_SUMMARY'],
        'target_env': 'test'
    }
)

# Get status
status = orchestrator.get_pipeline_status()
print(status)  # {'phase': 'testing', 'progress': 75%, 'estimated_time': '5m'}
```

## Pipeline Phases

### Phase 1: Code Generation

Generate APEX application code:
```python
orchestrator.generate_code(
    tables=['EMPLOYEES', 'DEPARTMENTS'],
    form_config={'EMPLOYEES': {'readonly': ['EMP_ID']}},
    report_config={'EMPLOYEE_SUMMARY': {'group_by': 'DEPT_ID'}}
)
```

### Phase 2: Schema & Data

Define data mappings and validation:
```python
orchestrator.configure_data_migration(
    mappings={'OLD_EMP': 'EMPLOYEES'},
    validation_rules={
        'EMPLOYEES': ['NOT NULL: EMP_ID', 'RANGE: SALARY 0-1000000']
    }
)
```

### Phase 3: APEX import (separate configured operation)

This prototype does not perform deployment. Use `apex-page-automation-safe` and
the configured native APEX route when component import is requested. The
following call is historical prototype pseudocode, not an operational API:
```python
orchestrator.deploy_to_environment(
    target_env='test',
    create_rollback=True  # historical pseudocode; not a database backup/rollback
)
```

### Phase 4: Testing

Execute automated tests:
```python
orchestrator.execute_tests(
    test_types=['ui', 'performance', 'regression']
)
```

### Phase 5: Verification

Verify and generate reports:
```python
report = orchestrator.generate_completion_report()
```

## Integration Points

Integrates all previous HITOs:

| HITO | Skill | Usage |
|------|-------|-------|
| 1 | apex-code-generation-safe | Generate forms, reports, validations |
| 2 | `apex-page-automation-safe` and configured APEX import route | Import artifacts when the requested environment exposes that capability; this prototype does not deploy them itself |
| 3 | apex-automated-testing-safe | Execute UI and performance tests |
| 4 | apex-data-migration-safe | Mapping and validation prototype; no live Oracle migration |
| 0 | Foundation | Credential management, path setup |

## Features

### Proposed orchestration behavior (prototype only)

- **Pipeline coordination** - Describes a possible sequence; full execution is not implemented
- **Error handling** - Prototype status reporting; no automatic database recovery
- **Progress tracking** - Simulated phase status
- **Estimated completion** - Prototype estimates, not live operation timings

### Proposed validation (not live environment checks)

- **Pre-flight checks** - Describe prerequisites; no complete live pipeline preflight
- **Schema validation** - Not performed against an Oracle environment by this generator
- **Credential validation** - No APEX connectivity test in the application-generation prototype
- **Data validation** - Prototype mapping/validation helpers only

### Reporting

- **Execution report** - Detailed pipeline log
- **Performance metrics** - Timing and resource usage
- **Test results** - Coverage and pass rates
- **Change audit** - Pipeline log available for this run; not a persisted complete audit trail

### Recovery

- **Recovery** - Requires a separately available operational recovery route; this prototype creates no savepoints or backups
- **Error recovery** - No automatic retry or data restore is implemented
- **Transaction safety** - Not guaranteed by this non-operational prototype
- **Data integrity** - No live Oracle checksum verification is implemented

## Configuration

Pipeline configuration example:

```yaml
project:
  name: EMPLOYEE_SYSTEM
  apex_url: https://apex.example.com

phases:
  code_generation:
    enabled: true
    tables: [EMPLOYEES, DEPARTMENTS]

  data_migration:
    enabled: true
    mappings:
      OLD_SCHEMA.EMP: TARGET_SCHEMA.EMPLOYEES

  deployment:
    enabled: true
    target_envs: [test, prod]

  testing:
    enabled: true
    test_types: [ui, performance, regression]
```

## Error Handling

Comprehensive error recovery:

- Validation failures → Stop before deployment
- Deployment errors → Report actual import-route result; no automatic rollback is implemented here
- Test failures → Detailed error reports
- Migration errors → Report validation/helper results; no Oracle data rollback is implemented here

## Logging

Illustrative in-memory operation log for the current run (not the persistent
audit log from controlled Oracle/APEX adapters):

```
2026-09-17 10:00:00 - PHASE_START - CodeGeneration
2026-09-17 10:00:05 - GENERATE_FORM - EMPLOYEES - SUCCESS
2026-09-17 10:00:10 - PHASE_COMPLETE - CodeGeneration (5s)
2026-09-17 10:00:15 - PHASE_START - DataMigration
2026-09-17 10:01:00 - PHASE_COMPLETE - DataMigration (45s)
...
```

## Performance

Typical end-to-end times:

| Phase | Duration (1M rows) |
|-------|-------------------|
| Code Generation | 5-10s |
| Data Migration | 30-60s |
| Deployment | 10-30s |
| Testing | 60-120s |
| **Total** | **2-4 minutes** |

## Status

**Development prototype; not an operational end-to-end deployment pipeline.**

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
