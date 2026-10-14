# Oracle y APEX: credenciales, ambientes y herramientas

## Fuente de permisos

El usuario indica la operación, el alcance y el ambiente. El agente usa la
credencial configurada para ese ambiente (`DB_TESTING_*` o `DB_PRODUCTION_*` en
`.env` para SQLcl, o el perfil equivalente que usa el conector seleccionado).
Oracle/APEX y el DBA determinan las operaciones efectivas de esa cuenta. No hay
una lista fija de permisos por ambiente ni un usuario hardcodeado en las skills.
La presencia de un perfil, el nombre del MCP, el nombre de una cuenta o un
resultado histórico no demuestra privilegios actuales.

Para identificar un destino cuando sea necesario, el coordinador puede hacer
una comprobación mínima de cuenta y ambiente. No inspeccione grants como
validación previa, intermedia o final de una operación solicitada: ejecútela con
la credencial configurada y reporte el resultado real de Oracle/APEX. Use
`inspect_oracle_privileges` solo si el usuario pide ver grants/roles o solicita
diagnosticar un error de acceso observado. Los grants visibles son informativos
y no garantizan que la operación vaya a tener éxito. No realizar mutaciones de
prueba para averiguar permisos ni pedir al usuario consultas que el agente
puede ejecutar.

Si la identidad o destino observado no corresponde al ambiente solicitado, no
leer contenido de objetos ni ejecutar cambios en ese destino; informar la
discrepancia. Si un canal devuelve datos antes de poder confirmar identidad,
descartar esos datos y no presentarlos. Un error de privilegio se informa tal
como lo devolvió el servicio. Una lectura denegada no impide intentar una ruta
configurada alternativa para el mismo ambiente, sin cambiar de cuenta/destino
de manera silenciosa.

Para una solicitud de lectura puntual, verificar primero la identidad/destino
con una sonda mínima si aún no está confirmado en la conexión activa y consultar
enseguida. No ejecutar como rutina `inspect_environment`, un inventario de
privilegios ni una inspección separada de contexto APEX. Reutilizar la identidad
verificada durante la conexión activa. Consultar esas herramientas adicionales
cuando resuelvan una ambigüedad concreta o un error actual. Los errores de
sesiones anteriores son pistas, no bloqueos actuales; volver a comprobar la
ruta y el resultado con las credenciales configuradas para esta solicitud.

## Herramientas por operación

| Operación | Ruta preferida | Credencial y alcance |
| --- | --- | --- |
| Oracle: inspeccionar objetos, columnas, errores y datos | `apex-controlled-mcp.execute_readonly_query` (SELECT de metadata con binds enteros); `inspect_oracle_session`, `inspect_oracle_privileges`, `inspect_environment`; MCP Oracle de lectura; `scripts/Execute-OracleSql.ps1 -ReadOnly` | Perfil Oracle seleccionado para el ambiente. La transacción de solo lectura bloquea DML directo; la ruta se reserva a consultas conocidas porque un SELECT puede invocar funciones con efectos laterales. |
| Oracle: ejecutar un DML puntual confirmado | `apex-controlled-mcp.execute_sql_file` o `Execute-OracleSql.ps1` | Las rutas controladas exigen `confirmed=true` y `backup_choice=yes/no`. Con sí, requieren y ejecutan un SQL de backup dedicado antes; si falta o falla, bloquean el DML. Registran inicio/resultado y hashes en `.bitacora.json`, sin SQL ni credenciales. No requiere conteo previo, bundle ni plan por defecto. |
| Oracle: ejecutar DDL/PLSQL o cambio coordinado | `execute_sql_file`, SQLcl; `execute_change_bundle` cuando se necesita comprobar una fingerprint o coordinar objetos | Usar la credencial seleccionada. Bundle/preflight es condicional al alcance. Con backup afirmativo, `execute_change_bundle` requiere `snapshot.sql` y lo ejecuta tras preflight y antes de apply; ante falla detiene apply. |
| APEX: listar aplicaciones, inspeccionar páginas/componentes y comparar metadata | Herramientas de lectura del MCP APEX configurado; `inspect_apex_context` / `inspect_environment`; export nativo o App Builder si la cuenta lo permite | Perfil APEX/App Builder configurado para el ambiente, o la sesión Oracle elegida cuando se leen vistas de metadata. Confirmar identidad y destino observados; el rótulo del MCP no basta. |
| APEX: crear, modificar, importar o eliminar componentes | Herramienta APEX de escritura disponible, `deploy_apex_page`, `Deploy-ApexPage.ps1` o bundle cuando aporta fingerprint/coordination | Las rutas controladas exigen ambas decisiones. Si backup=yes, requieren un export nativo previo; la validación sintáctica no prueba que refleje el estado vivo exacto. Los ejecutores MCP y PowerShell registran inicio/resultado correlacionados y hashes para escrituras en `.bitacora.json`; las consultas de solo lectura guardan un hash posterior al resultado. Herramientas externas no están cubiertas por esa garantía. |
| APEX: diagnóstico de error funcional | Metadata de solo lectura, export existente, logs/herramientas APEX configuradas; `apex-environment-alignment-complete` para comparación cuando aporte evidencia | No modificar durante diagnóstico salvo que el usuario también pidió la corrección. |

Los nombres `DB_TESTING_*` y `DB_PRODUCTION_*` son las claves de configuración
que consume actualmente el ejecutor SQLcl; no codifican grants. Si no se indica
ambiente en la solicitud, inferirlo del contexto y luego del selector `DB_ENV`.
Si ninguno define el destino, pedir solo el ambiente antes de conectar; no
elegir TEST o Producción a ciegas.

`execute_readonly_query` ejecuta una sola consulta SELECT de metadata sin archivo
SQL y no depende de que el proyecto sea un checkout Git. No usarla como sandbox
para SQL arbitrario: Oracle permite ciertos efectos laterales de funciones
llamadas desde SELECT aunque la transacción sea de solo lectura.
`execute_sql_file` requiere un
archivo `.sql` dentro del checkout que sirve al MCP; úsalo para DDL/DML/PLSQL.
Las herramientas mutativas bloquean la llamada si falta la confirmación o la
decisión explícita sí/no de backup. Estos campos reflejan la respuesta que el
agente recibió; no constituyen autenticación criptográfica del usuario. Cuando
backup=yes, usa un `backup_sql_path` dedicado que capture el alcance exacto y
verifica que termine correctamente antes de ejecutar el SQL principal.
No convertir una limitación de ruta del archivo en una limitación de acceso a
Oracle.

## Lecturas y cambios en vivo

Revisar o mostrar datos/especificaciones es read-only: verifica el destino una
vez si hace falta y consulta de inmediato. No inicies QA, inventarios ni el
flujo de cambios para una lectura simple.

Antes de una mutación, pide una sola confirmación que identifique ambiente,
objeto, operación, confirmación de ejecución y respuesta sí/no sobre backup. No
se ejecuta si falta una respuesta. Los argumentos del MCP bloquean campos
ausentes, pero no autentican criptográficamente a quien respondió. No se crea
backup, snapshot ni conteo previo por defecto. Si el usuario acepta backup,
prepara un SQL de backup específico, ejecútalo y verifica primero; si falta o
falla, detén la operación y reporta el bloqueo.

Cuando una corrección existente requiera comparar la huella base, o el cambio
coordine varios objetos, usa un `change.json` con preflight, apply, verify y
rollback. Si la huella cambió, detén ese bundle y vuelve a inspeccionar. Añade
snapshot únicamente cuando el usuario pidió backup.

Para diagnóstico de páginas, no exigir que el `SESSION_USER` de SQLcl sea igual
al esquema de parsing del workspace. Si el chequeo de asociación muestra una
diferencia, conservarla como contexto y probar la lectura de las vistas públicas
de metadata con la credencial elegida. Si el helper de página del MCP falla por
incompatibilidad de columnas o el helper de contexto devuelve ORA-20987, usar
consultas enlazadas mediante `execute_readonly_query` o `apex_run_sql` contra
`APEX_APPLICATION_PAGE_REGIONS`, items, procesos, botones, acciones y
validaciones. No acceder a `WWV_FLOW_*` internos.

## Separación entre herramientas y privilegios

Un conector puede exponer operaciones más amplias que las concedidas a su
credencial. La superficie de herramientas solo determina qué se puede intentar;
no concede permisos Oracle/APEX. A su vez, las credenciales con privilegios
amplios no autorizan cambios fuera de la solicitud del usuario. Usar la ruta
especializada cuando mejore la evidencia o el formato (por ejemplo, import
nativo APEX), sin añadir un gate de aprobación para una solicitud directa.

Por decisión del usuario, se consideran capacidades intencionales la ejecución
de DDL/DML/PLSQL Oracle solicitado y las operaciones APEX disponibles para la
credencial configurada, incluso cuando la operación resulte destructiva o el
ambiente se llame Producción. No son fallos que la skill carezca de una lista
local de grants/objetos o que envíe la operación a Oracle/APEX para obtener la
decisión efectiva. La solicitud sigue delimitando qué cambio realizar; el DBA y
el servicio deciden si la cuenta puede ejecutarlo.

## Secretos y evidencia

No imprimir contraseñas ni escribirlas en archivos versionados. Registrar
ambiente, cuenta observada (sin exponer secretos), destino, objeto/aplicación,
sentencia/artefacto pertinente y resultado. No guardar cadenas de conexión que
incluyan contraseña.
