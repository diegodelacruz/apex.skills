# Auditoría obligatoria

Toda mejora de skill, inicializador, documentación, plan de implementación o entrega APEX debe pasar auditoría antes de declararse terminada. No es opcional ni se sustituye por una revisión visual.

## Mínimo requerido para este repositorio

Ejecute desde la raíz de `apex.skills`:

```powershell
python .\scripts\audit_skill_ecosystem.py
git diff --check
```

La auditoría verifica recursos requeridos y enlaces Markdown locales. `git diff --check` detecta errores de espacios en blanco. Para código modificado se ejecuta además la validación correspondiente, por ejemplo:

```powershell
python -m py_compile .\scripts\nombre_del_script.py
```

Para PowerShell se valida el parser, y para cambios APEX/Oracle se ejecutan las pruebas de sólo lectura, QA y evidencias definidas por el plan de implementación.

## Criterio de cierre

Sólo se puede comunicar “listo”, generar el manual final o publicar una versión cuando:

1. La auditoría aplicable pasa sin referencias rotas.
2. Las pruebas o validaciones del artefacto modificado pasan.
3. El resultado y cualquier limitación quedan registrados en el plan y decisiones del proyecto.
4. No se expusieron secretos en consola, documentación, Git o evidencias.

La skill `apex-project-bootstrap-final` obliga esta revisión para cada proyecto nuevo y cada hito posterior.
