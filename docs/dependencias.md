# Dependencias y fuentes remotas

## Python

Instale dependencias desde la raíz después de inicializar los upstreams:

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt` instala `apex-mcp` desde `.upstreams/apex-mcp`, además de `python-docx`, `Pillow` y `pytest`.

## Upstreams administrados

El inicializador administra localmente los tres upstreams canónicos. No deben clonarse manualmente dentro de cada proyecto:

| Repositorio | Uso |
| --- | --- |
| `https://github.com/TechFernandesLTDA/apex-mcp` | Integración MCP Oracle/APEX; se limita a inspección/dry-run para APEX 24.1.3. |
| `https://github.com/jefersonKel/zaimella-skill` | Estándares, QA, Playwright y manuales. |
| `https://github.com/zaimella/zaimella-apex-oracle` | Fuente complementaria APEX/Oracle administrada como upstream local. |

Actualice los tres mediante `Update-ApexSkillUpstreams-V2.ps1`; el inicializador reaplica el patch canónico de conexión directa de `apex-mcp`.

## Node / Playwright

Playwright no es una dependencia Python. El flujo QA/manual usa el runner upstream `ensure-playwright-env.ps1`, que instala el paquete oficial `@playwright/test`. No clone el repositorio completo de Microsoft Playwright.

## Referencias transitivas

| Repositorio | Acción |
| --- | --- |
| `https://github.com/microsoft/playwright` | No clonar; usar el paquete npm oficial mediante el runner upstream. |
| `https://github.com/jlowin/fastmcp` | Dependencia resuelta por `apex-mcp`. |
