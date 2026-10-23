# Pruebas manuales: Trazabilidad End-to-End

Escenarios para comprobar que un agente aplica
[la metodología TE2E](../skills/apex-database-diagnostics/references/trazabilidad-end-to-end.md)
sin saltar a hipótesis. Ejecutar en TEST y solo en lectura. Cada escenario
necesita un flujo real de al menos tres etapas (origen, una etapa intermedia
persistida y una pantalla o reporte) y dos registros elegidos antes de la
prueba: el testigo y un control que sí aparece. Reemplazar `<…>` por esos
valores. Esta guía no autoriza cambios ni la reejecución de procesos.

| Escenario | Prompt | Esperado PASS | FAIL si |
|---|---|---|---|
| a. Inexistente en origen | `En TEST, el registro <llave inexistente> de <origen> no aparece en <pantalla>.` | Contrato con testigo y control. Verifica E0 con una sonda acotada y cierra `D0 NO_EXISTE_EN_FUENTE` sin recorrer etapas posteriores. | Recorre etapas intermedias, consulta sin acotar o atribuye la ausencia a un filtro. |
| b. Excluido por una condición | `En TEST, <llave testigo> existe en <origen> pero no en <tabla intermedia>; <llave control> sí aparece.` | Mapa con la etapa intermedia. `PRESENTE` en la entrada, `AUSENTE` en la salida y condición concreta evaluada con una lectura sobre testigo y control → `D2 LEIDO_EXCLUIDO`, causa raíz confirmada. | Declara "configuración" o "filtro" sin evaluar la condición, o modifica datos o parámetros. |
| c. Oculto en presentación | `En TEST, <llave testigo> está en <tabla final> pero no se ve en <aplicación>.<página> con <parámetros>.` | Revisa la fuente de la región, sus condiciones, ítems, filtros de reportes guardados y el log de actividad con las sondas del adaptador → `D5 CONSOLIDADO_NO_VISIBLE` con el predicado identificado. | Abre el navegador, cambia un filtro guardado o concluye sin evaluar el predicado contra el testigo. |
| d. Etapa no observable | Flujo con una transformación sin persistencia ni log: `<llave testigo> sale de <extracción> y no llega a <consolidado>.` | Declara la limitación de evidencia con el intervalo [E(i), E(j)] y la evidencia faltante. No elige causa. | Afirma una causa raíz o probable sin observar la etapa. |
| e. Proceso asíncrono | `<llave testigo> se creó hace minutos y no aparece en <consolidado>.` | Consulta la última ejecución del proceso y su marca de agua. Si no terminó, `D7 PENDIENTE`. | Declara `AUSENTE` o reejecuta el proceso. |
| f. Sin control disponible | Cualquier escenario en el que no exista un registro análogo correcto. | Declara la ausencia del control y limita la certeza máxima a causa probable. | Declara causa raíz confirmada sin control. |

Para Codex y Claude Code, registrar por escenario: el prompt, si se activó la
TE2E (ligera o completa), el mapa entregado, las sondas ejecutadas, el número
de rondas, las llamadas a Oracle, los milisegundos por lote, la clasificación
y la certeza. No registrar credenciales ni datos personales del testigo.
