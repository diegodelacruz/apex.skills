# Modo paso a paso / todos los pasos

Este protocolo aplica únicamente a cambios de objetos Oracle/APEX o a desarrollos. Las lecturas y diagnósticos siguen la lectura inmediata: no piden confirmaciones ni activan este flujo.

## Pregunta inicial y línea base

Antes de la primera escritura, pregunta una sola vez por el **ambiente**, **objeto**, **acción**, `backup sí/no` y modo: **paso a paso** (predeterminado) o **todos los pasos**. No se infiere `no` de silencio. La decisión de backup se conserva para el cambio y solo se vuelve a preguntar si cambia objeto o alcance.

En la misma llamada a `execute_readonly_batch` que verifica identidad/destino, obtén la línea base una vez por objeto afectado. Conserva valor/origen para una eventual reversión, pero no expliques rollback de rutina. Compara **antes → después → esperado**. Si antes ya coincide con lo esperado, advierte que no se puede probar el cambio y propone una variante distinguible.

```
LECTURA ──cambio solicitado──> DECISIÓN INICIAL ──> LÍNEA BASE
   ^              |                         |             |
   └── solo leer ─┘                         └── falta dato ─┘ pregunta puntual
```

## Paso a paso

El agente presenta exactamente un paso, quién lo ejecuta y su resultado esperado. Normalmente el usuario guarda, compila o confirma y escribe `confirmado`. Entonces el agente ejecuta una sola validación de solo lectura con `execute_readonly_batch`, muestra la consulta y el resultado observado.

```
PROPONER UN PASO → USUARIO EJECUTA → CONFIRMADO → VALIDAR → PASS → ¿continúo?
                                                    └ FAIL → DETENER
```

Si el usuario dice “hazlo tú”, el agente ejecuta solo ese paso con los gates vigentes (`confirmed=true` y `backup_choice=yes/no`), resume el resultado y pregunta si continúa. La pregunta **¿continúo?** entre pasos no viola la regla de una sola confirmación: cada paso es una unidad de alcance dentro de la decisión inicial. No solicita una nueva elección de backup salvo cambio de objeto o alcance. Máximo 5 iteraciones por cambio; al llegar al límite, detente y entrega estado y siguiente decisión necesaria.

Después de cada PASS muestra:

```
Paso N/5 — PASS
Ejecutor: usuario | agente
Cambio observado: <antes → después>
Validación: <SELECT de una línea>
Resultado: <salida observada>
¿Continúo con el siguiente paso?
```

Ante FAIL, sin rollback ni corrección automática: detente, muestra la consulta y observación, indica que el objeto queda como lo dejó el usuario y pregunta cómo seguir.

Un paso sin persistencia visible en metadatos (por ejemplo, una edición aún no guardada en App Builder) se marca **no verificable**; pide confirmar que fue guardado y no afirma PASS por una lectura indirecta.

## Todos los pasos

El agente entrega o ejecuta todos los pasos bajo la misma decisión inicial. Al final, hace una única llamada de validación consolidada con `execute_readonly_batch` y muestra PASS/FAIL por paso, comparación antes/después/esperado y resumen. Si algo falla, no corrige ni revierte de forma automática.

```
DECISIÓN INICIAL → LÍNEA BASE → PASOS 1..N → VALIDACIÓN CONSOLIDADA → RESUMEN
```

## Límites de evidencia

Las consultas son SELECT de una línea, con literales Oracle en mayúsculas. Para un identificador que contenga comilla simple, duplícala dentro del literal (`'O''BRIEN'`); no uses binds de texto en este protocolo. Las plantillas y el alcance de evidencia están en [consultas de validación](step-validation-queries.md).
