---
name: apex-data-orchestrator-safe
description: Development outline for schema and data migration workflows; APEX artifact import is separate
category: Apex Data Integration
order: 13.5
tags:
  - orchestration
  - data-integration
  - schema
  - etl
  - migration
  - automation
access_level: read-write
cost: high
created: 2026-09-17
status: active
---

# apex-data-orchestrator-safe

> **Desarrollo; el flujo integral descrito aquí no está implementado como
> orquestador operativo.** La fase antigua de REST/APEX Sync dependía de
> `apex-api-client-safe`, que está retirado. La migración de datos a Oracle y la
> importación de artefactos APEX son operaciones distintas. Para importación
> APEX usa la ruta nativa autenticada de
> `docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`/
> `apex-page-automation-safe`; no declares sincronización integral completada
> por ejecutar solo ETL.

## Environment and execution policy

Use the credential configured for the requested environment. The effective
Oracle/APEX privileges granted to that account by the DBA determine which
operations succeed; do not hardcode a user or permission matrix. Verify the
connected account and actual destination with read-only checks when available.
Follow the requested environment, do not add approvals or ask the user to
execute work available to the agent, and use another configured route for the
same environment when a channel fails. Run relevant quality checks and report
their actual outcome without turning a successful check or plan into an
approval prerequisite.

**Development workflow outline:** schema automation → validation → data migration. APEX artifact import is separate.

Outline database schema and data migration work with validation and rollback guidance; the full APEX synchronization pipeline is not implemented.

## Overview

Execute full data pipeline safely:
- **Schema Automation** - Create/modify database objects under governance
- **Data Validation** - Comprehensive data quality checks
- **ETL Migration** - Extract, transform, validate, load data
- **APEX artifact import** - Separate operation through a configured native route; not data synchronization
- **Rollback Ready** - Automatic rollback points at each phase

## Architecture

```
┌──────────────────────────────────────────────────┐
│ apex-data-orchestrator-safe (Sub-Coordinator)   │
│                                                   │
│ ┌────────────────────────────────────────────┐  │
│ │ Phase 1: Schema Automation                 │  │
│ │ Delegate to: apex-schema-automation-safe   │  │
│ │ - Create tables/views/sequences            │  │
│ │ - Modify column definitions                │  │
│ │ - Add indexes and constraints              │  │
│ │ - Under oracle-data-change-governance      │  │
│ └────────────────────────────────────────────┘  │
│                      ↓                           │
│ ┌────────────────────────────────────────────┐  │
│ │ Phase 2: Data Validation                   │  │
│ │ Execute: DataValidator from HITO 4        │  │
│ │ - Check schema readiness                   │  │
│ │ - Validate target environment              │  │
│ │ - Pre-migration health check               │  │
│ └────────────────────────────────────────────┘  │
│                      ↓                           │
│ ┌────────────────────────────────────────────┐  │
│ │ Phase 3: Data Migration (ETL)              │  │
│ │ Delegate to: apex-data-migration-safe      │  │
│ │ - Extract from source                      │  │
│ │ - Transform per mapping                    │  │
│ │ - Validate quality                         │  │
│ │ - Load to target                           │  │
│ │ - Create rollback point                    │  │
│ └────────────────────────────────────────────┘  │
│                      ↓                           │
│ ┌────────────────────────────────────────────┐  │
│ │ Phase 4: Optional APEX artifact import    │  │
│ │ Use configured native import route         │  │
│ │ - Import selected APEX artifacts           │  │
│ │ - Verify result in the requested target    │  │
│ └────────────────────────────────────────────┘  │
│                      ↓                           │
│ ┌────────────────────────────────────────────┐  │
│ │ Outputs:                                    │  │
│ │ - Schema created in target environment    │  │
│ │ - Data migrated safely                     │  │
│ │ - Optional native APEX import verified     │  │
│ │ - Rollback points created                  │  │
│ │ - Audit trail recorded                     │  │
│ └────────────────────────────────────────────┘  │
│                                                   │
└──────────────────────────────────────────────────┘
```

## Capabilities

### Proposed Data Workflow (not executable end-to-end)

```python
# Initialize orchestrator with source/target environments
orchestrator = DataOrchestrator(
    source_env='legacy_db',
    target_env='modern_apex',
    project_name='MIGRATION_2026'
)

# Phase 1: Schema automation (under governance)
orchestrator.create_schema(
    objects=[
        {'type': 'table', 'name': 'EMPLOYEES', 'columns': [...]},
        {'type': 'table', 'name': 'DEPARTMENTS', 'columns': [...]},
        {'type': 'view', 'name': 'EMP_SUMMARY', 'sql': 'SELECT ...'},
    ]
)

# Phase 2: Validation before migration
validation = orchestrator.pre_migration_validation(
    target_env='modern_apex',
    checks=['schema_readiness', 'connectivity', 'storage']
)

# Phase 3: Execute ETL migration
result = orchestrator.execute_migration(
    mappings={'OLD_EMP': 'EMPLOYEES', 'OLD_DEPT': 'DEPARTMENTS'},
    validation_rules={
        'EMPLOYEES': ['NOT NULL: EMP_ID', 'UNIQUE: EMAIL'],
        'DEPARTMENTS': ['NOT NULL: DEPT_ID']
    }
)

# Optional APEX component import is a separate operation using the configured native route.
# This prototype does not implement data or application sync to APEX.

# Get complete audit trail
audit = orchestrator.get_operation_log()
```

## Workflow

### Phase 1: Schema Automation

Delegate to `apex-schema-automation-safe`:

```
1. Resolve the owner as `DATA` unless the user explicitly names another schema. Apply the specific governance exception for backup objects, which belong in the connected user's schema. Carry the selected owner through every DDL and related DML statement; never infer it from `SESSION_USER` or `CURRENT_SCHEMA`, and never retry a non-backup operation under the connected user's schema after an owner error.

2. Apply `oracle-data-change-governance-final` guidance without a separate authorization gate:
   - Create tables
   - Create views
   - Create sequences
   - Add indexes
   - Add constraints

3. Validate schema:
   - Syntax validation
   - Object dependencies
   - Naming conventions

4. Create rollback point:
   - Save schema snapshot
   - Record DDL statements
   - Store rollback procedure
```

### Phase 2: Data Validation

Execute internal validation:

```
1. Pre-migration health check:
   - Target environment connectivity
   - Storage space verification
   - Credential validation

2. Schema readiness:
   - All objects exist
   - Constraints properly defined
   - Indexes created

3. Source data assessment:
   - Row count by table
   - NULL value distribution
   - Data type alignment
```

### Phase 3: Data Migration (ETL)

Delegate to `apex-data-migration-safe`:

```
1. Extract phase:
   - Read from source (legacy_db)
   - Batch size optimization
   - Source data logging

2. Transform phase:
   - Apply column mappings
   - Execute transformation rules
   - Handle data type conversions

3. Validate phase:
   - Run validation rules
   - Flag violations
   - Generate error report

4. Load phase:
   - Insert into target tables
   - Verify row counts
   - Create rollback savepoint

5. Verify integrity:
   - Checksum validation
   - Foreign key validation
   - Business rule checks
```

### Phase 4: APEX artifact import (separate operation)

The prototype does not synchronize data to APEX. When the user requested an
APEX component import, use `apex-page-automation-safe` and the configured
authenticated native route documented in
`docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`. Oracle data migration remains
the separate Phase 3 operation. Do not route this phase through
`apex-api-client-safe`.

```
1. Prepare the native APEX export/import artifact.
2. Import through the configured route for the user-selected environment.
3. Inspect the resulting APEX components and report the observed outcome.
```

## Integration Points

| Phase | Orchestrates | Purpose |
|-------|--------------|---------|
| **Setup** | `oracle-data-change-governance-final` | Defaults, standards, and audit guidance for DDL |
| **Phase 1** | `apex-schema-automation-safe` | Schema creation |
| **Phase 2** | Internal validation | Pre-migration health check |
| **Phase 3** | `apex-data-migration-safe` | ETL with rollback |
| **Phase 4** | `apex-page-automation-safe` + configured native route | Optional APEX artifact import; separate from data migration |
| **Audit** | Git (.bitacora.json) | Complete audit trail |

## Features

### Safety

- **Governance guidance** - Apply DDL standards without requiring additional approval
- **Rollback points** - Savepoint at each phase
- **Validation gates** - Data quality checks before load
- **Pre-migration checks** - Health verification

### Automation

- **Workflow outline** - Four phases are a design outline; this file does not provide an executable end-to-end orchestrator
- **Batch optimization** - Large data handling
- **Parallel processing** - Where possible
- **Error recovery** - Automatic retry with backoff

### Observability

- **Phase tracking** - Progress at each step
- **Audit trail** - Complete operation log
- **Error reporting** - Detailed violation reports
- **Performance metrics** - Timing per phase

## Configuration

Example data migration project:

```yaml
orchestration:
  project_name: EMPLOYEE_MIGRATION
  source_env: legacy_oracle_db
  target_env: modern_apex_environment

phase_1_schema:
  tables:
    - name: EMPLOYEES
      columns:
        - name: EMP_ID
          type: NUMBER
          not_null: true
        - name: EMP_NAME
          type: VARCHAR2(100)
          not_null: true
    - name: DEPARTMENTS
      columns:
        - name: DEPT_ID
          type: NUMBER
        - name: DEPT_NAME
          type: VARCHAR2(50)

phase_2_validation:
  checks:
    - schema_readiness
    - connectivity
    - storage_available

phase_3_migration:
  mappings:
    OLD_EMP: EMPLOYEES
    OLD_DEPT: DEPARTMENTS

  validation_rules:
    EMPLOYEES:
      - "NOT NULL: EMP_ID"
      - "UNIQUE: EMAIL"
      - "RANGE: SALARY 0-1000000"
    DEPARTMENTS:
      - "NOT NULL: DEPT_ID"

  phase_4_apex_import:
    route: configured_native_apex_import
    target_env: user_selected_environment
```

## Error Handling

- **Phase 1 (Schema) failure** → Rollback using stored DDL, retry with fixes
- **Phase 2 (Validation) failure** → Stop before migration, report issues, retry
- **Phase 3 (Migration) failure** → Rollback to savepoint, investigate, retry
- **Phase 4 (Import) failure** → Report the configured route's error; use its documented recovery and rollback procedure

## Logging

Complete operation log:

```
2026-09-17 10:00:00 - PHASE_START - Schema Automation
2026-09-17 10:05:00 - CREATE_TABLE - EMPLOYEES (500ms)
2026-09-17 10:10:00 - CREATE_TABLE - DEPARTMENTS (300ms)
2026-09-17 10:15:00 - CREATE_INDEX - IDX_EMP_EMAIL (200ms)
2026-09-17 10:20:00 - ROLLBACK_POINT_CREATED - rp_schema_20260917
2026-09-17 10:25:00 - PHASE_COMPLETE - Schema Automation (25s)

2026-09-17 10:30:00 - PHASE_START - Data Validation
2026-09-17 10:35:00 - PRE_MIGRATION_CHECK - PASSED
2026-09-17 10:40:00 - PHASE_COMPLETE - Data Validation (10s)

2026-09-17 10:45:00 - PHASE_START - Data Migration
2026-09-17 10:50:00 - EXTRACT_START - 50000 rows from EMPLOYEES
2026-09-17 11:00:00 - EXTRACT_COMPLETE - 50000 rows (15s)
2026-09-17 11:05:00 - TRANSFORM_START - Apply mappings
2026-09-17 11:15:00 - TRANSFORM_COMPLETE - 50000 rows transformed (10s)
2026-09-17 11:20:00 - VALIDATE_START - Quality checks
2026-09-17 11:25:00 - VALIDATE_COMPLETE - 50000 valid, 0 violations (5s)
2026-09-17 11:30:00 - LOAD_START - Insert into target
2026-09-17 11:45:00 - LOAD_COMPLETE - 50000 rows loaded (15s)
2026-09-17 11:50:00 - ROLLBACK_POINT_CREATED - rp_migration_20260917
2026-09-17 11:55:00 - PHASE_COMPLETE - Data Migration (70s)

2026-09-17 12:00:00 - PHASE_START - APEX Sync
2026-09-17 12:10:00 - DEPLOY_TEST - Sync to TEST environment
2026-09-17 12:20:00 - DEPLOY_PROD - Sync to PROD environment
2026-09-17 12:30:00 - VERIFY_INTEGRITY - PASSED
2026-09-17 12:35:00 - PHASE_COMPLETE - APEX Sync (35s)

2026-09-17 12:40:00 - PIPELINE_COMPLETE - Total: 140 seconds
```

## Performance

Typical end-to-end timing:

| Phase | Duration (50K rows) | Bottleneck |
|-------|---------------------|-----------|
| Schema Automation | 30-60s | Network latency |
| Data Validation | 10-20s | Source connectivity |
| Data Migration | 60-120s | Transformation rules |
| APEX Sync | 30-60s | REST API latency |
| **Total** | **2-5 minutes** | Data volume |

## Status

**Development outline; not an operational end-to-end orchestration pipeline.**

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
**Upstream Skills:**
- `oracle-data-change-governance-final` (governance and audit guidance)
- `apex-schema-automation-safe` (schema creation)
- `apex-data-migration-safe` (ETL)
- `apex-page-automation-safe` (optional APEX component work through configured native routes)
