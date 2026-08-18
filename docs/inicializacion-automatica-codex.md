# Inicializador de proyectos APEX para Codex Desktop

Esta guía resuelve el caso en que Codex responde que no tiene conexión Oracle, servidor MCP o herramientas de base de datos. Una skill no abre una conexión por sí misma: describe el procedimiento que el agente debe seguir. El servidor `apex-mcp-test`, su entorno Python y el perfil seguro deben estar configurados primero en el equipo del usuario.

## Qué se ejecuta una vez y qué se ejecuta por proyecto

| Recurso | Cuándo se prepara | Dónde queda |
| --- | --- | --- |
| Upstreams, `.venv` compartido y paquetes Python | Una vez por usuario/equipo; actualizar sólo cuando se solicite | Repositorio `apex.skills` |
| Perfil TEST y, si aplica, Producción | Una vez por usuario autorizado; se reemplaza sólo al cambiar credenciales | Keyring seguro del sistema |
| `apex-mcp-test` | Una vez por usuario/equipo; el inicializador lo verifica en cada proyecto | Configuración de Codex Desktop |
| `control-proyecto/`, decisiones y plan | En cada proyecto APEX | Raíz del proyecto |
| Dependencias particulares de una aplicación | Sólo cuando esa aplicación las requiere | Entorno local de esa aplicación |

## Primera instalación en un equipo

Abra PowerShell en el repositorio de skills. Copie estos comandos, reemplazando únicamente la ruta del proyecto APEX:

```powershell
cd "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "D:\ruta\mi-proyecto-apex" -InstallSharedDependencies
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py set --environment test
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py validate --environment test
codex mcp list
```

El tercer comando crea el entorno compartido, instala dependencias y registra `apex-mcp-test` en Codex Desktop sólo si aún no existe. El asistente solicitará los datos de TEST localmente y los guarda en el keyring del sistema. No pegue contraseñas, wallets ni DSN en el chat, archivos `.env`, JSON, scripts o repositorios.

Al terminar, abra una **tarea nueva** en Codex Desktop dentro de `D:\ruta\mi-proyecto-apex`. Una tarea que ya estaba abierta no incorpora el nuevo MCP.

## Inicio de cada proyecto APEX posterior

No reinstale paquetes ni vuelva a crear el perfil. Desde el repositorio de skills copie:

```powershell
cd "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills"
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "D:\ruta\mi-proyecto-apex"
```

El inicializador verifica el entorno compartido y `apex-mcp-test`; no duplica el servidor, no muestra secretos ni reemplaza perfiles. La skill `apex-project-bootstrap-final` debe hacer esta misma comprobación al iniciar el trabajo.

## Diagnóstico rápido

| Mensaje o síntoma | Causa probable | Acción exacta |
| --- | --- | --- |
| “No hay conexión Oracle”, “no hay conector” o no aparece `apex-mcp-test` | El MCP no fue registrado en Codex Desktop | Ejecute la sección **Primera instalación** y abra una tarea nueva. |
| `Shared runtime missing` | No existe `.venv` compartido | Ejecute el comando con `-InstallSharedDependencies`. |
| `Missing secure profile: test` | El perfil TEST no está guardado para este usuario de Windows | Ejecute `manage_apex_credentials.py set --environment test` y luego `validate`. |
| `apex-mcp-test` aparece en `codex mcp list`, pero la tarea no lo tiene | La tarea se abrió antes del registro del servidor | Cierre esa tarea y abra una nueva en Codex Desktop. |
| Error interno de ACL del terminal | Es una limitación de acceso del terminal/sandbox, no una prueba de que Oracle esté caído | Confirme `codex mcp list`, abra una tarea nueva y solicite diagnóstico mediante MCP. Si el MCP tampoco aparece, ejecute la primera instalación. |
| La validación del perfil falla | DSN, wallet, credenciales o permisos del usuario no son válidos | Corrija el perfil local con `set`; no cambie ni pruebe la base de datos mediante scripts de despliegue. |

## Prompt de uso posterior

Cuando la nueva tarea muestre el servidor, use este texto:

```text
Usa la skill apex-database-diagnostics y el servidor apex-mcp-test.
Analiza este error en modo sólo lectura. Identifica ambiente, aplicación,
página, componentes y objetos DATA afectados. No ejecutes cambios; entrega
evidencia, causa probable, plan de corrección, validación TEST y rollback.
```

## Producción

Producción no se configura por defecto. Sólo un usuario autorizado puede crear y validar el perfil `production`; se usa exclusivamente para diagnósticos de lectura. El upstream `apex-mcp` es 24.2 y el objetivo es APEX 24.1.3, por lo que se limita a inspección/dry-run hasta aprobar compatibilidad en TEST.

No hay un evento seguro para ejecutar comandos al sólo abrir una carpeta en Codex Desktop. La automatización canónica es ejecutar este inicializador por el primer agente o usuario de cada proyecto, respetando las aprobaciones para instalaciones.
