# Manual de uso — APEX Skills

Punto de entrada para usuarios y agentes Oracle APEX. No es necesario memorizar nombres largos: use `apex` o describa el objetivo en lenguaje natural; el coordinador selecciona los flujos especializados.

## 1. Preparar el equipo una sola vez

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

## 2. Uso recomendado

Empiece sus solicitudes con `Usa apex.`:

```text
Usa apex. Quiero revisar la página <id> de la aplicación <id> en TEST.
```

```text
Usa apex. Voy a trabajar en la aplicación <numero>, proyecto <nombre>,
rango de páginas <desde>-<hasta>.
```

```text
Usa apex. Compara esta aplicación/página entre TEST y Producción sólo en lectura.
```

El agente valida el perfil del ambiente solicitado antes de inspeccionar. Si el perfil no existe, es inválido o no tiene permisos, informa la limitación y no intenta sustituir el ambiente.

## 3. Flujos comunes

| Solicitud | Qué coordina `apex` |
| --- | --- |
| Proyecto nuevo | Workspace, decisiones, plan y ciclo de desarrollo. |
| Proyecto/rango de páginas | Reserva, detección de cruces TEST/Producción y estructura adicional. |
| Inspección o diagnóstico | MCP seguro, lectura, evidencia y causa. |
| Cambio de página existente | Alineación TEST/Producción antes de editar. |
| Cambio DATA | Gobierno de objetos, decisiones y scripts. |
| Copia Producción → TEST | Validación de ambos perfiles, alcance, diferencias y autorización para TEST. |
| Copia TEST → Producción | Explicación de impacto/riesgo y aprobación explícita separada para Producción. |
| Manual final | QA/evidencia y flujo de Word validado. |

## 4. Nombres de skills

Las skills especializadas no se eliminan: ayudan al coordinador a aplicar reglas concretas. Puede invocarlas si conoce el caso exacto, pero para el uso normal basta `apex`.

## 5. Documentación de consulta

| Necesidad | Documento |
| --- | --- |
| Instalación y problemas | [Inicialización Codex](docs/inicializacion-automatica-codex.md) |
| Perfiles TEST/Producción | [Perfiles seguros](docs/perfiles-credenciales-seguros.md) |
| MCP Codex Desktop | [Oracle MCP](docs/codex-desktop-mcp-oracle.md) |
| Casos de uso | [Casos de uso](docs/casos-de-uso-apex.md) |
| Dependencias/upstreams | [Dependencias](docs/dependencias.md) |
| Auditoría | [Auditoría obligatoria](docs/auditoria-obligatoria.md) |

## 6. Cierre obligatorio

```powershell
python .\scripts\audit_skill_ecosystem.py
git diff --check
```
