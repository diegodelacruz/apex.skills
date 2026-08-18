# Entornos Python para proyectos que usan APEX Skills

## Regla por defecto

No cree un entorno virtual por cada proyecto APEX solo porque el proyecto referencia las skills. Cree y mantenga un único entorno compartido en el repositorio de skills:

```text
apex.skills/
├─ .venv/
├─ requirements.txt
└─ skills/
```

Los agentes ejecutan los scripts usando ese intérprete, por ejemplo:

```powershell
<ruta-a-apex.skills>\.venv\Scripts\python.exe <ruta-a-apex.skills>\skills\apex-pattern-mining-safe\scripts\mine_export_patterns.py <export.zip>
```

La configuración MCP debe usar igualmente el Python absoluto del entorno compartido.

## Cuándo crear `.venv` en el proyecto

Hágalo solo si el proyecto agrega dependencias Python propias, exige aislamiento para CI/reproducibilidad, o el usuario lo pide. En ese caso, registre la decisión y el comando de instalación en `control-proyecto/decisiones/decisiones-globales.md`.

## Instalación de dependencias

Al iniciar un proyecto, el agente comprueba si el runtime requerido está disponible.

- Con aprobación automática habilitada: instala las dependencias faltantes en el entorno aplicable y registra el resultado.
- Sin aprobación automática: pregunta una sola vez antes de ejecutar la instalación, indicando entorno y paquetes.

Playwright no pertenece a `requirements.txt`, porque requiere Node. El runner upstream lo prepara solo cuando se necesitan capturas/QA para el manual Word.
