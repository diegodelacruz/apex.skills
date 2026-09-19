Auditoría post-implementación independiente del ecosistema apex.skills.

Este auditor es DESACOPLADO: no usa skills, orquestadores ni scripts internos del framework.
Valida la integridad del repositorio después de cualquier cambio.

Ejecuta:

```bash
python scripts/post_impl_audit.py
```

Interpreta el reporte:
- Cada check muestra [OK] o [!!] con su ID (P01-P10)
- AUDIT_PASS = todo correcto, AUDIT_FAIL = hay hallazgos
- Si hay fallos, indica al usuario qué corregir y en qué archivo
- NO invoques ninguna skill del repositorio para diagnosticar o corregir

Checks que ejecuta:
- P01: Sintaxis Python (scripts/ y tests/)
- P02: Suite de tests (pytest completo)
- P03: Registro de skills (skill dirs <-> .claude/commands/)
- P04: Frontmatter YAML (campos requeridos, orders únicos)
- P05: Enlaces Markdown (docs/ y skills/)
- P06: Consistencia de configuración (thresholds, conteos)
- P07: Coherencia de imports (bare vs qualified)
- P08: Archivos requeridos del ecosistema
- P09: Baseline de secretos
- P10: Estado Git (archivos sin commit)

User request: $ARGUMENTS
