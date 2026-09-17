---
name: apex-data-orchestrator-safe
description: Orchestrate complete data workflow - schema creation, migration, validation, and APEX sync
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
status: development
---

# apex-data-orchestrator-safe

**Sub-Coordinator Orchestrator:** Coordinate schema automation → data migration → APEX sync.

Manage complete data workflows from database schema creation through safe migration to APEX synchronization, with comprehensive validation and rollback capability at each step.

## Overview

Execute full data pipeline safely:
- **Schema Automation** - Create/modify database objects under governance
- **Data Validation** - Comprehensive data quality checks
- **ETL Migration** - Extract, transform, validate, load data
- **APEX Sync** - Deploy and synchronize across environments
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
│ │ Phase 4: APEX Sync                         │  │
│ │ Delegate to: apex-api-client-safe          │  │
│ │ - Deploy schema objects to APEX            │  │
│ │ - Synchronize data to TEST/PROD            │  │
│ │ - Verify sync integrity                    │  │
│ └────────────────────────────────────────────┘  │
│                      ↓                           │
│ ┌────────────────────────────────────────────┐  │
│ │ Outputs:                                    │  │
│ │ - Schema created in target environment    │  │
│ │ - Data migrated safely                     │  │
│ │ - APEX synchronized                        │  │
│ │ - Rollback points created                  │  │
│ │ - Audit trail recorded                     │  │
│ └────────────────────────────────────────────┘  │
│                                                   │
└──────────────────────────────────────────────────┘
```

## Capabilities

### Safe Data Pipeline Execution

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

# Phase 4: Sync to APEX
orchestrator.sync_to_apex(
    instances=['https://apex-test.example.com', 'https://apex-prod.example.com'],
    verify_integrity=True
)

# Get complete audit trail
audit = orchestrator.get_operation_log()
```

## Workflow

### Phase 1: Schema Automation

Delegate to `apex-schema-automation-safe`:

```
1. Under oracle-data-change-governance-final gate:
   - Create tables
   - Create views
   - Create sequences
   - Add indexes
   - Add constraints

2. Validate schema:
   - Syntax validation
   - Object dependencies
   - Naming conventions

3. Create rollback point:
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

### Phase 4: APEX Sync

Delegate to `apex-api-client-safe`:

```
1. Deploy schema objects:
   - Package objects as exportable components
   - Deploy to TEST environment first
   - Verify object creation in APEX

2. Synchronize data:
   - Create REST endpoints for data
   - Sync to TEST environment
   - Sync to PROD environment

3. Verify sync:
   - Row count verification
   - Data integrity checks
   - Connection validation
```

## Integration Points

| Phase | Orchestrates | Purpose |
|-------|--------------|---------|
| **Setup** | `oracle-data-change-governance-final` | Governance gate for all DDL |
| **Phase 1** | `apex-schema-automation-safe` | Schema creation |
| **Phase 2** | Internal validation | Pre-migration health check |
| **Phase 3** | `apex-data-migration-safe` | ETL with rollback |
| **Phase 4** | `apex-api-client-safe` | APEX synchronization |
| **Audit** | Git (.bitacora.json) | Complete audit trail |

## Features

### Safety

- **Governance gates** - DDL changes under `oracle-data-change-governance-final`
- **Rollback points** - Savepoint at each phase
- **Validation gates** - Data quality checks before load
- **Pre-migration checks** - Health verification

### Automation

- **End-to-end orchestration** - All 4 phases coordinated
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

phase_4_sync:
  instances:
    - https://apex-test.example.com
    - https://apex-prod.example.com
  verify_integrity: true
```

## Error Handling

- **Phase 1 (Schema) failure** → Rollback using stored DDL, retry with fixes
- **Phase 2 (Validation) failure** → Stop before migration, report issues, retry
- **Phase 3 (Migration) failure** → Rollback to savepoint, investigate, retry
- **Phase 4 (Sync) failure** → Rollback sync, investigate connectivity, retry

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

🚧 **Development** - Data orchestration coordinator (25% complete)

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
**Upstream Skills:**
- `oracle-data-change-governance-final` (governance gate)
- `apex-schema-automation-safe` (schema creation)
- `apex-data-migration-safe` (ETL)
- `apex-api-client-safe` (APEX sync)
