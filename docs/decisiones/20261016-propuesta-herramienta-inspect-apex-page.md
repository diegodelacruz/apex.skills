# Propuesta: herramienta `inspect_apex_page` (foto de página en una llamada)

- **Fecha:** 2026-10-16
- **Estado:** propuesta, **no implementada**. Pendiente de revisión independiente y de decisión del usuario antes de cualquier implementación.
- **Objetivo y necesidad:** que la revisión de una página APEX (por ejemplo, "revisa la 109.131") se resuelva con una sola llamada determinista, sin que el agente componga consultas SQL. Hoy el agente escribe las consultas del lote a partir de `skills/apex-database-diagnostics/references/page-snapshot-queries.md`; cuando las reescribe, puede equivocarse y cada error cuesta una conexión completa.
- **Alcance:** una herramienta MCP de solo lectura en `scripts/apex_controlled_mcp.py`, apoyada en `execute_readonly_batch`, más las actualizaciones de skills, adaptadores, documentación y pruebas que correspondan. **Fuera de alcance:** sesión SQLcl persistente, multiagente, cualquier escritura, producción.

## Evidencia medida

Medición del 2026-10-16 en TEST, página 109.131, con el registro de sesión de Codex (marcas de hora por evento; método descrito abajo).

| Medición | Resultado |
|---|---|
| Revisión con una sesión SQLcl por consulta (10 consultas) | 108,7 s a 164,7 s solo en Oracle |
| Revisión con el lote, ejecución 1 (una llamada, consultas del archivo de referencia tal cual) | 22,7 s en Oracle |
| Revisión con el lote, ejecución 2 | **83,1 s de punta a punta** |

Reparto de la ejecución 2 (83,075 s):

| Concepto | Tiempo |
|---|---:|
| Hasta la primera llamada de herramienta | 3,5 s |
| Suma de herramientas | 45,2 s |
| Resto atribuible al modelo | 37,8 s |
| Del último resultado a la respuesta final | 8,6 s |

La ejecución 2 hizo **dos lotes Oracle**: el primero (23,3 s) falló con `BATCH_PARTIAL_FAILURE` porque el agente escribió sus propias consultas con columnas inexistentes; antes hubo dos rechazos inmediatos por `INVALID_BIND_VARIABLE`; el segundo lote (20,0 s) fue correcto. Con una sola llamada correcta se estima un total de 35 a 40 s **[Estimado]**.

Descomposición del costo de conexión (del diagnóstico registrado en `20261015-lectura-por-lote-una-conexion.md`): arranque de SQLcl ~4,7 s, login ~5,7 s, DNS y TCP despreciables.

## Diseño propuesto

- **Firma:** `inspect_apex_page(application_id: int, page_id: int, environment: str | None = None)`.
- **Fuente única de consultas:** las consultas de la página se leen de un archivo versionado del repositorio (el contenido actual de `page-snapshot-queries.md` convertido a un formato que la documentación y la herramienta compartan), con un nombre estable por consulta. El agente nunca escribe SQL.
- **Ejecución:** reutiliza `execute_readonly_batch` internamente (una conexión, transacción de solo lectura, identidad incluida, fallo cerrado ante salida incompleta, errores aislados por consulta).
- **Salida:** objeto estructurado con una clave por componente (`page`, `regions`, `items`, `buttons`, `processes`, `validations`, `dynamic_actions`, `dynamic_action_steps`, `branches`, `computations`), identidad de sesión, `timings_ms`, `input_substitutions` y el código de cada consulta.
- **Compatibilidad de datos:** la salida debe conservar los acentos (codificación ya corregida en `20261016-codificacion-utf8-sqlcl.md`).
- **Skills:** `skills/apex-database-diagnostics/SKILL.md` y `skills/apex/SKILL.md` indicarán usar esta herramienta para revisar una página y reservar el lote libre para consultas que el snapshot no cubra.

## Alternativas consideradas

| Alternativa | Decisión | Motivo |
|---|---|---|
| Mantener el lote y la referencia (estado actual) | Insuficiente | Funciona, pero depende de que el modelo copie bien las consultas; en la medición falló una vez de dos |
| Reforzar las instrucciones de las skills | Insuficiente | No elimina la variabilidad del modelo ni entre agentes (Codex, Claude Code, Antigravity) |
| Sesión SQLcl persistente | Aplazada | Ahorraría ~10 s por llamada, pero exige gestionar ciclo de vida, credenciales en memoria, caducidad y concurrencia |
| Multiagente para el diagnóstico | No aporta tiempo en este caso | El tiempo se reparte entre conexión Oracle (52 %) y composición del modelo (46 %); más agentes pagarían más conexiones |

## Criterios de aceptación

1. Una revisión de la página 109.131 en TEST usa **una** llamada a la herramienta y **una** conexión Oracle, sin `INVALID_BIND_VARIABLE` ni `BATCH_PARTIAL_FAILURE`.
2. El resultado coincide con la línea base de la página (regiones `Reporte` y `Barra de Acciones`; botones `HISTORICO`, `Codigos_ISD`, `AGREGAR`; acción dinámica `CierreDialogo`; sin ítems, procesos, validaciones, ramas ni cálculos).
3. Tiempo total de punta a punta menor que la ejecución 2 (83,1 s), con la meta de 35 a 40 s **[Estimado]**.
4. Acentos correctos (`Histórico`, `...IMPORTACIÓN`) y sin `Ã` ni `�`.
5. Un agente que no sea Codex obtiene el mismo resultado con la misma herramienta.

## Riesgos

- Las vistas `APEX_APPLICATION_*` y sus columnas dependen de la versión de APEX (verificado en 24.2); otra versión podría requerir ajustes y debe fallar con un código claro, no con datos parciales.
- Acoplar documentación y herramienta al mismo archivo exige una prueba que impida que se desincronicen.
- Una herramienta más aumenta la superficie MCP; es de solo lectura y reutiliza las validaciones del lote.

## Plan de pruebas

Pruebas unitarias con simulación (consultas leídas del archivo, binds, estructura de salida, fallo cerrado, versiones sin una vista) y validación en vivo en TEST de solo lectura. La medición de tiempo usa el registro de sesión: ejecutar la revisión en una conversación nueva y, en la misma conversación, pedir el cálculo de marcas de hora (total, hasta la primera herramienta, tiempo en herramientas, redacción final y resto del modelo) sin mostrar el contenido de los mensajes.

## Implementación sugerida (fases, cada una revisable por separado)

1. Convertir las consultas de página a un formato único compartido, con prueba de sincronía.
2. Implementar `inspect_apex_page` con pruebas.
3. Actualizar skills, adaptadores, documentación y changelog.
4. Validar en vivo y medir con el método anterior.

## Compatibilidad, rollback y descontinuación

Compatible con Windows y SQLcl 26.2.2 (los verificados); no cambia Oracle, APEX ni credenciales. Rollback: revertir los commits de la herramienta y de las skills; el lote libre sigue disponible. Descontinuación: retirar la herramienta si una sesión persistente o un cambio de versión de APEX la hiciera innecesaria.

## Backlog relacionado (pendiente, sin implementar)

- Guarda de credenciales: que un carácter fuera de CP1252 en usuario o contraseña falle cerrado también en lecturas tolerantes (hoy se sustituiría y produciría un login fallido).
- Mensaje de `runtime-state.json` corrupto o ilegible: hoy se reporta como `RUNTIME_NOT_INSTALLED`.
- Tiempo por consulta dentro del lote: el intento con `set timing on` no capturó datos; **[Inferencial]** SQLcl en español imprime "Transcurrido:" en lugar de "Elapsed:".
- Pilotos de comportamiento del modo paso a paso (escenarios a a e de `docs/PRUEBAS-COMPORTAMIENTO-PASO-A-PASO.md`).
- Verificar la documentación oficial de Codex sobre subagentes (no se pudo acceder por la política de red de la sesión).
- Sesión SQLcl persistente, solo si el tiempo total sigue sin cumplir la meta tras esta herramienta.
