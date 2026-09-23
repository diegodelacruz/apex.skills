# Política canónica de evolución del ecosistema

**Estado:** obligatoria
**Ámbito:** todo cambio en `apex.skills`, sin importar el agente utilizado, el
tipo de archivo o el tamaño del cambio.

## 1. Principio de independencia

Ningún agente o skill mantenido dentro de este repositorio puede aprobar por sí
solo un cambio que modifique el propio repositorio. El agente o skill que se
modifica no puede ser su único revisor.

La revisión debe realizarla un agente externo al repositorio o una persona
independiente. Se pueden ejecutar validadores determinísticos locales, pero no
constituyen por sí solos una revisión independiente.

Ningún archivo puede obligar técnicamente a un agente externo arbitrario. La
forma más sólida de hacer efectiva esta política en cada sesión es combinar la
regla canónica, adaptadores para cada agente, hooks, CI y revisión independiente.

## 2. Justificación de cambios

Antes de agregar, modificar o eliminar una skill, agente, adaptador, ruta,
dependencia, upstream, script, estándar o documento, se debe registrar:

- objetivo, necesidad y alcance;
- alternativas consideradas y motivo de la decisión;
- impacto, riesgos y dependencias;
- permisos y datos que puede utilizar;
- compatibilidad con agentes, sistemas operativos y versiones de APEX;
- plan de pruebas, rollback y descontinuación cuando corresponda.

No se debe crear una skill nueva si una existente puede cubrir correctamente la
necesidad sin perder claridad, seguridad o separación de responsabilidades.

## 3. Fuente única y consistencia

El inventario real de `skills/*/SKILL.md` es la fuente de verdad. Todo cambio
debe mantener sincronizados el `SKILL.md`, el routing, los catálogos, los
adaptadores, los índices, la documentación, las pruebas, los scripts, los
assets y las plantillas relacionadas.

Una skill no puede publicarse si queda huérfana, si el routing apunta a una
skill inexistente o si un catálogo declara información distinta.

## 4. Conexiones y dependencias

Toda modificación debe verificar enlaces Markdown, rutas locales, referencias
cruzadas, nombres de skills, scripts, plantillas, assets, adaptadores,
dependencias Python/Node, comandos de instalación, upstreams y referencias
externas.

Las referencias externas deben registrar URL, rama, commit, fecha, licencia,
clasificación y propósito. No se incorporarán secretos, credenciales, datos
reales, identificadores APEX ni código externo sin revisión de seguridad,
licencia y compatibilidad.

## 5. Estándares de programación

Los estándares canónicos de programación y documentación son obligatorios. Se
debe ejecutar el validador aplicable a cada cambio. Un estándar no aplicable se
debe marcar como `N/A` y justificar.

Los formateadores automáticos no pueden sustituir ni contradecir los estándares
canónicos. Cualquier modificación de estos estándares requiere una decisión
documentada y revisión independiente.

## 6. Upstreams y backups

Los upstreams `managed` son necesarios para funcionamiento y QA. Los upstreams
`references` sólo sirven para consulta y adaptación. Ambos se controlan desde
el registro único de upstreams.

Toda actualización debe:

1. revisar el estado Git, la URL, la rama y el commit esperado;
2. ejecutar preflight de disponibilidad remota y consistencia local en lectura;
3. conservar una copia base verificable dentro de `vendor/upstreams` para cada upstream administrado;
4. preservar copias locales con cambios desconocidos y no sustituirlas automáticamente;
5. preparar cada avance remoto en staging y aceptar únicamente un fast-forward de la rama registrada;
6. crear y verificar el backup del checkout afectado antes de reemplazarlo;
7. validar el commit, el overlay local y la compilación aplicable antes de activar la copia nueva;
8. usar la copia activa anterior o el snapshot incluido cuando un remoto no responda o la actualización falle;
9. restaurar automáticamente los checkouts ya reemplazados ante un fallo interno del proceso;
10. conservar evidencia del backup, actualización, fallback, validación y rollback.

No se deben actualizar upstreams manualmente fuera de `Sync-ApexSkillUpstreams.ps1`.

## 7. Auditoría y publicación

Durante el desarrollo se validan los archivos afectados. Antes de publicar se
ejecuta una auditoría integral del repositorio, incluyendo funcionalidad,
técnica, seguridad, dependencias, compatibilidad, routing, documentación,
upstreams, hooks, CI y rollback.

Todo `FAIL` bloquea la publicación. Todo `N/A` debe incluir una justificación
concreta. No se puede declarar una validación completa si una prueba obligatoria
no pudo ejecutarse.

Como mínimo, antes de publicar deben ejecutarse:

```powershell
python .\scripts\audit_skill_ecosystem.py
python -m pytest tests -v
git diff --check
git status --short
```

También se deben ejecutar los validadores de seguridad, formato, tipos,
dependencias y SQL que correspondan al cambio.

## 8. Evidencia y trazabilidad

Cada cambio debe conservar objetivo, decisión, responsable, agente utilizado,
archivos afectados, comandos ejecutados, resultados, limitaciones, riesgos,
aprobaciones y estado final. La publicación requiere evidencia reproducible y
revisión independiente.
