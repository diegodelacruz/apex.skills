# Decisión: rescate selectivo del PR #15 (auditoría semántica)

- **Fecha:** 2026-10-23
- **Estado:** pendiente de revisión independiente
- **Objetivo:** conservar lo que sigue siendo útil de la rama `main-id71p3` (PR #15, 12 commits del 2026-09-18 y 2026-09-19, "auditoría completa"). Ese PR no se puede integrar: su base tiene un mes, su CI falla, choca con `main` en 11 archivos y borra tres guías que `main` mantiene.
- **Alcance:** un diagnóstico de sólo lectura nuevo, `scripts/audit_semantic_checks.py`, con los controles SM08 (archivos huérfanos) y SM09 (frescura de documentación); sus pruebas; la eliminación de un bloque heredado inalcanzable en `scripts/Update-ApexSkillUpstreams-V2.ps1`; una mención en `docs/auditoria-obligatoria.md`, y el changelog. No cambia CI, `run_ci_checks.py`, skills, routing, catálogos ni la política.
- **Decisión:** se trasladan, reescritas sobre `main`, sólo las piezas vigentes que no chocan con nada. El auditor rescatado no es un gate porque hoy reporta 15 huérfanos y la política (§7) indica que todo `FAIL` bloquea y que la auditoría no corrige: convertirlo en gate obligaría a corregir hallazgos que aún no se revisaron con la persona usuaria. Termina con código 1 cuando hay hallazgos, para poder usarlo como gate en el futuro. Las demás piezas se descartan porque ya están en `main` o fueron reemplazadas, o se dejan pendientes de una decisión del responsable.

## Clasificación por commit

| Commit | Contenido | Clasificación | Motivo |
|---|---|---|---|
| `5939406` | Bloque muerto en `Update-ApexSkillUpstreams-V2.ps1` | **Vigente, trasladado** | El bloque final usa `$repos`, que no está definido. Con `-IncludeReferences` y una actualización exitosa, el script sigue de largo, crea un segundo directorio de backup vacío e imprime `UPDATE_COMPLETE` dos veces. La rama de rollback ya termina antes. |
| `5939406` | Orden de exit codes en `Setup-ApexSkills.ps1` | Reemplazado | `main` reestructuró la instalación: `requirements.txt` se verifica antes y `apex-mcp` se instala aparte, con su propia verificación. |
| `5939406` | Ruta personal de SQLcl en `Initialize-OracleConnection.ps1` | Reemplazado | `main` ya usa `$env:USERPROFILE`. Agregar `APEX_SQLCL_PATH` sería una capacidad nueva, no un rescate. |
| `5939406` | Atribución personal en `Initialize-ApexCodexProject.ps1` | Pendiente de decisión | Es la atribución del propio responsable del repositorio. Quitarla le corresponde a él. |
| `5939406` | Imports `scripts.` en `apex_export_utilities.py` y `run_apex_mcp_with_profile.py` | Descartado | `main` usa imports directos de forma consistente y ejecuta los scripts desde `scripts/`. Cambiarlos rompería la ejecución directa. |
| `5939406` | `apex-api-client-safe` como `retired` | Ya en `main` | `status: retired`. |
| `5939406` | Conteos, tabla y fecha de `CLAUDE.md` | Reemplazado | `main` tiene el inventario vigente (31 entradas), controlado por Q02. |
| `e29cc6a` | Borrado de tres guías marcadas como obsoletas | Descartado | `main` siguió manteniendo `conectar-agente-a-oracle.md`, `habilitar-escritura-apex.md` y `windows-inicializacion-apex.md`. No se resucitan borrados. |
| `e29cc6a` | Enlace en `SOLICITUD-PERMISOS-DBA-APEX-2413.md` | Ya en `main` | El destino existe y el enlace resuelve. |
| `e29cc6a` | Conteos en `README.md` y `CLAUDE.md`; umbral de cobertura en `pyproject.toml` | Reemplazado | El inventario cambió. `.coveragerc` es la fuente única del 55% (política §7). |
| `05a6c28` | `post_impl_audit.py` (P01–P10) y `/post-audit` | Reemplazado | Duplica `audit_quality_score.py` (Q01–Q09), `audit_skill_ecosystem.py` y `run_ci_checks.py`, que ya están en CI. |
| `9cdf2c7` | Estrategia L0–L4, registro, plantillas y `audit_security_checklist.py` | Pendiente de decisión | Crea un segundo documento "obligatorio", con release gates y rotación de auditores que la política canónica no define. Eso contradice la fuente única (§3). Debe decidirlo el responsable y, de aprobarse, entrar como cambio de política. El checklist L2 se superpone con `detect-secrets`, `bandit` y la línea base de secretos. |
| `9cdf2c7` | `audit_semantic_checks.py` SM01–SM07 | Reemplazado o defectuoso | SM03 y SM04 duplican Q01 y Q02. SM05 resuelve desde la carpeta de la skill rutas escritas desde la raíz del repositorio y da cuatro falsos positivos en `main`. SM02 depende de una lista fija de tags (ver `12a830a`). |
| `3f22c1a` | `audit_desacoplada.py`, punto de entrada único | Reemplazado | El runner de `main` es `run_ci_checks.py`. Según la política §1, un script local no constituye revisión independiente, sin importar de qué módulos dependa. |
| `17f5900` | Alcance y desacople en la documentación de auditoría | Pendiente de decisión | Sólo modifica los documentos de la estrategia L0–L4. |
| `b7664f1` | SM08 huérfanos, SM09 frescura | **Vigente, trasladado y corregido** | Recorría el árbol completo, incluidos `.venv`, `.claude/worktrees` y archivos sin versionar. Ahora se limita a los archivos versionados (`git ls-files`). SM09 aceptaba cualquier fecha precedida de "date"; ahora exige una etiqueta de actualización y excluye `docs/decisiones/`, cuyas fechas registran decisiones, no frescura. Recibe la fecha de corte como parámetro para que las pruebas sean determinísticas. |
| `b7664f1` | SM10, consistencia de conteos en los README | Reemplazado | Q02 ya exige cada skill en ambos catálogos y el conteo en `README.md` y `CLAUDE.md`. Además, la expresión de SM10 no coincide con "31 skill entries" y aprobaba sin verificar. |
| `b7664f1` | Sección en `MANUAL-DE-USO.md` | Reemplazado | Se documenta en `auditoria-obligatoria.md`, que es la guía de auditoría. |
| `5576f55` | La auditoría sólo diagnostica | Ya en `main` | La política §7 dice que la auditoría es de sólo lectura y que no corrige ni armoniza hallazgos. El auditor rescatado lo cumple y lo prueba. |
| `5492b80` | Formato Black de los scripts de auditoría | Sin objeto | Sólo afecta a código que no se traslada. El código nuevo pasa Black 26. |
| `e7ec786` | Excepción Black/Python a la regla de tabs | Ya en `main` | `docs/reglas-formateo-canonicas.md` ya la contiene. |
| `e80650c` | flake8 en scripts de auditoría y `controlled_capabilities.py` | Reemplazado | `main` pasa flake8 en CI. |
| `12a830a` | Ampliar `valid_tags` de SM02 | Reemplazado | Sin SM02 no aplica. Una lista fija ya está desactualizada: en `main` rechaza 8 tags legítimos, como los de `apex-external-context-learn`. |

## Alternativas, riesgos y compatibilidad

- **Alternativas:**
  - Integrar el PR completo: descartado por los choques y los borrados.
  - Rebasearlo: descartado, porque el resultado tendría más conflictos que contenido útil.
  - Activar SM08 como gate de CI: diferido hasta revisar los hallazgos con la persona usuaria.
- **Impacto y riesgos:**
  - SM08 decide por coincidencia de nombre de archivo, así que una mención en el changelog cuenta como referencia y un nombre muy genérico podría ocultar un huérfano.
  - SM09 sólo evalúa los documentos que declaran una fecha rotulada (hoy, 5 de 52).
- **Compatibilidad:** Python 3.13, sólo biblioteca estándar y `git`. No se conecta a Oracle ni a APEX.
- **Validación:**
  - `tests/test_audit_semantic_checks.py` cubre SM08, SM09, la sólo lectura, los códigos de salida y la regresión del bloque eliminado.
  - Se ejecutó `scripts/run_ci_checks.py`.
  - Hallazgos actuales en `main`: 13 documentos y 2 scripts sin menciones, y ningún documento clave vencido.
- **Rollback:** revertir el commit. No hay datos ni configuración que restaurar.
- **Seguimiento:** revisar con el responsable los 15 huérfanos, la estrategia L0–L4 y la atribución en `Initialize-ApexCodexProject.ps1`. Cerrar el PR #15 como reemplazado por este cambio.
