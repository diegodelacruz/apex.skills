# Corrección del inventario de skills

## Objetivo y necesidad

Alinear la documentación vigente y la prueba del auditor con el inventario real de 31 archivos `SKILL.md`, después de agregar `apex-external-context-learn` en GitHub.

## Decisión y alcance

- Actualizar los conteos vigentes en `CLAUDE.md`, `skills/README.md` y `docs/ACTUALIZACION-ECOSISTEMA.md` a 31 skills: 25 técnicas y 6 orquestadores.
- Hacer que `test_quality_audit.py` compare la evidencia del auditor con el número de skills encontrado en el repositorio, en lugar de codificar un total fijo.
- Mantener intactos los changelogs históricos que describen inventarios anteriores.

## Alternativas e impacto

Se consideró cambiar únicamente la expectativa fija de 30 a 31. Se elige una comprobación dinámica para evitar que la misma prueba quede obsoleta al agregar otra skill. El cambio no agrega dependencias, accesos ni datos; sólo corrige documentación y validación del inventario.

## Validación y rollback

Ejecutar `python scripts/audit_skill_ecosystem.py`, `python scripts/audit_quality_score.py`, `python -m pytest tests/test_quality_audit.py -q` y `git diff --check`. El rollback consiste en revertir este registro y los cuatro archivos afectados si la auditoría no confirma el inventario.
