# Inicializador de proyectos APEX para Codex Desktop

Use este inicializador cuando Codex indique que no tiene conexión Oracle, servidor MCP o herramientas de base de datos. Una skill no abre una conexión por sí misma: el entorno Python, el perfil seguro y `apex-mcp-test` deben estar disponibles en el equipo.

## Primera instalación: copie sólo estos comandos

Reemplace únicamente la ruta del proyecto APEX:

```powershell
cd "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "D:\ruta\mi-proyecto-apex" -InstallSharedDependencies
```

El inicializador muestra cuatro pasos breves y realiza automáticamente lo que pueda hacer sin pedirle secretos:

1. Crea el entorno Python compartido e instala las dependencias.
2. Importa TEST desde el `.env` ignorado sólo si el perfil seguro aún no existe; construye el DSN y descubre workspace ID, workspace name y parsing schema con consultas de lectura.
3. Registra `apex-mcp-test` en Codex Desktop sólo si aún no está registrado.
4. Confirma que el proyecto está listo.

No escriba usuario, contraseña, wallet, workspace ID, parsing schema ni workspace name. La conexión directa existente usa `DB_TESTING_USER`, `DB_TESTING_PASSWORD`, `DB_TESTING_HOST`, `DB_TESTING_PORT` y `DB_TESTING_SID` del `.env`; no requiere wallet.

Después abra una **tarea nueva** de Codex Desktop dentro de `D:\ruta\mi-proyecto-apex`. Una tarea anterior no adquiere MCPs nuevos.

## Cada proyecto posterior

No reinstale paquetes ni cree perfiles otra vez. Copie:

```powershell
cd "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills"
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "D:\ruta\mi-proyecto-apex"
```

## Resultado esperado

```text
APEX Codex Bootstrap
--------------------
[2/4] Checking secure TEST profile...
      [OK] TEST profile ready.
[3/4] Checking Codex MCP registration...
      [OK] apex-mcp-test available.
[4/4] Project readiness...
      [OK] D:\ruta\mi-proyecto-apex
```

`Unsupported` en la columna `Auth` de `codex mcp list` no es un error: este servidor MCP local usa `stdio`, no autenticación OAuth.

## Si falla

| Mensaje | Acción |
| --- | --- |
| `Shared runtime missing` | Ejecute con `-InstallSharedDependencies`. |
| No local `.env` file was found | Copie el `.env` seguro al repositorio de skills; no lo suba a Git. |
| Could not import the TEST profile | Revise las variables TEST del `.env` o los permisos APEX, sin compartir secretos. |
| MCP no aparece en la tarea | Abra una tarea nueva de Codex Desktop. |
| Error ACL del terminal | Confirme que el inicializador termine con `[OK] apex-mcp-test available`, abra una tarea nueva y use el MCP. |

## Prompt posterior

```text
Usa la skill apex-database-diagnostics y el servidor apex-mcp-test.
Analiza este error en modo sólo lectura. No ejecutes cambios; entrega evidencia,
causa probable, plan de corrección, validación TEST y rollback.
```

Producción se importa y registra sólo para usuarios autorizados y únicamente en lectura. APEX 24.1.3 mantiene el upstream 24.2 en modo inspección/dry-run hasta aprobar compatibilidad en TEST.
