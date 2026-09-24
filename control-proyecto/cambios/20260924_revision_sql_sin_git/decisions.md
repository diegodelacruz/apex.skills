# Revisión de SQL local sin requisito de Git

## Objetivo y necesidad

Evitar que una revisión estática solicitada de un archivo SQL/PLSQL se rechace sólo porque la carpeta que lo contiene no es un repositorio Git. El usuario reportó ese rechazo al pedir una revisión de un paquete en producción.

## Decisión y alcance

Actualizar `skills/apex-database-diagnostics/SKILL.md` para declarar explícitamente que la inspección estática local no requiere `.git` ni comandos Git. Git sólo aplica cuando se solicita historial, rama o procedencia de cambios. La regla conserva la distinción entre revisar el archivo y validar comportamiento contra la base de datos.

## Alternativas e impacto

No se modifican las políticas de acceso Oracle, las conexiones autorizadas, ni los límites de solo lectura en producción. No se agrega dependencia, permiso o ruta. No se cambia `path_setup.py`: su búsqueda de la raíz Git sirve a scripts de este repositorio y no es el flujo de lectura del archivo SQL entregado por el usuario. Como alternativa, se podría dejar la regla implícita, pero eso no prevendría que un agente imponga un requisito Git ajeno a la revisión.

## Validación y rollback

Validación: `python scripts/audit_skill_ecosystem.py` (`AUDIT_PASS`), `python scripts/audit_quality_score.py` (`100/100`), `python -m pytest tests -v` (`483 passed`, 57.07% coverage), `bash scripts/security-audit.sh` (8/8 checks; Bandit and mypy check passed under that script), and `git diff --check` (clean). La revisión independiente confirmó que el flujo ahora permite la revisión estática sin perfil y conserva los controles autorizados para ejecución/despliegue; también motivó aclarar que TEST/runtime se informa como no ejecutado cuando no aplica. Las comprobaciones equivalentes a CI encontraron fallos de formato, flake8 y mypy estricto en archivos existentes de external-context; ver los hallazgos de auditoría. No se ejecutó SQL ni se usó una conexión de producción. Responsable: Codex; agente revisor: agente externo independiente. Para revertir, restaurar el paso anterior de `SKILL.md` y retirar este registro de decisión.
