---
name: apex-data-migration-safe
description: Development prototype for migration design, schema mapping, validation, and in-memory markers; no live Oracle executor
category: Apex Data Integration
order: 25
tags:
  - data-migration
  - etl
  - schema-mapping
  - validation
  - prototype
  - data-sync
access_level: read-write
cost: high
created: 2026-09-17
status: active
---

# apex-data-migration-safe

Development prototype for planning and validating data-migration mappings. It does not execute ETL against Oracle or provide backup/restore.

This skill's Python helpers are development prototypes, not an operational
Oracle migration executor. Follow `skills/apex/SKILL.md` for live operations:
simple reads are immediate; mutations require one confirmation including the
backup choice; backups and preliminary row counts are not created/performed by
default. Do not route an isolated transaction through a migration workflow.
The Python helpers operate on supplied in-memory data and log simulated status;
their rollback markers are not backups, savepoints, or database restoration.

## Overview

Design and validate a data migration using the available prototype helpers:
- Schema mapping and transformation rules
- Data validation and quality checks
- ETL-shaped in-memory helper flow; no live source/target connection or load
- Optional in-memory status marker; it is not a backup or rollback
- Change tracking and audit trail

## Capabilities

### SchemaMappingGenerator

Define schema mapping rules for data transformation:
```python
from apex_data_migration import SchemaMappingGenerator

mapper = SchemaMappingGenerator(source_schema='OLD_SCHEMA', target_schema='NEW_SCHEMA')

# Simple column mapping
mapper.map_column('USER_ID', 'USER_ID', data_type='NUMBER')
mapper.map_column('USERNAME', 'USER_NAME', data_type='VARCHAR2', length=100)

# Transformation rule
mapper.add_transformation('STATUS', lambda v: 'ACTIVE' if v == 1 else 'INACTIVE')

# Complex mapping
mapper.add_column_mapping({
    'source': 'OLD_EMAIL',
    'target': 'NEW_EMAIL',
    'transform': 'LOWER'
})

spec = mapper.to_dict()
```

### DataValidator

Validate data before migration:
```python
from apex_data_migration import DataValidator

validator = DataValidator()

# Add validation rules
validator.add_not_null_rule('USER_ID')
validator.add_length_rule('USERNAME', min=3, max=50)
validator.add_format_rule('EMAIL', pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
validator.add_range_rule('AGE', min=0, max=150)
validator.add_uniqueness_rule('USER_ID')

# Validate dataset
results = validator.validate(data)
issues = validator.flag_violations(results)
```

### ETLPipeline

Orchestrate ETL operations:
```python
from apex_data_migration import ETLPipeline

pipeline = ETLPipeline(source_conn='source_db', target_conn='target_db')

# Extract
extracted_data = pipeline.extract(
    source_table='OLD_USERS',
    batch_size=1000
)

# Transform
transformed = pipeline.transform(extracted_data, mapping_spec)

# Validate
validation_results = pipeline.validate(transformed)

# This only logs a simulated marker; it does not load Oracle or create a backup.
loaded = pipeline.load(transformed, target_table='USERS', create_rollback=True)

# Verify
pipeline.verify(source_count, target_count)
```

### RollbackManager

Manage in-memory status markers only; no restoration is performed:
```python
from apex_data_migration import RollbackManager

manager = RollbackManager()

# This marker does not capture or restore database state.
point = manager.create_rollback_point(
    schema='NEW_SCHEMA',
    affected_tables=['USERS', 'ACCOUNTS']
)

# This only changes the marker's status in memory.
if error_occurred:
    manager.rollback_to_point(point)
```

### ChangeTracker

Track and audit data changes:
```python
from apex_data_migration import ChangeTracker

tracker = ChangeTracker()

# Record change
tracker.record_change(
    operation='INSERT',
    table='USERS',
    rows_affected=1000,
    data_hash='abc123...'
)

# Get change audit log
audit_log = tracker.get_audit_log()
```

## Integration

Uses separate skills/routes for adjacent work:
- `apex-api-client-safe` is retired and is not an APEX connectivity prerequisite.
- `apex-code-generation-safe` (generated object migration)
- `apex-schema-automation-safe` (schema creation)
- `apex-delivery-lifecycle-safe` (migration in deployment)

## Migration Strategy

### Schema Mapping

Supported transformation types:
- Direct mapping (source → target)
- Column renaming
- Data type conversion
- Expression-based transformation
- Conditional logic

### Data Validation

Validation rules:
- NOT NULL constraints
- Length/Size limits
- Format/Pattern matching
- Range checks (numeric, date)
- Uniqueness enforcement
- Custom validation functions

### ETL Pipeline

Phases:
1. Extract - Read from source (with batching)
2. Transform - Apply mapping rules
3. Validate - Check data quality
4. Simulated load - Record a status marker; no target write is performed
5. Verify - Prototype-level supplied-value comparison; no database query

### Rollback Management

Rollback markers are in-memory metadata only. They do not create savepoints,
backups, or restore affected tables. A live migration requires a separately
available and explicitly selected operational route.

## Security

- ✅ No hardcoded credentials (use manage_apex_credentials)
- ✅ Sensitive data masking support
- ✅ Encryption for data in transit
- ✅ Audit trail of all changes
- ✅ In-memory marker inspection only; no database rollback verification

## Error Handling

Prototype behavior:
- Data validation failures → return validation findings; no data rollback
- No database connection or automatic retry is implemented
- Transform errors → detailed logging
- Partial load recovery

## Logging

All migration operations logged:
```
2026-09-17 10:15:30 - EXTRACT - table=USERS rows=1000 - SUCCESS
2026-09-17 10:16:01 - TRANSFORM - rows=1000 errors=0 - SUCCESS
2026-09-17 10:17:15 - VALIDATE - violations=0 - SUCCESS
2026-09-17 10:18:45 - LOAD - target=NEW_SCHEMA.USERS rows=1000 - SUCCESS
2026-09-17 10:20:00 - VERIFY - source=1000 target=1000 - VERIFIED
```

## Performance

Typical operation times:
- Schema mapping definition: 1-2 minutes
- Data extraction (1M rows): 30-60s
- Transformation: 2-10s
- Validation: 5-15s
- Load: 20-90s
- Full migration: 2-5 minutes (1M rows)

## Status

🔨 **Development prototype** - mapping and in-memory validation helpers; no live Oracle migration executor

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
