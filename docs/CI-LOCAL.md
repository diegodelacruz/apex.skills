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
`pip check`, la auditoría del ecosistema, la puntuación de calidad, la suite
completa con cobertura, Black, isort, flake8, mypy, Bandit, detect-secrets y
`git diff --check`. Termina en el primer fallo.
La política canónica exige ejecutar este comando antes de cada commit o pull
request; GitHub Actions ejecuta el mismo runner.

## Cobertura

El umbral combinado de líneas ejecutables y destinos de ramas es **55%**; no
exige que las métricas de líneas y ramas alcancen 55% cada una. El último
reporte dio 60.65% de líneas, 43.12% de ramas y 56.63% combinado con 485
pruebas aprobadas. La meta
gradual del combinado es **80%**. `coverage.py` excluye ramas y líneas
justificadas por su configuración, pero cobertura no demuestra por sí sola que
las pruebas sean correctas ni que validen todos los casos. Cada aumento del
piso requiere primero pruebas que alcancen el nuevo valor.

`requirements.txt` contiene rangos y no un lock completo: CI y el entorno local
usan las mismas reglas de instalación, pero las versiones resueltas pueden
cambiar con el tiempo. Para reproducir exactamente todas las dependencias,
haría falta incorporar y mantener un archivo de bloqueo.
