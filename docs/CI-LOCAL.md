# Ejecutar CI localmente

El repositorio usa Python **3.13** como versión base. Se permiten actualizaciones
de parche dentro de 3.13; CI y el entorno virtual local deben usar esa misma
serie menor.

## Preparar el entorno en Windows

Desde la raíz del repositorio, una sola vez:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Después de actualizar `requirements.txt`, repetir el último comando.

## Ejecutar la misma secuencia que GitHub Actions

```powershell
.\.venv\Scripts\python.exe scripts\run_ci_checks.py
```

El runner comprueba la versión Python, la consistencia de dependencias con
`pip check`, la auditoría del ecosistema, la cobertura y enlaces Markdown de
todo el repositorio con `scripts/audit_markdown_links.py`, la puntuación de calidad, la suite
completa con cobertura, Black, isort, flake8, mypy, Bandit, detect-secrets y
`git diff --check`. Termina en el primer fallo.
La política canónica exige ejecutar este comando antes de cada commit o pull
request; GitHub Actions ejecuta el mismo runner.

El hook de pre-commit ejecuta el mismo `scripts/audit_markdown_links.py`. Su
salida concilia Markdown versionado encontrado en disco, incluye Markdown
pertinente no versionado, informa exclusiones y distingue enlaces locales,
externos rotos y externos no verificables. Un resultado incompleto o roto
devuelve un código distinto de cero. Se excluyen `.git`, entornos virtuales,
cachés, checkouts locales `.upstreams` y snapshots binarios bajo
`vendor/upstreams`; los upstreams se validan por sus propios controles de
origen/sincronización, no como Markdown mantenido directamente en este repo.
El índice Git actual no registra submódulos; si se agrega alguno, el auditor
falla cerrado hasta que cada submódulo tenga una auditoría de Markdown anidada
desde su propia raíz.

## Cobertura

El umbral combinado de líneas ejecutables y destinos de ramas es **55%**; no
exige que las métricas de líneas y ramas alcancen 55% cada una. El último
último runner local (2026-09-30) aprobó 509 pruebas con 57.94% de cobertura
combinada. La meta gradual del combinado es **80%**. `coverage.py` excluye ramas y líneas
justificadas por su configuración, pero cobertura no demuestra por sí sola que
las pruebas sean correctas ni que validen todos los casos. Cada aumento del
piso requiere primero pruebas que alcancen el nuevo valor.

`requirements.txt` contiene rangos y no un lock completo: CI y el entorno local
usan las mismas reglas de instalación, pero las versiones resueltas pueden
cambiar con el tiempo. Para reproducir exactamente todas las dependencias,
haría falta incorporar y mantener un archivo de bloqueo.
