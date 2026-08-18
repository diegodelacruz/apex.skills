# Manual de uso — APEX Skills

Este es el punto de entrada para usar las skills de Oracle APEX con Codex Desktop. No contiene secretos ni datos de un proyecto particular.

## 1. Preparar el equipo una sola vez

Abra PowerShell y reemplace los marcadores por rutas absolutas:

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

El inicializador prepara dependencias, habilita conexión Oracle directa sin wallet cuando corresponda, importa TEST desde el `.env` local si hace falta y registra `apex-mcp-test` en Codex Desktop.

Abra una tarea **nueva** de Codex Desktop dentro del proyecto APEX al terminar.

## 2. Empezar cada proyecto APEX

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>"
```

Después pida al agente:

```text
Usa apex-project-bootstrap-final para iniciar este proyecto APEX.
```

El agente crea `control-proyecto/`, decisiones y plan antes de desarrollar.

## 3. Diagnosticar un error sin hacer cambios

Para TEST:

```text
Usa apex-database-diagnostics y apex-mcp-test.
Analiza este error sólo en lectura. No ejecutes cambios; entrega evidencia,
causa, plan TEST, validación y rollback.
```

Cuando el error pueda depender de versión o configuración, use ambos ambientes autorizados:

```text
Usa apex-database-diagnostics, apex-mcp-test y apex-mcp-production.
Compara ambos ambientes sólo en lectura y genera la evidencia de diferencias.
No ejecutes cambios.
```

## 4. Modificar una página existente

Antes de editar, el agente debe comparar TEST y Producción, registrar `environment-diff.md`, proponer sincronización si procede y esperar autorización para cualquier operación fuera de TEST.

## 5. Documentación de consulta

| Necesidad | Documento |
| --- | --- |
| Instalación, mensajes y solución de problemas | [Inicialización Codex](docs/inicializacion-automatica-codex.md) |
| Perfiles seguros TEST/Producción | [Perfiles seguros](docs/perfiles-credenciales-seguros.md) |
| Registro MCP en Codex Desktop | [Oracle MCP](docs/codex-desktop-mcp-oracle.md) |
| Flujos reutilizables y comparación de ambientes | [Casos de uso](docs/casos-de-uso-apex.md) |
| Reglas de estructuras y entregables por proyecto | [Estructura estándar](docs/estructura-estandar-proyecto.md) |
| Auditoría obligatoria | [Auditoría](docs/auditoria-obligatoria.md) |

## 6. Cierre obligatorio

Antes de informar que un cambio está terminado, ejecute:

```powershell
python .\scripts\audit_skill_ecosystem.py
git diff --check
```

El manual detallado de cada aplicación se genera al cierre, después de QA aprobada y evidencia validada.
