# Manual de uso — APEX Skills

Punto de entrada para usar las skills de Oracle APEX con Codex Desktop. No contiene secretos ni datos de un proyecto particular.

## 1. Preparar el equipo una sola vez

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

## 2. Regla inicial de acceso

Antes de inspeccionar, comparar, exportar, copiar o reservar páginas, el agente valida el perfil del ambiente solicitado en modo sólo lectura. Si el perfil no existe, es inválido o no tiene permisos, informa la limitación y detiene ese flujo; no solicita ni muestra secretos.

Abra una tarea **nueva** de Codex Desktop dentro del proyecto APEX.

## 3. Formas de uso

### Iniciar un proyecto

```text
Usa apex-project-bootstrap-final para iniciar este proyecto APEX.
```

### Trabajar por proyecto y rango de páginas

```text
Voy a trabajar en la aplicación <numero> en el proyecto <nombre-proyecto>,
en el rango de páginas <desde> a <hasta>. Usa apex-page-range-governance.
Valida TEST y Producción, comprueba cruces de rango, crea la estructura del
proyecto dentro de la carpeta de aplicación y registra las diferencias.
No crees ni modifiques páginas si existe conflicto sin mi decisión explícita.
```

La estructura adicional será `aplicaciones/aplicacion-<numero>/<nombre-proyecto>/` con subcarpetas `pruebas/` y `produccion/`. No reemplaza `control-proyecto/`.

Toda página creada debe usar:

| Propiedad APEX | Valor |
| --- | --- |
| Page Name | `<nombre-proyecto>-<nombre-pagina>` |
| Page Title | `<nombre-pagina>` |

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

La solicitud debe identificar aplicación, páginas y autorizar explícitamente modificar TEST. El agente valida ambos perfiles, advierte alcance, crea backup/export y diferencias cuando el riesgo o el flujo lo ameriten, y no modifica Producción.

### Copiar TEST → Producción

La copia hacia Producción exige **autorización explícita e independiente**. Antes de ejecutar, el agente explica objetos/artefactos, ambiente destino, impacto y riesgo. Recomienda controles proporcionales; no los impone para un cambio menor ya validado por el usuario fuera de las skills.

## 4. Documentación de consulta

| Necesidad | Documento |
| --- | --- |
| Instalación y solución de problemas | [Inicialización Codex](docs/inicializacion-automatica-codex.md) |
| Perfiles seguros TEST/Producción | [Perfiles seguros](docs/perfiles-credenciales-seguros.md) |
| Registro MCP en Codex Desktop | [Oracle MCP](docs/codex-desktop-mcp-oracle.md) |
| Casos reutilizables | [Casos de uso](docs/casos-de-uso-apex.md) |
| Estructura y rango de páginas | [Layout y registro](skills/apex-page-range-governance/references/layout-and-register.md) |
| Auditoría obligatoria | [Auditoría](docs/auditoria-obligatoria.md) |

## 5. Cierre obligatorio

```powershell
python .\scripts\audit_skill_ecosystem.py
git diff --check
```
