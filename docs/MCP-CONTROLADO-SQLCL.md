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
APEX, privilegios, ejecución SQL desde un archivo del checkout y despliegue de
export SQL nativo. Al iniciar, usa las sondas de solo lectura para identificar
la cuenta y el destino seleccionado e inspecciona privilegios de sesión cuando
estén disponibles. La consulta no es una autorización ni sustituye la respuesta
real del servidor ante la operación solicitada.

| Operación | Herramientas/ruta | Fuente de identidad y permiso |
| --- | --- | --- |
| Oracle lectura/diagnóstico | `inspect_oracle_session`, `inspect_environment`, `inspect_oracle_privileges`, `execute_sql_file` con consulta de lectura | Perfil Oracle del ambiente elegido en `.env`; grants y roles observados/efectivos en Oracle |
| Oracle DDL/DML/PLSQL | `execute_sql_file` o SQLcl (`Execute-OracleSql.ps1`) | Mismo perfil seleccionado; Oracle aplica los permisos otorgados |
| APEX lectura/contexto | `inspect_apex_context`, `inspect_environment`, `apex_get_page_details`; si el adaptador falla, `apex_run_sql` con binds sobre `APEX_APPLICATION_*` | Credencial del canal elegido; verificar el destino real y el contexto/app/workspace |
| APEX escritura/import | `deploy_apex_page` o herramienta APEX de escritura disponible | Credencial del ambiente configurado; permisos efectivos decididos por Oracle/APEX al ejecutar |

El conector determina la superficie que puede intentarse; no concede los
privilegios. La etiqueta/nombre del MCP tampoco demuestra cuál base o instancia
contestó: valida identidad y destino mediante la sesión cuando sea posible.

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

`execute_sql_file` ejecuta archivos SQL del checkout con la credencial Oracle
del ambiente elegido. Si el proyecto del usuario no pertenece a ese checkout,
crea el `.sql` temporal dentro del checkout del conector, o usa
`scripts/Execute-OracleSql.ps1 -Sql/-SqlFile` cuando esté disponible; no detengas
la consulta por la ubicación del proyecto. Usa la ruta nativa APEX para imports
cuando corresponda. No solicites confirmación separada para una operación ya
pedida. Informa errores observados y prueba otra ruta configurada para el mismo
ambiente cuando la primera ruta falle.

Para inventariar objetos de una página, verifica primero el destino real del
MCP APEX con una consulta de identidad de solo lectura. Si coincide con el
ambiente solicitado, consulta `APEX_APPLICATION_PAGE_REGIONS` y las vistas de
procesos, items, acciones dinámicas, validaciones y botones con IDs enlazados.
Si `apex_get_page_details` devuelve una columna inválida, usa esta lectura
directa de vistas públicas; no abandones el diagnóstico ni cambies a otro
ambiente.
