# Manual de uso — APEX Skills

Punto de entrada para usuarios y agentes Oracle APEX. Describa el objetivo en lenguaje natural: el coordinador detecta el contexto y selecciona los flujos especializados. No es necesario escribir `usa apex` ni memorizar nombres de skills.

## 1. Preparar el equipo una sola vez

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

## 2. Uso recomendado

Escriba la solicitud directamente:

```text
Quiero revisar la página <id> de la aplicación <id> en TEST porque está lenta.
```

```text
Revisa el paquete <esquema>.<paquete> y propone cómo optimizar su ejecución.
```

```text
Voy a trabajar en la aplicación <numero>, proyecto <nombre>, rango de páginas <desde>-<hasta>.
```

El coordinador reconoce APEX, Oracle, Application Express/App Express, objetos de base de datos, SQL, PL/SQL, errores ORA y rendimiento. También cubre errores tipográficos frecuentes como `orcle`, `oracel`, `orcale`, `oracl`, `oralce`, `apx`, `apxe`, `apexx`, `a-pex` y `apek`. Si un término aislado es ambiguo, solicita una aclaración breve antes de operar.

El agente valida el perfil del ambiente solicitado antes de inspeccionar. Si el perfil no existe, es inválido o no tiene permisos, informa la limitación y no intenta sustituir el ambiente.

## 3. Reiniciar el MCP local

`apex-mcp-test` y `apex-mcp-production` usan `stdio`: se inician por cada tarea de Codex Desktop, no quedan ejecutándose como un servicio permanente.

1. Cierre la tarea actual de Codex Desktop que usa el MCP.
2. Desde PowerShell, ejecute:

```powershell
cd "<RUTA_APEX_SKILLS>"
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>"
codex mcp list
```

3. Confirme que `apex-mcp-test` aparece como `enabled`. Si requiere Producción autorizada, confirme también `apex-mcp-production`.
4. Abra una **tarea nueva** con `<RUTA_PROYECTO_APEX>` como workspace y describa directamente el trabajo.

El inicializador reaplica la compatibilidad de conexión directa, verifica el perfil TEST y confirma el registro MCP. No solicite wallet para una conexión directa ya configurada. `Unsupported` en la columna `Auth` es normal para un MCP local `stdio`.

## 4. Flujos comunes

| Solicitud | Qué coordina automáticamente |
| --- | --- |
| Proyecto nuevo | Workspace, decisiones, plan y ciclo de desarrollo. |
| Proyecto/rango de páginas | Reserva, detección de cruces TEST/Producción y estructura adicional. |
| Inspección, error o lentitud | MCP seguro, lectura, evidencia, causa y análisis de rendimiento. |
| Optimización de paquete, función, vista o consulta | Diagnóstico de ejecución; gobierno DATA si se solicita un cambio. |
| Cambio de página existente | Alineación TEST/Producción antes de editar. |
| Cambio DATA | Gobierno de objetos, decisiones, scripts y validación de estilo SQL. |
| Copia Producción → TEST | Validación de ambos perfiles, alcance, diferencias y autorización para TEST. |
| Copia TEST → Producción | Explicación de impacto/riesgo y aprobación explícita separada para Producción. |
| Manual final | QA/evidencia y flujo de Word validado. |

## 5. Nombres de skills

Las skills especializadas no se eliminan: ayudan al coordinador a aplicar reglas concretas. Puede invocarlas si conoce el caso exacto, pero para el uso normal basta describir la necesidad.

## 6. Documentación de consulta

| Necesidad | Documento |
| --- | --- |
| Instalación y problemas | [Inicialización Codex](docs/inicializacion-automatica-codex.md) |
| Perfiles TEST/Producción | [Perfiles seguros](docs/perfiles-credenciales-seguros.md) |
| MCP Codex Desktop | [Oracle MCP](docs/codex-desktop-mcp-oracle.md) |
| Casos de uso | [Casos de uso](docs/casos-de-uso-apex.md) |
| Dependencias/upstreams | [Dependencias](docs/dependencias.md) |
| Auditoría | [Auditoría obligatoria](docs/auditoria-obligatoria.md) |

## 7. Cierre obligatorio

```powershell
python .\scripts\audit_skill_ecosystem.py
git diff --check
```
