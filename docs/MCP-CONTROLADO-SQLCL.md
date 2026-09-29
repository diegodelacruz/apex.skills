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
ejecución SQL desde un archivo del checkout y despliegue de export SQL nativo.
Para una lectura simple, reutiliza la identidad ya verificada en la conexión
activa; si no existe, haz una sonda mínima de identidad/destino y consulta
enseguida. No leas contenido antes de confirmar el destino. No agregues inventarios
de entorno, escaneos de privilegios ni diagnósticos de workspace sin una
ambigüedad concreta. En tareas de escritura, la inspección de privilegios puede
aportar contexto, pero no reemplaza la respuesta real del servidor.

| Operación | Herramientas/ruta | Fuente de identidad y permiso |
| --- | --- | --- |
| Oracle lectura/diagnóstico | `inspect_oracle_session`, `inspect_environment`, `inspect_oracle_privileges`, `execute_readonly_query` (SELECT inline con binds enteros) | Perfil Oracle del ambiente elegido en `.env`; grants y roles observados/efectivos en Oracle |
| Oracle DDL/DML/PLSQL | `execute_sql_file` o SQLcl (`Execute-OracleSql.ps1`) | Mismo perfil seleccionado; Oracle aplica los permisos otorgados |
| APEX lectura/contexto | `inspect_apex_context`, `inspect_environment`, `apex_get_page_details`; si el adaptador falla, `apex_run_sql` con binds sobre `APEX_APPLICATION_*` | Credencial del canal elegido; verificar el destino real y el contexto/app/workspace |
| APEX escritura/import | `deploy_apex_page` o herramienta APEX de escritura disponible | Credencial del ambiente configurado; permisos efectivos decididos por Oracle/APEX al ejecutar |

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
con binds enteros,
directamente por SQLcl y la envía dentro de una transacción Oracle de solo
lectura. El control limita escrituras directas en esa transacción, pero Oracle
permite que ciertas funciones llamadas desde SELECT tengan efectos laterales;
por eso esta herramienta se usa para consultas de metadata conocidas, no como
sandbox para SQL arbitrario o funciones de usuario. La bitácora registra una
huella conjunta de la consulta y los binds, sin guardar sus textos/valores. Así las lecturas de
metadata no dependen de que la carpeta del proyecto sea un repositorio Git ni
de un archivo bajo el checkout del MCP. `execute_sql_file` ejecuta artefactos
DDL/DML/PLSQL desde el checkout. Si el proyecto del usuario no pertenece a ese
checkout, crea el `.sql` temporal dentro del checkout del conector (por ejemplo,
`.codex-tmp/<nombre>.sql`) y pasa una ruta relativa a ese checkout. El servidor
rechaza archivos fuera de su raíz, incluidos archivos del proyecto y rutas
absolutas. Para una lectura, usa `execute_readonly_query`; para otro SQL, usa
`apex_run_sql` en el MCP APEX verificado para el mismo ambiente o
`scripts/Execute-OracleSql.ps1 -Sql/-SqlFile` si está inicializada. Un `ORA-20987` de
`inspect_apex_context` informa que falló esa comprobación de contexto; no
sustituye el resultado de una consulta directa de solo lectura a las vistas
públicas `APEX_APPLICATION_*`. Informa el resultado real de la consulta e
intenta otra ruta configurada para el mismo ambiente cuando sea necesario.

Para inventariar objetos de una página, verifica primero el destino real del
MCP APEX con una consulta de identidad de solo lectura. Si coincide con el
ambiente solicitado, consulta `APEX_APPLICATION_PAGE_REGIONS` y las vistas de
procesos, items, acciones dinámicas, validaciones y botones con IDs enlazados.
Si `apex_get_page_details` devuelve una columna inválida, usa esta lectura
directa de vistas públicas; no abandones el diagnóstico ni cambies a otro
ambiente.
