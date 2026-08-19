# Inicializador de proyectos APEX para Codex

Use este inicializador cuando Codex indique que no tiene conexión Oracle, servidor MCP o herramientas de base de datos. Una skill no abre una conexión por sí misma: el entorno Python, el perfil seguro, las skills locales y `apex-mcp-test` deben estar preparados en el equipo.

## Primera instalación: copie sólo estos comandos

Reemplace los marcadores por rutas absolutas:

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

El inicializador muestra siete pasos y realiza automáticamente lo posible sin pedir secretos:

1. Crea el entorno Python compartido e instala las dependencias.
2. Aplica el patch canónico para que `apex-mcp` acepte conexión Oracle directa; wallet queda opcional.
3. Importa TEST desde `.env` si el perfil seguro aún no existe y descubre los metadatos APEX mediante consultas de lectura.
4. Ejecuta un mensaje MCP `initialize` local y exige la respuesta correcta del servidor antes de continuar.
5. Instala o verifica enlaces de todas las skills del repositorio en el directorio de usuario de Codex CLI.
6. Registra `apex-mcp-test` en Codex sólo si aún no está registrado.
7. Confirma que el proyecto está listo.

No escriba usuario, contraseña, wallet, workspace ID, parsing schema ni workspace name. La conexión directa usa las variables `DB_TESTING_*` del `.env` y no requiere wallet. Abra una **tarea nueva** de Codex Desktop o una sesión nueva de Codex CLI dentro del proyecto al terminar.

## Cada proyecto posterior

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>"
```

El resultado correcto incluye:

```text
[2/7] Applying direct Oracle connection compatibility...
      [OK] Direct connection supported; wallet is optional.
[3/7] Checking secure TEST profile...
      [OK] TEST profile ready.
[4/7] Validating TEST MCP handshake...
      [OK] TEST MCP initialize response received.
[5/7] Installing skills for Codex CLI...
      [OK] APEX coordinator and specialist skills are available.
[6/7] Checking Codex MCP registration...
      [OK] apex-mcp-test available.
```

`Unsupported` en la columna `Auth` de `codex mcp list` no es un error: el servidor local usa `stdio`, no OAuth. Ese listado valida el registro; el paso 4 valida que el servidor realmente responde al protocolo MCP y el paso 5 permite que Codex seleccione las skills por contexto.

## Si falla

| Mensaje | Acción |
| --- | --- |
| `Shared runtime missing` | Ejecute con `-InstallSharedDependencies`. |
| `Required APEX MCP integration scripts are missing` | Actualice el repositorio de skills y vuelva a ejecutar. |
| `Could not import the TEST profile` | Revise las variables TEST del `.env` o los permisos APEX, sin compartir secretos. |
| `APEX_MCP_HANDSHAKE_FAIL` | Ejecute `git pull`, repita el inicializador y abra una sesión nueva de Codex. Si persiste, conserve el mensaje sin incluir secretos. |
| `MCP startup failed ... initialize response` | Actualice el repositorio, ejecute el inicializador y reinicie la tarea/sesión. Esta versión evita el cierre de `os.execvpe` en Windows. |
| `Could not install APEX skills for Codex CLI` | Revise las rutas en `%USERPROFILE%\.codex\skills`; no use `-Force` hasta revisar cualquier skill existente con el mismo nombre. |
| MCP no aparece en la tarea | Abra una tarea nueva de Codex Desktop o una sesión nueva de Codex CLI. |
| Error ACL del terminal | Complete el inicializador, abra una tarea nueva y use MCP. |

## Prompt posterior

```text
Revisa en producción el paquete data.pk_ejemplo en modo solo lectura.
Ejecuta las consultas necesarias mediante MCP; no me pidas resultados ni ejecutes cambios.
```

Para casos que deban comparar ambos ambientes, consulte [casos de uso](casos-de-uso-apex.md). Producción se importa y registra sólo para usuarios autorizados y únicamente en lectura. APEX 24.1.3 mantiene el upstream 24.2 en modo inspección/dry-run hasta aprobar compatibilidad en TEST.
