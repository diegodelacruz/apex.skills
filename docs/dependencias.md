# Dependencias y fuentes remotas

## Python

Para una clonación nueva, ejecute un único comando:

.\scripts\Setup-ApexSkills.ps1

El script prepara snapshots administrados, intenta actualizar cada remoto, crea `.venv`, instala `requirements.txt`, valida la compilación del runtime y luego instala las skills. Los snapshots versionados de `vendor/upstreams/` permiten continuar sin acceso remoto; cada copia previa se respalda antes de reemplazarla. Si un remoto falla, se conserva la copia activa o se usa el snapshot incluido. `Initialize-ApexCodexProject.ps1 -ProjectPath <RUTA>` también ejecuta este setup automáticamente antes de validar el proyecto.

```powershell
python -m pip install -r requirements.txt
```

requirements.txt instala las dependencias base. El runtime apex-mcp es opcional para CI/Dependabot y se instala localmente por Setup-ApexSkills.ps1 desde .upstreams/managed/apex-mcp.

`fastmcp` es una dependencia directa para `apex-controlled-mcp`; no depende de
`apex-mcp`. El setup autónomo `Setup-ApexControlledMcp.ps1` instala Python,
Java y SQLcl por usuario sin usar VS Code ni clonar upstreams.

## Upstreams administrados

El registro administra los tres upstreams canónicos bajo `.upstreams/managed/`; sus snapshots de recuperación están versionados bajo `vendor/upstreams/`. No deben clonarse manualmente dentro de cada proyecto:

| Repositorio | Uso |
| --- | --- |
| `https://github.com/TechFernandesLTDA/apex-mcp` | Integración MCP Oracle/APEX; se limita a inspección/dry-run para APEX 24.1.3. |
| `https://github.com/jefersonKel/zaimella-skill` | Estándares, QA, Playwright y manuales. |
| `https://github.com/zaimella/zaimella-apex-oracle` | Fuente complementaria APEX/Oracle administrada como upstream local. |

Los snapshots actuales de `zaimella-skill` y `zaimella-apex-oracle` no contienen un archivo de licencia; el registro conserva `not-declared`. El responsable del repositorio confirmó el 2026-09-23 que autoriza redistribuir ambos snapshots en el repositorio GitHub `diegodelacruz/apex.skills`; esa autorización de publicación no cambia la licencia declarada de los upstreams.

La instalación y actualización normal usa `scripts/Sync-ApexSkillUpstreams.ps1`. El script actualiza cada upstream por separado, verifica fast-forward y overlay, respalda antes del reemplazo y conserva la copia anterior cuando no puede validar una actualización. El snapshot de `apex-mcp` separa el commit MIT del overlay local existente. Las referencias continúan siendo opcionales y no se incluyen en el setup normal.

## Referencias opcionales

Oracle APEX y `emilkowalski/skills` se clonan bajo `.upstreams/references/` con `Initialize-ApexSkillUpstreams-V2.ps1 -IncludeReferences`. Son fuentes de consulta/adaptación y no runtime ni destino de importación.

## Node / Playwright

Playwright no es una dependencia Python. El flujo QA/manual usa el runner upstream `ensure-playwright-env.ps1`, que instala el paquete oficial `@playwright/test`. No clone el repositorio completo de Microsoft Playwright.

## Referencias transitivas

| Repositorio | Acción |
| --- | --- |
| `https://github.com/microsoft/playwright` | No clonar; usar el paquete npm oficial mediante el runner upstream. |
| `https://github.com/jlowin/fastmcp` | Dependencia resuelta por `apex-mcp`. |

## Política de actualización

No actualice upstreams manualmente. Use el registro único `upstreams.lock.json`
y los scripts canónicos. El flujo hace preflight, crea un backup verificable,
actualiza mediante fast-forward, valida los commits y revierte automáticamente
todos los checkouts si falla una actualización.
