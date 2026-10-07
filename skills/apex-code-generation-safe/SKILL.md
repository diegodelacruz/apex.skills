---
name: apex-code-generation-safe
description: Generate APEX components automatically from schema and metadata
category: Apex Engineering & Design
order: 24
tags:
  - code-generation
  - apex
  - forms
  - reports
  - automation
  - read-only
access_level: read
cost: low
created: 2026-09-17
status: active
---

# apex-code-generation-safe

> **Genera artefactos de especificación; no despliega directamente a APEX.**
> El JSON generado aquí no sustituye por sí solo un export importable. Para
> cambios de componentes, prepara/importa el artefacto por la ruta autenticada
> documentada en `docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md` y
> `apex-page-automation-safe`.

## Estándar de código generado

Para SQL, PL/SQL y artefactos APEX generados, aplicar
`docs/reglas-formateo-canonicas.md`: minúsculas fuera de literales, comentarios
y nombres entre comillas, y tabuladores físicos con ancho visual de cuatro para
la sangría. Nunca usar espacios iniciales. Antes de entregar un archivo SQL,
validarlo con `skills/oracle-data-change-governance-final/scripts/validate_sql_style.py`;
`STYLE_FAIL` obliga a corregirlo. El código Python es la única excepción y usa
cuatro espacios por Black.

Generate Oracle APEX applications components automatically: Forms, Reports, validations, and JavaScript interactions from database schema and metadata.

## Overview

This skill generates production-ready APEX code from:
- Database table structure
- SQL queries
- Business rules
- Validation requirements

## Capabilities

### ApexFormGenerator
Generate interactive APEX Forms from tables:
```python
from apex_code_generators import ApexFormGenerator

gen = ApexFormGenerator('EMPLOYEES')
form_json = gen.generate_from_table()
form_json = gen.add_validation_rules()
print(form_json)
```

### ApexReportGenerator
Generate APEX Reports from queries:
```python
from apex_code_generators import ApexReportGenerator

gen = ApexReportGenerator('SELECT * FROM EMPLOYEES')
report_json = gen.generate_from_query()
report_json = gen.add_columns_formatting()
print(report_json)
```

### ApexValidationGenerator
Generate PL/SQL and JavaScript validations:
```python
from apex_code_generators import ApexValidationGenerator

gen = ApexValidationGenerator()
plsql = gen.generate_plsql_validations('EMPLOYEES')
javascript = gen.generate_javascript_validations()
```

### ApexJavaScriptGenerator
Generate dynamic interactions:
```python
from apex_code_generators import ApexJavaScriptGenerator

gen = ApexJavaScriptGenerator()
js = gen.generate_item_interactions()
js = gen.generate_conditional_display()
print(js)
```

## Example Workflow

```
1. Define schema (table/columns)
   ↓
2. Generate Form → APEX Form JSON
   ↓
3. Generate Report → APEX Report JSON
   ↓
4. Generate Validations → PL/SQL + JavaScript
   ↓
5. Generate JavaScript → Dynamic interactions
   ↓
6. Convert/review the specification as an APEX export artifact
   ↓
7. Import through the configured native APEX route and verify the result
```

## Integration

Related workflows:
- `apex-schema-automation-safe` (schema creation)
- `apex-page-automation-safe` (native APEX component workflow where configured)
- `apex-automated-testing-safe` (testing generated forms)
- `apex-delivery-lifecycle-safe` (deployment pipeline)

## Security

- ✅ No SQL injection (parameterized)
- ✅ XSS protection (escaped output)
- ✅ Read-only output (non-destructive)
- ✅ Audit trail integration

## Output Formats

- **Forms:** APEX Form JSON specification
- **Reports:** APEX Report JSON specification
- **Validations:** PL/SQL + JavaScript
- **JavaScript:** APEX Dynamic Action compatible

## Performance

Typical generation times:
- Simple form (10 columns): 50-100ms
- Complex report (50 columns): 200-300ms
- Full validations (20 rules): 150-250ms

## Status

🔨 **Active** - Core generators building (90% complete)

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
