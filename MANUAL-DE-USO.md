# Manual de uso — APEX Skills

Punto de entrada para usar las skills de Oracle APEX con Codex Desktop. No contiene secretos ni datos de un proyecto particular.

## 1. Preparar el equipo una sola vez

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

El inicializador prepara dependencias, habilita conexión Oracle directa cuando corresponda, importa TEST desde `.env` si hace falta y registra `apex-mcp-test`.

## 2. Regla inicial de acceso

Antes de inspeccionar, comparar, exportar o copiar, el agente valida el perfil del ambiente solicitado en modo sólo lectura. Si el perfil no existe, es inválido o no tiene permisos, informa la limitación y detiene ese flujo; no solicita ni muestra secretos.

Abra una tarea **nueva** de Codex Desktop dentro del proyecto APEX.

## 3. Formas de uso

### Iniciar un proyecto

```text
Usa apex-project-bootstrap-final para iniciar este proyecto APEX.
```

### Inspeccionar APEX u Oracle

```text
Conéctate al ambiente <test|production>. Primero valida mi perfil de acceso
en modo sólo lectura. Después revisa la aplicación <id>, página <id> u objeto
<nombre>. No ejecutes cambios; entrega evidencia y limitaciones de acceso.
```

### Diagnosticar o comparar ambientes

```text
Usa apex-database-diagnostics, apex-mcp-test y apex-mcp-production.
Primero valida ambos perfiles. Compara aplicación <id>, página <id> u objeto
<nombre> sólo en lectura. Genera environment-diff.md. No ejecutes cambios.
```

### Copiar Producción → TEST

La solicitud debe identificar aplicación, páginas y autorizar explícitamente modificar TEST. El agente valida ambos perfiles, crea backup/export de TEST, genera diferencias y rollback antes de aplicar. Producción permanece sólo lectura.

### Copiar TEST → Producción

La copia hacia Producción exige **autorización explícita e independiente** del usuario, incluso si el cambio ya fue aprobado en TEST. Antes de aplicar, el agente valida perfiles, QA TEST, release SQL/manifiesto, backup/rollback y evidencia. Sin esa autorización no instala, importa ni modifica Producción.

```text
El cambio TEST <id> está aprobado para Producción. Autorizo explícitamente
instalar los artefactos <lista> en Producción. Valida perfil, QA, backup,
rollback y evidencia antes de ejecutar. Registra el resultado.
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

```powershell
python .\scripts\audit_skill_ecosystem.py
git diff --check
```

El manual detallado de cada aplicación se genera al cierre, después de QA aprobada y evidencia validada.
