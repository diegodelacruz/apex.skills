# Estado canónico actual

## Entrada para proyectos nuevos

1. `apex-project-bootstrap-final`
2. `apex-delivery-lifecycle-safe`

## Upstreams administrados

| Fuente | Propósito | Gestión |
| --- | --- | --- |
| `apex-mcp` | Herramientas MCP APEX | `.upstreams/managed/`; inicializador/actualizador V2 |
| `zaimella-skill` | Estándares, QA, Playwright y manuales | `.upstreams/managed/`; inicializador/actualizador V2 |
| `zaimella-apex-oracle` | Fuente privada APEX/Oracle | `.upstreams/managed/`; inicializador/actualizador V2 |

Las referencias opcionales `oracle-apex` y `emilkowalski-skills` viven en
`.upstreams/references/` y sirven únicamente para consulta o adaptación.

`scripts/Sync-ApexSkillUpstreams.ps1` prepara snapshots incluidos, revisa los remotos y actualiza las copias administradas con backup y rollback. `Setup-ApexSkills.ps1` lo ejecuta al instalar; `Initialize-ApexCodexProject.ps1` ejecuta el setup automáticamente antes del diagnóstico. Tras revisar un upstream actualizado, regenere los snapshots y sus commits fijados con `scripts/Export-ApexSkillUpstreamSnapshots.ps1`.

## Runtime

La opción inicial es un único `.venv` en el repositorio de skills. Los proyectos nuevos solo crean `.venv` propio si tienen dependencias propias, CI aislado o instrucción explícita. La decisión debe constar en `control-proyecto/decisiones/decisiones-globales.md`.

Para Codex, `apex-controlled-mcp` usa esa `.venv` y un runtime per-user de
Java/SQLcl bajo `%LOCALAPPDATA%\ApexSkills\runtimes`. No usa ni registra el
upstream `apex-mcp` completo.
