# Decisiones: instalación y upstreams resilientes

## Objetivo y alcance

Permitir una instalación nueva con un solo comando, incluso si un upstream remoto no está disponible. Mantener dentro de `apex.skills` una copia base de los tres upstreams administrados. Al instalar, usar la copia base, comprobar los remotos, respaldar antes de actualizar y continuar con la versión anterior si la consulta, descarga o validación de una actualización falla.

## Necesidad observada

El reporte del compañero muestra una inicialización que exigió repetir el comando con `-InstallSharedDependencies`, luego detenerse por `apex-mcp` ausente y después fallar a mitad de la clonación de upstreams cuando Git no encontró `zaimella-skill`. El instalador existente ya ofrece un comando compuesto, pero descarga primero y aborta ante el primer remoto ausente; no incorpora una copia base en Git.

## Alternativas

1. Documentar una secuencia de varios comandos: rechazada porque vuelve a dejar el orden de preparación al usuario.
2. Usar únicamente las copias locales ignoradas en `.upstreams`: rechazada porque no llegan con una clonación nueva de `apex.skills`.
3. Incluir snapshots versionados con SHA-256 verificado en `vendor/upstreams`, con sincronización remota por repositorio, backup verificable y fallback local: elegida. Las referencias opcionales permanecen fuera de la instalación normal.

## Alcance técnico previsto

- Reutilizar el snapshot empacado en cada clon nuevo.
- Consultar cada upstream administrado de forma independiente; una indisponibilidad no cancela los demás.
- Descargar una actualización a un staging temporal, validar URL, rama, commit, integridad y aplicación del overlay local aprobado antes de sustituir la copia activa.
- Crear backup verificable del snapshot activo y del registro antes de reemplazarlo; rollback sólo del repositorio afectado.
- No cambiar ni borrar `.upstreams` preexistente si está sucio, es incompatible o la actualización falla.
- Hacer que el bootstrap Codex prepare upstreams, Python y skills en la misma ejecución, sin requerir reejecutar con una bandera para el caso normal.
- Mantener `apex-mcp` sin registro automático; su superficie y modificaciones locales contienen operaciones APEX internas de escritura.

## Hallazgos, impactos y límites

- Las tres copias administradas locales existen y coinciden con los commits del lock actual.
- `apex-mcp` tiene siete archivos modificados localmente (189 inserciones y 69 eliminaciones); se preservarán exactamente. Su patch cubre conexión directa, compatibilidad APEX 24.1.3 y edición de aplicaciones existentes. La política de este cambio no ejecutará ni registrará ese MCP.
- `zaimella-skill` (1.45 MB) y `zaimella-apex-oracle` (23.32 MB) no contienen `LICENSE`, `COPYING` ni `NOTICE` en sus snapshots. La licencia sigue declarada como no identificada; el responsable del repositorio confirmó el 2026-09-23 que autoriza redistribuir ambos snapshots en `diegodelacruz/apex.skills`.
- Confirmación del usuario, 2026-09-23: el snapshot completo de `zaimella-apex-oracle` está saneado y su publicación está autorizada; también confirmó la redistribución de `zaimella-skill` en GitHub. Un escaneo `detect-secrets` de los tres ZIP extraídos de forma segura reportó cero candidatos; no se mostraron valores.
- El usuario autorizó publicar `execute_sql_file` con el alcance y riesgo documentados: ejecuta cualquier `.sql` dentro del checkout contra el ambiente seleccionado, incluso producción si se solicita expresamente, con los privilegios Oracle de la conexión. La anotación destructiva MCP informa al cliente, pero no impone aprobación; la documentación exige mostrar el archivo y obtener confirmación explícita antes de invocarlo.
- `zaimella-apex-oracle` no aparece como dependencia de ejecución de los scripts de instalación; conservarlo como upstream administrado y respaldarlo no significa instalarlo como paquete Python.
- Las ramas remotas `zaimella-skill/main` y `zaimella-apex-oracle/main` avanzaron respecto de los commits fijados al momento del inventario. No se actualizarán las copias locales durante la preparación del mecanismo.
- Las referencias `oracle-apex` (247.84 MB) y `emilkowalski-skills` (0.23 MB) son opcionales y se excluyen del bundle normal.

## Riesgos y controles

- Riesgo de incluir secretos o datos sensibles en snapshots: ejecutar auditoría de secretos/seguridad antes de considerar publicable el cambio.
- Riesgo de incompatibilidad del upstream nuevo: validar hash, manifiesto, rama, estado de staging y aplicación del patch; ante fallo se conserva el activo.
- Riesgo de filesystem/ZIP parcialmente extraído: extraer y verificar en staging; promover sólo tras validar todos los archivos y hashes.
- Riesgo de que una copia heredada con modificaciones no canónicas sea confundida con un upstream limpio: conservar el commit upstream y el overlay local como elementos separados y auditables.
- Auditoría desacoplada posterior detectó dos defectos corregidos en `Sync-ApexSkillUpstreams.ps1`: una promoción parcial podía dejar el destino incompleto y perder del staging la copia anterior; además, `git status` omitía archivos ignorados al decidir si una copia podía reemplazarse. La promoción registra el repositorio antes de copiar y recupera ante fallo; los archivos no rastreados, incluidos los ignorados, ahora protegen la copia local.
- Riesgo de cadena de suministro: la validación de una actualización de `apex-mcp` ejecuta el backend de construcción del código remoto mediante `pip wheel`. La instalación automática supone confianza en el upstream y en sus dependencias de construcción; hashes del bundle detectan corrupción, pero no autentican un repositorio comprometido.

## Compatibilidad, permisos y datos

El flujo se limita a Windows/PowerShell y Git para instalación local. La sincronización consulta repositorios remotos por HTTPS. No consulta Oracle, no usa credenciales Oracle, no cambia APEX ni registra servidores MCP. Se conserva la compatibilidad con las versiones/ramas registradas en `upstreams.lock.json` y APEX 24.1.3.

## Pruebas, rollback y descontinuación

Probar inicialización desde estado ausente, remoto indisponible, remoto con avance válido, actualización incompatible, archivos de snapshot corruptos, fallo a mitad de copia del candidato, archivo ignorado dentro del checkout y copia activa modificada. Verificar backup y restauración en cada caso. Descontinuar el bundle sólo después de demostrar que cada instalación nueva puede reconstruirlo desde una fuente con derechos y disponibilidad verificados.

## Trazabilidad

- Responsable: Diego de la Cruz Sandoval y Codex como equipo de trabajo.
- Agente: Codex.
- Repositorio: `apex.skills`.
- No se actualizarán ni modificarán checkouts remotos durante este cambio.
- Auditoría desacoplada realizada después de la implementación inicial: confirmó el fallo de rollback parcial y el riesgo de reemplazar archivos ignorados; ambos controles se corrigieron en `scripts/Sync-ApexSkillUpstreams.ps1`. La auditoría también señaló la ejecución del backend remoto y la autenticación de procedencia como riesgos residuales.
- Validación focalizada posterior a la corrección: un fixture temporal con remoto Git local confirmó que un archivo ignorado se conserva y bloquea el avance remoto, y que un fallo inyectado tras crear el destino parcial restaura la versión activa anterior y conserva el backup. El fixture fue eliminado al terminar.
- Cierre local: 468 pruebas pasaron; auditoría de ecosistema `AUDIT_PASS`; calidad `100/100`; seguridad `8/8`; mypy, Black, isort, flake8, sintaxis PowerShell, hashes de snapshots y aplicación del overlay pasaron. `git diff --cached --check` pasó.
- Auditoría independiente final del índice staged: verificó la corrección de los hallazgos previos y registró las decisiones explícitas del responsable sobre redistribución, ejecución SQL y saneamiento de snapshots.
