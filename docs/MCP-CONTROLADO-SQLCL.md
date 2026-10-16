# MCP con SQLcl administrado

## Propósito

`apex-controlled-mcp` es un servidor MCP local por STDIO que usa SQLcl y el
perfil Oracle del ambiente seleccionado. Puede coexistir con otros MCP Oracle/
APEX, incluido el upstream `apex-mcp` completo.

La solicitud directa define la operación, el alcance y el ambiente. El servidor
selecciona el perfil Oracle `DB_TESTING_*` o `DB_PRODUCTION_*` configurado en
`.env`; Oracle y los grants efectivos de esa cuenta deciden si la operación
procede. Las rutas APEX usan la credencial que corresponda al conector
seleccionado. No se codifican permisos por ambiente ni usuarios concretos.
Mantén los secretos fuera de archivos versionados.

## Runtime

`scripts/Install-ApexControlledRuntime.ps1` instala SQLcl y Java bajo
`%LOCALAPPDATA%\ApexSkills\runtimes`, fuera de Git y sin modificar PATH. El
bootstrap verifica el runtime y reporta los estados Oracle/APEX; sus sondeos
iniciales no limitan operaciones posteriores.

## Herramientas

El servidor incluye `doctor`, inspección de entorno, sesión Oracle, contexto
APEX, privilegios, ejecución de consultas SELECT en transacción de solo lectura,
ejecución SQL desde un archivo del checkout, paquetes de cambio en vivo y
despliegue de export SQL nativo.
Para una lectura simple, reutiliza la identidad ya verificada en la conexión
activa; si no existe, haz una sonda mínima de identidad/destino y consulta
enseguida. No leas contenido antes de confirmar el destino. No agregues inventarios
de entorno, escaneos de privilegios ni diagnósticos de workspace sin una
ambigüedad concreta. Para una escritura solicitada, no inspecciones grants antes,
durante ni después: ejecuta la solicitud confirmada e informa la respuesta real
del servicio, incluidos los errores de privilegios. Inspecciona grants solo si el
usuario lo pide o para diagnosticar un error de acceso ya observado.

| Operación | Herramientas/ruta | Fuente de identidad y permiso |
| --- | --- | --- |
| Oracle lectura/diagnóstico | `inspect_oracle_session`, `inspect_environment`, `inspect_oracle_privileges`, `execute_readonly_query` (un SELECT inline con binds enteros), `execute_readonly_batch` (hasta 25 SELECT y 100000 caracteres en una sesión), `Execute-OracleSql.ps1 -ReadOnly` | Perfil Oracle del ambiente elegido en `.env`; grants y roles observados/efectivos en Oracle |
| Oracle DML puntual | `execute_sql_file` o `Execute-OracleSql.ps1` | Ambas rutas controladas exigen confirmación explícita y `backup_choice=yes/no`; con sí requieren SQL de backup dedicado y lo ejecutan antes. Sin backup aceptado: sin conteo previo ni bundle de rutina |
| Oracle DDL/PLSQL o cambio coordinado | `execute_sql_file`, `execute_change_bundle`, `Execute-OracleSql.ps1` o `Invoke-OracleApexChange.ps1` | Bundle solo cuando aporta fingerprint/preflight o coordina objetos; con backup=yes, `snapshot.sql` se ejecuta tras preflight y antes de apply |
| APEX lectura/contexto | `inspect_apex_context`, `inspect_environment`, `apex_get_page_details`; si el adaptador falla, `apex_run_sql` con binds sobre `APEX_APPLICATION_*` | Credencial del canal elegido; verificar el destino real y el contexto/app/workspace |
| APEX escritura/import | `deploy_apex_page`, `Deploy-ApexPage.ps1`, bundle cuando agrega fingerprint/coordinación, o herramienta APEX de escritura disponible | Las rutas controladas exigen ambas decisiones. Si backup=yes, se requiere un export nativo previo; validar sintaxis no prueba que coincida con el estado vivo exacto |

El conector determina la superficie que puede intentarse; no concede los
privilegios. La etiqueta/nombre del MCP tampoco demuestra cuál base o instancia
contestó: valida identidad y destino mediante la sesión antes de leer contenido.
Si una ruta devuelve datos antes de poder validarlos, descártalos si el destino
observado no coincide con el solicitado.

Errores como `PROFILE_MISSING`, `APEX_CONTEXT_INVALID`, `AUTHORIZATION_DENIED`
o `EXECUTION_ERROR` reflejan el estado observado de esa ruta. Si una ruta falla,
reporta el mensaje y usa otra disponible dentro de la solicitud.
La diferencia entre el usuario SQLcl y el esquema de parsing del workspace es
informativa; no prueba falta de permiso para leer las vistas públicas de
metadata. `APEX_CONTEXT_INVALID` solo debe reportarse como bloqueo cuando una
operación APEX devuelve ese error real, no por comparar nombres de usuario y
esquemas.

## Instalación y registro

```powershell
.\scripts\Setup-ApexControlledMcp.ps1
.\scripts\Register-ApexControlledMcp.ps1
```

El MCP usa los perfiles Oracle configurados por ambiente. El perfil App Builder
es independiente y solo se necesita para rutas que inician sesión con esa
cuenta. La falta de un perfil no invalida otro canal autenticado.

## Ejecución

`execute_readonly_query` acepta una sola sentencia SELECT en una línea física,
con binds enteros, directamente por SQLcl y la envía dentro de una transacción Oracle de solo
lectura. El control limita escrituras directas en esa transacción, pero Oracle
permite que ciertas funciones llamadas desde SELECT tengan efectos laterales;
por eso esta herramienta se usa para consultas de metadata conocidas, no como
sandbox para SQL arbitrario o funciones de usuario. La bitácora registra una
huella conjunta de la consulta y los binds, sin guardar sus textos/valores. Así las lecturas de
metadata no dependen de que la carpeta del proyecto sea un repositorio Git ni
de un archivo bajo el checkout del MCP. Para una revisión completa de página,
`execute_readonly_batch` acepta entre 1 y 25 SELECT de una línea con hasta
100000 caracteres totales y binds enteros compartidos. Valida todo el lote antes
de conectar, devuelve sesión/esquema/servicio por defecto y cada resultado con
su propio delimitador y ORA. Abre una única sesión y transacción de solo lectura;
un error Oracle en una consulta no detiene las restantes. Su continuación de
errores solo aplica a esta ruta; las demás llamadas a `sqlcl_result`, incluidas
las de mutación, conservan el default `whenever sqlerror exit ... rollback`.
Cada resultado requiere ambos marcadores; si falta uno devuelve
`OUTPUT_INCOMPLETE`. Los ORA dentro del bloque devuelven `ORACLE_ERROR` y los
errores `SP2-xxxx`, `SQLCL_ERROR`. Un ORA de conexión/autenticación antes del
primer marcador hace fallar el lote y todas sus consultas con
`CONNECTION_FAILED`, incluso sin identidad. El lote solo devuelve `ok=true`
cuando todas las consultas son `SUCCESS` y la identidad solicitada está
presente. Si falla la bitácora, conserva los resultados y devuelve
`audit_persisted=false` junto con un aviso.
La bitácora registra un digest por consulta, el código/ORA de cada resultado y
tiempos, sin SQL, binds ni datos devueltos. Usa las consultas comprobadas de
`skills/apex-database-diagnostics/references/page-snapshot-queries.md` para una
página. `execute_sql_file` ejecuta artefactos DDL/DML/PLSQL desde el checkout. Si el proyecto del usuario no pertenece a ese
checkout, crea el `.sql` temporal dentro del checkout del conector (por ejemplo,
`.codex-tmp/<nombre>.sql`) y pasa una ruta relativa a ese checkout. El servidor
rechaza archivos fuera de su raíz, incluidos archivos del proyecto y rutas
absolutas. Para una consulta puntual, usa `execute_readonly_query`; si se usa el helper
PowerShell, añade `-ReadOnly`, que acepta solo un SELECT y configura la
transacción como read-only. Para una mutación por PowerShell, proporciona la
confirmación y elección de backup requeridas; con backup=yes incluye un archivo
de backup dedicado. Un `ORA-20987` de
`inspect_apex_context` informa que falló esa comprobación de contexto; no
sustituye el resultado de una consulta directa de solo lectura a las vistas
públicas `APEX_APPLICATION_*`. Informa el resultado real de la consulta e
intenta otra ruta configurada para el mismo ambiente cuando sea necesario.

Una solicitud para revisar o mostrar datos/especificaciones es read-only: tras
una única comprobación del destino si se necesita, consulta el objeto
inmediatamente. No ejecutes validaciones, QA, inventarios, conteos previos ni
flujos de cambio como preflight rutinario. Antes de una mutación, solicita una
sola confirmación que identifique ambiente, objeto, operación exacta y si el
usuario quiere backup. Las rutas controladas requieren `confirmed` y
`backup_choice=yes/no`; esto bloquea campos ausentes, aunque no autentica
criptográficamente quién respondió. Si responde no, no crees backup. Si
responde sí, ejecuta el artefacto de backup aceptado primero y detente si falta
o falla. No exijas conteo previo para INSERT, UPDATE, DELETE, MERGE u otra
transacción. Ejecuta DML puntual directamente y conserva el evento de auditoría
normal. Usa bundle solo si un
cambio existente requiere comparación de fingerprint o varias operaciones
coordinadas lo justifican.

Los ejecutores controlados MCP y los scripts PowerShell
`Execute-OracleSql.ps1`, `Deploy-ApexPage.ps1` e
`Invoke-OracleApexChange.ps1` registran los intentos de ejecución en
`control-proyecto/.bitacora.json` como JSON Lines. Cada operación de escritura
registra eventos de inicio y resultado correlacionados por ID, con ambiente,
operación, origen y hash, resultado, código de salida, duración y decisión de
backup; los bundles añaden hashes de artefactos. Las consultas inline de solo
lectura y `Execute-OracleSql.ps1 -ReadOnly` registran un único evento con hash
después de obtener el resultado y no requieren una escritura previa de auditoría.
Si falla el registro posterior de una lectura, se conserva y devuelve el
resultado de la consulta junto con una advertencia. No se guardan SQL, credenciales,
cadenas de conexión ni salida del servidor. Si no se puede guardar el evento
inicial de una escritura, el adaptador bloquea la ejecución. Si falla el registro
final después de SQLcl, informa que la operación pudo haberse aplicado y que no
debe repetirse automáticamente.
El archivo está ignorado por Git y es local: los adaptadores lo usan de forma
append-only, pero no es inmutable ni a prueba de manipulación. El script
`.hooks/pre-commit.sh` también puede añadir metadatos de archivos staged al mismo
JSONL; no se instala con `pre-commit install` mientras no esté configurado como
hook en `.pre-commit-config.yaml`.

Las consultas y ejecuciones SQL directas devuelven y registran `profile_load`,
`sqlcl_process` y `route_total` en milisegundos. No ejecutan `sqlcl -version`
como prevalidación repetida; `doctor()` conserva esa comprobación cuando se
solicita explícitamente. Si SQLcl no puede arrancar, la ruta devuelve el error
observado por el propio intento. `sqlcl_process` incluye arranque de SQLcl,
conexión, envío de SQL y respuesta del servidor; no es una medida aislada del
tiempo interno de Oracle. Para bundles, los
`phase_durations_ms` provienen de marcadores ejecutados en Oracle, mientras
`elapsed_ms` cubre los procesos SQLcl de preflight y apply/verify.

Para inventariar objetos de una página, verifica primero el destino real del
MCP APEX con una consulta de identidad de solo lectura. Si coincide con el
ambiente solicitado, consulta `APEX_APPLICATION_PAGE_REGIONS` y las vistas de
procesos, items, acciones dinámicas, validaciones y botones con IDs enlazados.
Si `apex_get_page_details` devuelve una columna inválida, usa esta lectura
directa de vistas públicas; no abandones el diagnóstico ni cambies a otro
ambiente.

## Paquetes de cambio

`execute_change_bundle` recibe un `change.json` dentro del checkout. Úsalo
cuando una huella o coordinación entre objetos aporte una protección concreta,
no para una lectura o DML puntual. Valida sus rutas y ejecuta preflight,
comprueba su marcador de fingerprint y solo entonces ejecuta apply y verify en
una secuencia acotada de SQLcl; registra hashes, duración y resultado sin
guardar SQL ni secretos. `snapshot.sql` solo se ejecuta cuando el usuario acepta
backup, después del preflight y antes de apply; si falta o falla, apply no
corre. Si `backup_choice=no`, `change.json` no puede declarar `snapshot`.
`rollback.sql` es opcional; si se declara debe estar dentro del checkout,
pero no es una fase automática ni prueba que la reversión sea segura.
