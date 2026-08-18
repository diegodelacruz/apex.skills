# Dependencias y fuentes remotas

## Python

Instale las dependencias desde la raíz del repositorio después de inicializar los upstreams:

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt` instala el servidor `apex-mcp` desde `.upstreams/apex-mcp`, además de `python-docx`, `Pillow` y `pytest`.

## Node / Playwright

Playwright no es una dependencia Python. El flujo de QA/manual lo instala de manera reutilizable mediante la script upstream `ensure-playwright-env.ps1`, que usa el paquete oficial `@playwright/test`. No clone el repositorio completo de Microsoft Playwright para usar estas skills.

## Referencias a repositorios no clonados

| Repositorio | Uso | Acción |
| --- | --- | --- |
| `https://github.com/zaimella/zaimella-apex-oracle` | Fuente oficial de objetos APEX/Oracle para un proyecto empresarial Zaimella. | Clonar dentro del proyecto que lo requiera, no dentro de este repositorio de skills. |
| `https://github.com/zaimella/Zaimella-Movilmella` | Fuente Flutter de Movilmella. | No clonar para proyectos APEX salvo que el alcance incluya esa aplicación. |
| `https://github.com/microsoft/playwright` | Código fuente oficial de Playwright. | No clonar; instalar el paquete npm oficial mediante el runner upstream. |
| `https://github.com/jlowin/fastmcp` | Dependencia Python transitiva/directa de `apex-mcp`. | La resuelve pip desde la dependencia declarada de `apex-mcp`. |
