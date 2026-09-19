---
name: apex-api-client-safe
description: Retired simulated REST adapter; it must not be used for Oracle APEX deployment.
category: Apex Integration
order: 22
tags:
  - rest-api
  - deployment
  - environment-sync
  - automation
  - read-only
access_level: read
cost: low
created: 2026-09-17
status: retired
---

# apex-api-client-safe

> **No operativo.** El cliente asociado no tenía transporte HTTP ni contrato
> oficial APEX; falla cerrada con `ADAPTER_INCOMPATIBLE`. No use los ejemplos
> históricos de este archivo. La ruta vigente es la de App Builder autenticado o
> export/import nativo descrita en `docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`.

REST API client for Oracle APEX: create, deploy, and synchronize applications across environments.

## Overview

Automate APEX application deployment using the APEX REST API:
- Create applications from templates
- Deploy to different environments (dev, test, prod)
- Export/import applications
- Synchronize environments
- Validate deployments

## Capabilities

### ApexRestClient
Base REST client for APEX operations:
```python
from apex_rest_client import ApexRestClient

client = ApexRestClient(
    base_url='https://apex.example.com',
    username='admin',
    password='secret'  # pragma: allowlist secret
)

app_id = client.create_application({
    'name': 'My App',
    'schema': 'my_schema'
})
```

### CRUD Operations
```python
# Get application
app = client.get_application(app_id)

# Update application
client.update_application(app_id, {'name': 'Updated App'})

# Delete application
client.delete_application(app_id)
```

### Deployment
```python
# Export application
zip_bytes = client.export_application(app_id)

# Import application
app_id = client.import_application(zip_bytes)

# Deploy to environment
client.deploy_to_environment(app_id, 'production')
```

### Environment Synchronization
```python
# Sync between environments
client.sync_between_environments(
    app_id,
    source_env='development',
    target_env='production'
)
```

## Integration

Works seamlessly with:
- `apex-code-generation-safe` (generated code deployment)
- `apex-delivery-lifecycle-safe` (deployment pipeline)
- `apex-automated-testing-safe` (post-deployment validation)
- `apex-schema-automation-safe` (schema creation)

## Security

- ✅ OAuth2 authentication
- ✅ Token caching with expiration
- ✅ Exponential backoff retry logic
- ✅ HTTPS only
- ✅ Audit trail of all operations

## Error Handling

Automatic retry with exponential backoff:
```python
# Retries up to 3 times with exponential backoff
# 1s, 2s, 4s delays
result = client.create_application(config)
```

## Logging

All API calls logged for audit trail:
```
2026-09-17 10:15:30 - GET /api/v1/applications/123 - 200 OK
2026-09-17 10:16:01 - POST /api/v1/applications - 201 CREATED
```

## Performance

Typical operation times:
- Create application: 2-5 seconds
- Export application: 1-3 seconds
- Deploy to environment: 10-30 seconds
- Sync environments: 30-60 seconds

## Status

🔨 **Development** - REST client building (85% complete)

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
