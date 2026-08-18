# Inicialización automática para un proyecto APEX en Codex Desktop

No debe repetir la instalación en cada proyecto. Los recursos se separan así:

| Recurso | Frecuencia | Ubicación |
| --- | --- | --- |
| Upstreams, `.venv` compartido y perfil TEST | Una vez por usuario/equipo; se actualizan cuando se solicite | Repositorio `apex.skills` y keyring del sistema |
| `apex-mcp-test` | Una vez por usuario/equipo | Configuración de Codex Desktop |
| `control-proyecto/`, decisiones y plan | Una vez por proyecto | Raíz del proyecto APEX |
| Dependencias propias de la aplicación | Sólo si el proyecto las necesita | Entorno local del proyecto |

Al comenzar un proyecto, el agente debe usar la skill `apex-project-bootstrap-final`. Para verificar y completar el registro del MCP de forma idempotente, ejecute desde el repositorio de skills:

```powershell
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "D:\ruta\mi-nuevo-proyecto"
```

El comando no vuelve a registrar `apex-mcp-test` si ya existe y no lee ni sobrescribe credenciales. Si el entorno compartido todavía no existe, instale las dependencias explícitamente:

```powershell
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "D:\ruta\mi-nuevo-proyecto" -InstallSharedDependencies
```

La instalación descarga paquetes y debe seguir la política de aprobación del usuario. El registro es global a Codex Desktop, pero cada tarea debe abrirse después de que el MCP esté registrado; una tarea ya iniciada no incorpora herramientas nuevas.

No existe un evento seguro para ejecutar comandos automáticamente sólo por abrir una carpeta en Codex Desktop. La automatización canónica es que el primer agente ejecute este inicializador al comenzar el proyecto, respetando las aprobaciones, o que el usuario lo ejecute una vez antes de abrir la tarea.
