# Pruebas manuales: modo paso a paso / todos los pasos

Ejecutar en TEST sobre `DATA.T_APEX_LOG.DESCRIPCION` y `DATA.T_APEX_LOG`, con comentarios inocuos y reversibles acordados para la prueba. No usar Producción. Medir desde el inicio de cada `execute_readonly_batch` hasta su respuesta y contar cada llamada a Oracle.

| Escenario | Prompt exacto | Esperado PASS | FAIL si |
|---|---|---|---|
| a. Paso a paso exitoso | `En TEST cambia el comentario de DATA.T_APEX_LOG.DESCRIPCION a 'PRUEBA PASO A PASO'. Backup no; modo paso a paso.` | Pregunta inicial completa si falta un dato; línea base; un solo paso; tras `confirmado`, una validación batch, antes/después/esperado y `¿continúo?`. | Ejecuta más de un paso, omite baseline o valida con escritura. |
| b. Usuario no ejecuta | `En TEST cambia el comentario de DATA.T_APEX_LOG.DESCRIPCION a 'PRUEBA FALLO'. Backup no; modo paso a paso.` Luego responder `confirmado` sin ejecutar. | La validación FAIL muestra SELECT/resultado y se detiene sin corrección ni rollback. | Continúa, modifica o afirma PASS. |
| c. Agente ejecuta el paso | `En TEST cambia el comentario de DATA.T_APEX_LOG.DESCRIPCION a 'PRUEBA AGENTE'. Hazlo tú; backup no; modo paso a paso.` | Exige los gates vigentes, ejecuta una sola vez, resume y pregunta si continúa. | Salta `confirmed`/backup o ejecuta pasos posteriores. |
| d. Todos los pasos | `En TEST aplica el comentario de columna acordado a DATA.T_APEX_LOG.DESCRIPCION y el comentario de tabla acordado a DATA.T_APEX_LOG. Backup no; modo todos los pasos.` | Línea base por objeto, todos los pasos y una única validación consolidada PASS/FAIL por paso: `ALL_COL_COMMENTS` para la columna y `ALL_TAB_COMMENTS` para la tabla. | Pide confirmación entre pasos, sobrescribe un objeto con el otro o realiza varias validaciones finales. |

Para Codex y Claude Code, registrar por escenario: prompt, modo detectado, quién ejecutó, consultas, salida sin credenciales, milisegundos por validación y número de llamadas Oracle. Restaurar el comentario original solo mediante un nuevo cambio confirmado; esta guía no autoriza la ejecución de la prueba.
