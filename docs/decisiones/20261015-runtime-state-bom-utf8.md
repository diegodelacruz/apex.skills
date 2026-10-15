# Decisión: tolerar BOM UTF-8 en runtime-state.json

- **Fecha:** 2026-10-15
- **Estado:** vigente
- **Objetivo y necesidad:** permitir que `runtime_state()` lea el estado del runtime generado con BOM UTF-8 por Windows PowerShell 5.1 (`Set-Content -Encoding UTF8`). Con `utf-8`, `json.loads()` rechazaba el BOM y el diagnóstico clasificaba un runtime instalado como ausente.
- **Alcance:** cambiar únicamente la codificación de lectura en `runtime_state()`, añadir regresiones para archivos con y sin BOM y para `doctor_report()`, y registrar la corrección en este documento y el changelog.
- **Decisión:** leer `runtime-state.json` con `encoding="utf-8-sig"`, que consume un BOM UTF-8 si existe y conserva la lectura de JSON UTF-8 sin BOM.
- **Alternativas consideradas:** corregir también el instalador PowerShell para escribir sin BOM. Se descarta en este cambio porque no es necesario para aceptar el estado existente en máquinas ya instaladas, ampliaría el alcance a una plataforma de escritura y no resolvería archivos ya creados. Puede evaluarse por separado si existe una necesidad adicional.
- **Impacto y riesgos:** evita el falso `RUNTIME_NOT_INSTALLED` para archivos con BOM. El cambio se limita al decodificador usado para ese archivo; permanecen los errores de lectura y JSON inválido clasificados como estado no disponible.
- **Compatibilidad:** conserva compatibilidad con archivos UTF-8 sin BOM y acepta los archivos UTF-8 con BOM producidos por Windows PowerShell 5.1. No cambia el instalador ni requiere acceso a Oracle.
- **Validación:** pruebas de regresión para BOM, sin BOM y `doctor_report()` con BOM, más suite y validadores locales aplicables; prueba roja registrada antes del cambio.
- **Rollback:** revertir el cambio de `utf-8-sig` a `utf-8` y retirar las pruebas y esta decisión junto con la entrada correspondiente del changelog.
- **Descontinuación:** no aplica; no se introduce interfaz ni dependencia nueva. Reconsiderar únicamente si se retira el formato de estado con BOM y sus usuarios compatibles.
