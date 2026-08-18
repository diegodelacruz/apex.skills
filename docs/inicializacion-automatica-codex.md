# Inicializador de proyectos APEX para Codex Desktop

Use este inicializador cuando Codex indique que no tiene conexión Oracle, servidor MCP o herramientas de base de datos. Una skill no abre una conexión por sí misma: el entorno Python, el perfil seguro y `apex-mcp-test` deben estar preparados en el equipo.

## Primera instalación: copie sólo estos comandos

Reemplace los marcadores por rutas absolutas:

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

El inicializador muestra cinco pasos y realiza automáticamente lo posible sin pedir secretos:

1. Crea el entorno Python compartido e instala las dependencias.
2. Aplica el patch canónico para que `apex-mcp` acepte conexión Oracle directa; wallet queda opcional.
3. Importa TEST desde `.env` si el perfil seguro aún no existe y descubre los metadatos APEX mediante consultas de lectura.
4. Registra `apex-mcp-test` en Codex Desktop sólo si aún no está registrado.
5. Confirma que el proyecto está listo.

No escriba usuario, contraseña, wallet, workspace ID, parsing schema ni workspace name. La conexión directa usa las variables `DB_TESTING_*` del `.env` y no requiere wallet. Abra una **tarea nueva** de Codex Desktop dentro del proyecto al terminar.

## Cada proyecto posterior

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>"
```

El resultado correcto incluye:

```text
[2/5] Applying direct Oracle connection compatibility...
      [OK] Direct connection supported; wallet is optional.
[3/5] Checking secure TEST profile...
      [OK] TEST profile ready.
[4/5] Checking Codex MCP registration...
      [OK] apex-mcp-test available.
```

`Unsupported` en la columna `Auth` de `codex mcp list` no es un error: el servidor local usa `stdio`, no OAuth.

## Si falla

| Mensaje | Acción |
| --- | --- |
| `Shared runtime missing` | Ejecute con `-InstallSharedDependencies`. |
| `Required APEX MCP integration scripts are missing` | Actualice el repositorio de skills y vuelva a ejecutar. |
| `Could not import the TEST profile` | Revise las variables TEST del `.env` o los permisos APEX, sin compartir secretos. |
| MCP no aparece en la tarea | Abra una tarea nueva de Codex Desktop. |
| Error ACL del terminal | Complete el inicializador, abra una tarea nueva y use MCP. |

## Prompt posterior

```text
Usa la skill apex-database-diagnostics y el servidor apex-mcp-test.
Analiza este error en modo sólo lectura. No ejecutes cambios; entrega evidencia,
causa probable, plan de corrección, validación TEST y rollback.
```

Para casos que deban comparar ambos ambientes, consulte [casos de uso](casos-de-uso-apex.md). Producción se importa y registra sólo para usuarios autorizados y únicamente en lectura. APEX 24.1.3 mantiene el upstream 24.2 en modo inspección/dry-run hasta aprobar compatibilidad en TEST.
