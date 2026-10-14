# Decisión: comprobar SQLcl solo bajo solicitud de diagnóstico

- **Fecha:** 2026-10-13
- **Estado:** vigente
- **Objetivo:** evitar ejecutar una comprobación adicional de SQLcl antes de cada lectura o cambio y conservar el diagnóstico explícito del runtime.
- **Decisión:** solo la herramienta `doctor()` ejecuta `sqlcl -version` con timeout de 30 segundos. Las lecturas, inspecciones, consultas, SQL directo y bundles intentan la operación solicitada directamente. Si SQLcl no inicia, la ruta clasifica el error observado sin repetir la prueba de versión.
- **Alternativa descartada:** mantener el preflight de runtime en todas las rutas. Agregaba una ejecución local repetida y podía consumir hasta 30 segundos antes de la operación.
- **Implicación:** errores de instalación o arranque se descubren en el propio intento de operación, salvo que el usuario solicite `doctor()`. La llamada SQLcl normal conserva su timeout operacional de 120 segundos.
- **Validación:** cobertura de que `doctor_report()` solo sea llamado por la herramienta explícita, que `doctor()` conserve el probe `-version`, que consultas no hagan el preflight y que un runtime ausente devuelva un error clasificado.
