# Decisión: modo paso a paso, todos los pasos y línea base

- **Fecha:** 2026-10-15
- **Estado:** pendiente de revisión independiente
- **Objetivo:** definir una interacción verificable para cambios Oracle/APEX y desarrollos sin retrasar lecturas inmediatas.
- **Alcance:** documentación, adaptadores de instrucciones y regresiones; no cambia `scripts/apex_controlled_mcp.py`, herramientas MCP, credenciales ni datos Oracle/APEX.
- **Decisión:** antes de escribir se pide una vez ambiente, objeto, acción, backup sí/no y modo. Paso a paso es predeterminado, valida una unidad por vez y limita a cinco iteraciones; todos los pasos valida de forma consolidada. La línea base se lee una vez por objeto en el mismo lote de identidad. El checkpoint `¿continúo?` es una unidad de alcance, no otra decisión de backup. Fallos y pasos no verificables detienen el flujo sin corrección o rollback automáticos.
- **Alternativas:** mantener solo la confirmación única previa, descartada porque no describe la pausa/validación; imponer pasos a lecturas, descartado porque contradice lectura inmediata; cambiar el MCP, descartado porque el comportamiento cabe en instrucciones y pruebas.
- **Impacto y riesgos:** armoniza `AGENTS.md`, `CLAUDE.md`, coordinador y governance. Las plantillas dependen de vistas públicas/privilegios APEX y una falla de conectividad no demuestra ausencia de una vista.
- **Compatibilidad:** conserva los gates `confirmed` y `backup_choice`, las lecturas inmediatas y el uso de vistas públicas `APEX_APPLICATION_*`; no usa `WWV_FLOW_*`.
- **Validación:** pruebas rojas antes de los documentos; regresiones de referencias, frases D1-D7 y validación sintáctica de SELECT. TEST solo lectura confirmó `DATA.T_APEX_LOG.DESCRIPCION`; 17 plantillas terminaron correctamente, la forma larga de validaciones devolvió `ORA-00942`, y la variante pública `APEX_APPLICATION_PAGE_VAL` terminó correctamente. Un intento previo recibió `SP2-0640` antes de SQL y queda como evidencia de conectividad transitoria, no de ausencia de metadatos.
- **Rollback:** revertir conjuntamente documentos, adaptadores, pruebas y changelog; no hay datos que restaurar.
- **Descontinuación:** revisar si se incorpora una aprobación autenticada o una evidencia de persistencia distinta; mantener entonces lectura inmediata y no corrección automática ante fallos.
