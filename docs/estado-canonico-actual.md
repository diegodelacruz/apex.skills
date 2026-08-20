# Estado canónico actual

## Entrada para proyectos nuevos

1. `apex-project-bootstrap-final`
2. `apex-delivery-lifecycle-safe`

## Upstreams administrados

| Fuente | Propósito | Gestión |
| --- | --- | --- |
| `apex-mcp` | Herramientas MCP APEX | Inicializador/actualizador V2 |
| `zaimella-skill` | Estándares, QA, Playwright y manuales | Inicializador/actualizador V2 |
| `zaimella-apex-oracle` | Fuente privada APEX/Oracle | Inicializador/actualizador V2 |

Use `scripts/Initialize-ApexSkillUpstreams-V2.ps1` para preparar una copia nueva y `scripts/Update-ApexSkillUpstreams-V2.ps1` para toda actualización manual, con backup y rollback.

## Runtime

La opción inicial es un único `.venv` en el repositorio de skills. Los proyectos nuevos solo crean `.venv` propio si tienen dependencias propias, CI aislado o instrucción explícita. La decisión debe constar en `control-proyecto/decisiones/decisiones-globales.md`.
