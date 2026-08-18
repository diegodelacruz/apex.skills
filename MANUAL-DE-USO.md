# Manual de uso — APEX Skills

Este es el punto de entrada para usar las skills de Oracle APEX con Codex Desktop. No contiene secretos ni datos de un proyecto particular.

## 1. Preparar el equipo una sola vez

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

El inicializador prepara dependencias, habilita conexión Oracle directa sin wallet cuando corresponda, importa TEST desde el `.env` local si hace falta y registra `apex-mcp-test`.

## 2. Regla inicial de acceso

Antes de cualquier inspección, comparación, exportación o copia, el agente valida el perfil del ambiente solicitado en modo sólo lectura. Si el perfil no existe, es inválido o no tiene permisos, debe informar esa limitación y detener ese flujo; no pide ni muestra credenciales y no intenta usar otro ambiente como sustituto.

Abra una tarea **nueva** de Codex Desktop dentro del proyecto APEX al terminar la preparación.

## 3. Formas de uso

### Iniciar un proyecto

```text
Usa apex-project-bootstrap-final para iniciar este proyecto APEX.
```

### Inspeccionar APEX u Oracle en TEST o Producción

```text
Conéctate al ambiente <test|production>. Primero valida mi perfil de acceso
en modo sólo lectura. Después revisa la aplicación <id>, página <id> u objeto
<nombre>. No ejecutes cambios; entrega evidencia y limitaciones de acceso.
```

### Diagnosticar un error

```text
Usa apex-database-diagnostics en <test|production>. Primero valida el perfil.
Analiza este error sólo en lectura; entrega evidencia, causa, plan TEST,
validación y rollback. No ejecutes cambios.
```

### Comparar TEST y Producción

```text
Usa apex-database-diagnostics, apex-mcp-test y apex-mcp-production.
Primero valida ambos perfiles. Compara aplicación <id>, página <id> u objeto
<nombre> sólo en lectura. Genera environment-diff.md con evidencia,
diferencias y limitaciones. No ejecutes cambios.
```

### Copiar páginas de Producción a TEST

La solicitud debe identificar aplicación, páginas y ambiente destino. Copiar es una modificación de TEST, por lo que el agente debe validar ambos perfiles, confirmar la autorización explícita incluida en la solicitud, generar backup/export de TEST, comparar diferencias y preparar evidencia/rollback antes de aplicar la copia. Nunca sobrescribe TEST silenciosamente ni modifica Producción.

```text
Conéctate a Producción y TEST. Valida primero ambos perfiles. Copia las páginas
<lista> de la aplicación <id> desde Producción hacia TEST. La autorización para
modificar TEST está confirmada. Antes de aplicar: exporta backup de TEST,
genera environment-diff.md, detalla el impacto y rollback. No modifiques Producción.
```

## 4. Documentación de consulta

| Necesidad | Documento |
| --- | --- |
| Instalación, mensajes y solución de problemas | [Inicialización Codex](docs/inicializacion-automatica-codex.md) |
| Perfiles seguros TEST/Producción | [Perfiles seguros](docs/perfiles-credenciales-seguros.md) |
| Registro MCP en Codex Desktop | [Oracle MCP](docs/codex-desktop-mcp-oracle.md) |
| Flujos reutilizables y comparación de ambientes | [Casos de uso](docs/casos-de-uso-apex.md) |
| Reglas de estructuras y entregables por proyecto | [Estructura estándar](docs/estructura-estandar-proyecto.md) |
| Auditoría obligatoria | [Auditoría](docs/auditoria-obligatoria.md) |

## 5. Cierre obligatorio

Antes de informar que un cambio está terminado, ejecute:

```powershell
python .\scripts\audit_skill_ecosystem.py
git diff --check
```

El manual detallado de cada aplicación se genera al cierre, después de QA aprobada y evidencia validada.
