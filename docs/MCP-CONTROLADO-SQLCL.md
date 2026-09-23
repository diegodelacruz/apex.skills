# MCP controlado con SQLcl administrado

## Decisión

El repositorio incorpora `apex-controlled-mcp`, un servidor MCP local por
STDIO que utiliza SQLcl administrado por el usuario. No registra ni carga el
upstream `apex-mcp` completo.

La necesidad es ofrecer una conexión Oracle/APEX repetible, con diagnóstico y
mensajes estructurados, sin depender de VS Code ni de instalaciones manuales
de SQLcl. La cuenta Oracle conserva como fuente de verdad sus privilegios
efectivos; el MCP no concede ni simula permisos.

## Runtime y seguridad

`scripts/Install-ApexControlledRuntime.ps1` instala bajo
`%LOCALAPPDATA%\ApexSkills\runtimes`, fuera de Git y sin modificar PATH:

| Componente | Fuente | Integridad | Uso |
| --- | --- | --- | --- |
| SQLcl 26.2.2.233.1901 | Oracle | SHA-1 publicado por Oracle | Ejecución Oracle/APEX |
| Temurin Java 21 | API oficial Adoptium | SHA-256 publicado por Adoptium | Runtime local de SQLcl |

La comprobación SHA-1 de SQLcl es el checksum de mayor fuerza publicado por
Oracle para esa versión. Si Oracle publica SHA-256, el manifiesto debe
actualizarse antes de cambiar versión. El bootstrap extrae a staging, verifica
antes de instalar y deja un `runtime-state.json` sin secretos.

## Herramientas expuestas

El servidor expone diagnóstico local, consulta de identidad Oracle y ejecución
de artefactos SQL versionados. No expone DML directo a `WWV_FLOW_*`, paquetes
internos APEX, SQL en línea ni credenciales. Los cambios se envían en archivos
SQL dentro del repositorio y se registran con huella SHA-256, ambiente y código
de salida, sin contenido SQL ni secretos.

Para una aplicación existente, el MCP obtiene dinámicamente su workspace y
esquema de parsing desde el `application_id` solicitado; no contiene una
allowlist codificada para una aplicación concreta. Al iniciar el trabajo en un
ambiente puede inventariar sus workspaces, esquemas y aplicaciones, sin imponer
esa lectura como bloqueo previo de cada operación. La creación de una aplicación nueva requerirá una herramienta separada
para importar un export nativo completo y un preflight contra el workspace
destino; no se debe simular como una página aislada.

`doctor` no se conecta a Oracle. Las demás herramientas informan
`RUNTIME_NOT_INSTALLED`, `PROFILE_MISSING`, `AUTHORIZATION_DENIED` o
`EXECUTION_ERROR` según evidencia observada.

## Instalación y rollback

```powershell
.\scripts\Setup-ApexControlledMcp.ps1
```

El setup autónomo crea `.venv`, instala FastMCP como dependencia directa y
después invoca `Install-ApexControlledRuntime.ps1`. No ejecuta el bootstrap de
upstreams, no usa VS Code y no necesita una instalación SQLcl o Java previa.

El runtime es per-user y eliminable borrando únicamente
`%LOCALAPPDATA%\ApexSkills\runtimes`. No se toca la instalación de Oracle,
VS Code, PATH ni el registro de Windows.

Antes de registrar el MCP se ejecutan pruebas unitarias, `doctor` y una sonda
de solo lectura en TEST. Producción requiere selección explícita de ambiente y
no se activa mediante el bootstrap.

Cuando el runtime esté listo, registre únicamente esta fachada:

```powershell
.\scripts\Register-ApexControlledMcp.ps1
```

El registro deja a Codex iniciar el servidor STDIO con la `.venv` del
repositorio. Las herramientas de escritura se marcan como tales, por lo que el
cliente puede aplicar su política de confirmación antes de invocarlas. En
particular, `execute_sql_file` ejecuta cualquier archivo `.sql` dentro del
checkout usando la conexión y los privilegios Oracle del ambiente seleccionado,
incluso producción si se solicita expresamente. La marca MCP es informativa y
no fuerza una aprobación: el agente/cliente debe mostrar el archivo y obtener
confirmación explícita del usuario antes de invocar la herramienta. Oracle
limita las operaciones según los permisos de esa cuenta. No coloque
credenciales ni SQL no revisado en el repositorio.

## Guía para un nuevo usuario

Cada persona configura su propio `.env`, runtime y registro MCP. No debe copiar
credenciales de otro usuario ni instalar SQLcl o Java globalmente.

1. Cree un `.env` local con los campos `DB_TESTING_*` y, cuando corresponda,
   `DB_PRODUCTION_*`. Las variables `APEX_*` corresponden a App Builder y se
   mantienen separadas de las credenciales Oracle. Nunca se versiona `.env`.
2. Ejecute `.\scripts\Setup-ApexControlledMcp.ps1` y luego
   `.\scripts\Register-ApexControlledMcp.ps1`.
3. Reinicie Codex para que cargue el registro actualizado.
4. Solicite al DBA la asociación de la cuenta Oracle usada por SQLcl con cada
   workspace APEX que se vaya a automatizar. Use la plantilla en
   [Solicitud de contexto APEX para SQLcl](SOLICITUD-CONTEXTO-APEX-SQLCL.md).
5. Solicite al agente el estado inicial de TEST. El MCP inventaría los
   workspaces/esquemas configurados y muestra alertas sin pedir consultas
   manuales al usuario.
6. Pida la operación APEX en TEST. El MCP la ejecuta directamente; si Oracle o
   APEX la rechazan, devuelve el código y mensaje observados.
7. Solo después de una operación TEST comprobada se solicita el mismo contexto
   para Production y se trabaja allí cuando se indique explícitamente.

Para objetos Oracle ordinarios, una petición sin esquema se interpreta como
`DATA.<objeto>`. Para trabajar en otro esquema, el usuario debe indicarlo de
forma explícita, por ejemplo `DDELACRUZ.<objeto>`.

## Inventario inicial y mensajes esperados

Al iniciar una tarea en un ambiente, `inspect_environment` obtiene la sesión
SQLcl, base/contenedor, workspaces de negocio, esquemas asociados y número de
aplicaciones por workspace. Excluye únicamente los workspaces internos de
Oracle. El inventario se construye desde los metadatos reales, por lo que admite
esquemas nuevos sin modificar el MCP. Es informativo: no impide una
operación posterior ni se repite por cada petición.

| Resultado | Significado | Acción del usuario |
| --- | --- | --- |
| `ENVIRONMENT_READY` | Se inventariaron las capacidades del ambiente. | Revise alertas iniciales y continúe. |
| `SUCCESS` | Oracle/APEX completó la operación solicitada. | Continúe con el trabajo. |
| `APEX_CONTEXT_INVALID` | APEX rechazó la operación por workspace o Security Group. | Entregue al DBA el error observado; la operación no se completó. |
| `AUTHORIZATION_DENIED` | Oracle devolvió falta de privilegio para la operación concreta. | Solicite solo el privilegio, objeto y ambiente indicados por el error. |
| `PROFILE_MISSING` | Faltan valores Oracle locales. | Complete el `.env` local sin compartir secretos. |
| `RUNTIME_NOT_INSTALLED` | Falta el runtime administrado. | Ejecute el setup autónomo. |

La ejecución usa los permisos reales de la conexión para el ambiente elegido.
Si existen, se realiza la operación; si faltan, se devuelve el error real. La
creación de una aplicación completa requiere un export APEX completo y una
herramienta dedicada; no se trata como una página aislada.
