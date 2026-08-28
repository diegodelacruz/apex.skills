# Pendientes del proyecto

Este archivo mantiene los trabajos pendientes de `apex.skills`. Cada punto debe
conservar objetivo, alcance, riesgo, dependencia, responsable, evidencia y
estado. Un pendiente no se cierra sólo porque exista una propuesta: requiere
validación y revisión independiente según la política canónica.

## P-001 — Auditoría integral y calificación del ecosistema

**Estado:** pendiente
**Objetivo:** llevar el repositorio a una calificación cercana a 100/100 en
cualquier agente compatible, aplicando estándares de industria y un punto medio
entre las diferencias de criterio de Codex, Claude, Cursor, Gemini y otros.

**Alcance inicial:**

- definir una matriz de calidad común y medible;
- auditar funcionalidad, técnica, seguridad, dependencias, documentación,
  routing, skills, adaptadores, hooks, CI y upstreams;
- comparar el comportamiento de descubrimiento y activación entre agentes;
- actualizar documentación y catálogos sin duplicar autoridad;
- identificar brechas, deuda técnica y controles faltantes;
- establecer una línea base de puntuación y criterios de aceptación;
- exigir revisión independiente y evidencia reproducible antes del cierre.

**Dependencias:** política canónica de evolución, auditoría integral, inventario
de skills y matriz de compatibilidad entre agentes.
**Criterio de cierre:** todos los controles aplicables en `PASS`, los `N/A`
justificados, documentación sincronizada, pruebas ejecutadas, limitaciones
declaradas y revisión independiente registrada.

## P-002 — Prueba controlada del ciclo de actualización de upstreams

**Estado:** pendiente
**Objetivo:** probar en un checkout temporal el preflight, backup, fast-forward,
validación del commit y rollback automático sin tocar los cambios locales
existentes de `apex-mcp`.

**Criterio de cierre:** evidencia de éxito y de fallo controlado, incluyendo
restauración completa del lock y de todos los repositorios seleccionados.
