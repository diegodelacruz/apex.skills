# Trazabilidad End-to-End (TE2E)

Metodología agnóstica de dominio para diagnosticar un dato que existe en un
origen y no aparece, o aparece incorrectamente, en un punto de observación
(pantalla, reporte, proceso, interfaz, archivo o tabla destino). Este documento
no depende de una tecnología: las sondas concretas de cada plataforma viven en
adaptadores separados, por ejemplo [el adaptador de esta skill](trazabilidad-adaptador-oracle-apex.md).
El formato de entrega está en [la plantilla del mapa](../assets/mapa-trazabilidad.template.md).

Principio rector: **no se declara una causa antes de seguir un registro real
hasta la primera etapa verificable donde diverge.**

## 1. Cuándo aplica

- **Disparador:** discrepancia de datos entre un origen y un punto de
  observación: falta un registro, sobra, está duplicado, tiene otro valor, un
  total no cuadra, o "en A sí y en B no".
- **No aplica** a lecturas simples, errores de ejecución sin discrepancia de
  datos ni problemas de rendimiento.
- **Modo ligero:** si entre el origen y el punto de observación hay como máximo
  dos etapas (por ejemplo, una sola consulta), basta el contrato, una ronda de
  sondas y el veredicto con su evidencia, sin mapa formal. El mapa completo es
  obligatorio con tres o más etapas, o cuando la primera ronda no localiza la
  divergencia.
- La TE2E es un diagnóstico: se ejecuta de inmediato y en solo lectura.

## 2. Contrato de entrada mínimo

| Campo | Obligatorio | Si falta |
|---|---|---|
| **Registro testigo**: identificador en el origen más dos o tres atributos discriminantes (fecha, importe, tipo) | Sí | Derivar un candidato con la lectura más estrecha posible a partir del síntoma. Preguntar solo si no se puede acotar. |
| **Testigo de control**: registro análogo al testigo que sí aparece correctamente | Sí | Buscar uno con los mismos atributos discriminantes salvo el sospechoso. Si no existe, declararlo: el veredicto queda limitado a causa probable (§8). |
| **Resultado esperado**: en qué punto, con qué valor y con qué forma (fila individual, parte de un total, oculto por regla) | Sí | Pedirlo. Sin expectativa no hay divergencia que medir. |
| **Resultado observado**: qué se ve, con qué parámetros, filtros, usuario o rol y en qué momento | Sí | Reconstruirlo desde la descripción y rotularlo como supuesto. |
| **Proceso o ejecución relacionada**: corrida, lote, fecha de corte, tarea programada | Si el flujo es asíncrono | Descubrir la última ejecución relevante. |
| **Ambiente** | Sí | Usar el ambiente predeterminado del repositorio y declararlo. |

Si la expectativa contradice una regla de negocio documentada u observada, el
veredicto puede ser `DX EXPECTATIVA_INCORRECTA` (§7), no un defecto.

## 3. Mapa de trazabilidad

El mapa describe el recorrido real que el testigo **debería** seguir. Se
compone de un encabezado, una tabla de etapas, el linaje de llaves, las ramas
podadas, la evidencia por etapa y el veredicto, todo en Markdown.

**Tipos de etapa** (cerrados): `fuente`, `extraccion`, `filtro`,
`transformacion`, `persistencia_intermedia`, `consolidacion`, `presentacion`.
Si un mismo artefacto realiza varios tipos, se separan como etapas distintas.

**Estados de etapa:**

| Estado | Significado |
|---|---|
| `NO_VERIFICADO` | Aún no se observó. |
| `PRESENTE` | El testigo está con la llave y el valor esperados en esta etapa. |
| `ALTERADO` | El testigo está, pero con otra llave, otro valor u otro tipo. |
| `AUSENTE` | Una sonda bien acotada, con identidad que puede ver la etapa, no lo encontró. |
| `AGREGADO` | El testigo contribuye a un grupo y ya no tiene identidad individual. |
| `NETEADO` | El testigo se compensa con una contrapartida dentro del grupo. |
| `PENDIENTE` | La etapa asíncrona que debía procesarlo aún no corrió o no terminó. |
| `NO_OBSERVABLE` | No hay forma de observar la etapa: no persiste, no hay registro, falta privilegio o el dato fue sobrescrito. |

**Linaje de llaves:** cadena explícita `llave_origen → … → llave_visible`. Cada
salto declara su correlación:

- `exacta`: llave o tabla de mapeo persistida;
- `determinista`: función que puede recomputarse sobre el testigo;
- `por_atributos`: coincidencia por fecha, importe, ventana temporal u otros
  atributos;
- `inferida`: deducida sin evidencia directa.

**Ramas podadas:** cada rama del flujo descartada se lista con su razón, por
ejemplo "no lee la fuente del testigo".

## 4. Evidencia por etapa

Un bloque por sonda ejecutada:

```text
S<n> · Etapa E<k> · <dirección: atras | adelante | diferencial>
Pregunta:       ¿El testigo está en la entrada/salida de E<k> con valor V?
Sonda:          <lectura, archivo o registro consultado>, acotada por <llave>; límite <n filas>
Ambiente:       <ambiente> · identidad <verificada | reutilizada de S<m>>
Momento:        <fecha y hora de la sonda> · versión del artefacto observada
Resultado:      <hecho observado, resumido, sin datos sensibles>
Esperado aquí:  <valor o forma esperada en esta etapa>
Control:        <resultado del testigo de control en la misma sonda>
Estado:         PRESENTE | ALTERADO | AUSENTE | AGREGADO | NETEADO | PENDIENTE | NO_OBSERVABLE
Interpretación: <inferencia separada del hecho; "ninguna" si no aplica>
Costo:          <filas leídas aproximadas / tiempo>
```

Reglas de evidencia:

- **Resultado** contiene solo hechos observados; toda inferencia va en
  **Interpretación**.
- Un "sin filas" vale como `AUSENTE` solo si la sonda usó la llave correcta
  según el linaje y una identidad que puede ver esa etapa. En otro caso, el
  estado es `NO_OBSERVABLE`.
- Una sonda que falla porque el objeto no existe o no es accesible deja la
  etapa `NO_OBSERVABLE` por esa vía, nunca `AUSENTE`. Los nombres sin
  calificar dentro de un artefacto se resuelven en el contexto de su
  propietario, no en el de la sesión de diagnóstico: hay que repetir la sonda
  con el nombre calificado que reporte el descubrimiento de dependencias.
- Los parámetros de presentación (filtros, fechas, valores de sesión) se
  reemplazan por los valores que usó quien observó el síntoma. Si no se
  conocen, se declaran como supuesto en el bloque de evidencia.
- Se observa la **versión desplegada** del artefacto en el ambiente, no la del
  repositorio. Si difieren, se registra.
- La memoria de sesiones anteriores es una pista de búsqueda, nunca una etapa
  verificada.

## 5. Procedimiento

1. **Contrato.** Completar §2 con el testigo y el testigo de control.
2. **Verificar extremos** (barato y obligatorio). Comprobar que el testigo
   existe en la fuente (E0) y que el síntoma se reproduce en la presentación
   (En) con los mismos parámetros. Si E0 está `AUSENTE`, se cierra como
   `D0 NO_EXISTE_EN_FUENTE`. Si En sí lo muestra, el síntoma no se reproduce:
   revisar parámetros, usuario y momento antes de seguir.
3. **Descubrir el flujo** (§6) desde ambos extremos hasta obtener una cadena
   continua E0…En. Los huecos quedan como `NO_VERIFICADO`.
4. **Recorrer el flujo:**
   - *hacia atrás:* punto visible → su fuente o consulta → quién escribe esa
     fuente → qué lee quien escribe → … → origen;
   - *hacia adelante:* testigo en el origen → quién lo lee → dónde lo escribe →
     … → punto visible;
   - con cuatro o más etapas, **bisección:** sondear primero la etapa
     intermedia observable más barata y reducir el intervalo
     [última `PRESENTE`, primera distinta de `PRESENTE`].
5. **Localizar la primera divergencia:** la etapa `k` donde E(k-1) está
   `PRESENTE` con llave y valor correctos y E(k) tiene otro estado, ambas
   observadas sobre el mismo testigo con la correlación declarada. El testigo
   de control debe seguir `PRESENTE` en E(k); si también diverge, el problema
   no es específico del testigo y se replantea la expectativa o el control.
6. **Explicar el mecanismo de `k`.** Identificar la regla, condición, cruce,
   mapeo o ventana concreta y **evaluarla contra los valores del testigo y del
   control** con una lectura que replique la lógica. El mecanismo debe predecir
   el resultado observado para el testigo y el correcto para el control.
7. **Clasificar** (§7) y **declarar la certeza** (§8).
8. **Parar.** No sondear aguas abajo de `k` salvo para explicar el síntoma
   visible. Toda corrección sigue el protocolo de cambios del repositorio.

## 6. Descubrimiento dinámico de etapas

Las etapas se descubren desde los artefactos, sin suponer la arquitectura:

| Desde | Pregunta | Pistas genéricas |
|---|---|---|
| Pantalla o reporte | ¿De dónde lee y qué filtra? | Definición de la fuente o consulta, parámetros, filtros por defecto, seguridad por fila, paginación, caché |
| Vista o consulta | ¿Qué objetos usa y cómo los cruza? | Texto de la definición, dependencias declaradas, cruces obligatorios (descartan filas sin pareja), predicados |
| Tabla o almacén | ¿Quién la escribe? | Código que inserta, actualiza o fusiona, disparadores, cargas, replicación |
| Código o proceso | ¿Qué lee, qué escribe, cuándo corre? | Búsqueda acotada de nombres de objetos y campos, planificadores, colas, registros de ejecución |
| API o servicio | ¿Qué contrato y qué transformación aplica? | Especificación, mapeos, registros de solicitud y respuesta correlacionados por identificador |
| Archivo | ¿Qué layout y qué selección tiene? | Especificación de columnas, encabezados, reglas de rechazo, archivos de error |

El mapa es **suficiente** cuando existe una cadena continua por la que el
testigo debería pasar. No hace falta mapear el sistema completo.

## 7. Taxonomía de divergencia

Toda conclusión se clasifica con uno de estos códigos y su evidencia mínima:

| Código | Significado | Evidencia mínima |
|---|---|---|
| `D0 NO_EXISTE_EN_FUENTE` | El testigo no existe en el origen declarado. | Sonda acotada en E0 con identidad válida sin resultados; llave confirmada con quien reporta o con un segundo atributo. |
| `D1 NO_LEIDO` | Existe, pero la extracción no lo alcanzó (ventana, marca de agua, partición, conexión, origen equivocado). | E0 `PRESENTE`, ausente en la salida de la extracción y criterio de alcance evaluado contra el testigo. |
| `D2 LEIDO_EXCLUIDO` | Entró a una etapa y un filtro, validación o cruce lo descartó. | Presente en la entrada de `k`, ausente en su salida y condición concreta evaluada como falsa para el testigo, o registro de rechazo. |
| `D3 TRANSFORMADO` | Cambió la llave, el valor, el tipo, el redondeo o el mapeo. | Valor correcto en `k-1`, distinto en `k`, y regla que produce exactamente el valor observado. |
| `D4 PERSISTIDO_NO_CONSOLIDADO` | Está en la persistencia intermedia, pero no en la consolidación. | Presente en la intermedia, ausente en la consolidada y causa ubicada en la etapa de consolidación. |
| `D5 CONSOLIDADO_NO_VISIBLE` | Está en el destino final, pero la presentación lo oculta (parámetros, seguridad, paginación, caché). | Presente en la fuente de la presentación y predicado o regla de presentación evaluado contra el testigo. |
| `D6 AGREGADO_NETEADO` | Contribuye correctamente, pero sin identidad individual, o se compensa con una contrapartida. | Grupo calculado para el testigo, agregado recomputado solo para ese grupo y, si hay neteo, contrapartida identificada. |
| `D7 PENDIENTE` | La etapa asíncrona que debía incluirlo aún no corrió, sigue en curso o falló. | Última ejecución, su estado y su marca de agua comparados con el momento del testigo. |
| `DX EXPECTATIVA_INCORRECTA` | El flujo cumple su regla y la expectativa era otra. | Regla documentada u observada que produce el resultado visto. |

**D1–D6 frente a DX.** El mismo mecanismo puede ser un defecto o el diseño
previsto: por ejemplo, un filtro de presentación que solo muestra registros
cerrados. Si el diagnóstico confirma el mecanismo, pero no hay una regla de
negocio documentada que diga si debe existir, se clasifica con el código
D1–D6 que corresponda y se informa `DX` como alternativa. Se indica qué regla
o qué responsable debe decidirlo. La certeza sobre el **mecanismo** no cambia;
lo que queda abierto es si es un **defecto**. No se elige `DX` en silencio.

## 8. Criterios de cierre

- **Causa raíz confirmada.** Se cumplen todas:
  1. primera divergencia localizada con correlación `exacta` o `determinista`;
  2. mecanismo concreto identificado en `k`;
  3. mecanismo evaluado sobre el testigo, prediciendo el resultado observado;
  4. el mismo mecanismo evaluado sobre el testigo de control predice su
     resultado correcto;
  5. no hay evidencia contradictoria.
- **Causa probable.** Se cumplen 1 y 2, pero falta 3 o 4, la correlación es
  `por_atributos` o `inferida`, o no existe testigo de control. Se indica qué
  sonda la confirmaría.
- **Limitación de evidencia.** Hay una etapa `NO_OBSERVABLE` dentro del
  intervalo. Se declara el intervalo [E(i), E(j)] donde está la divergencia y
  la evidencia que lo cerraría. No se elige una causa.
- **Regla anti-configuración.** "Configuración", "filtro", "permisos" o
  "parametrización" no pueden declararse causa raíz ni causa probable sin
  haber completado los pasos 5 y 6 sobre un registro real. Antes de eso solo
  pueden aparecer rotuladas como **hipótesis**.
- **Anti-patrones prohibidos:**
  - concluir a partir de una lectura amplia sin resultados;
  - "probar" cambiando un filtro, parámetro o configuración persistida;
  - asumir que el código del repositorio es el desplegado;
  - convertir memoria histórica en evidencia;
  - saltar etapas intermedias observables para declarar la causa en una
    posterior.

## 9. Flujos complejos

- **Llaves transformadas.** Mantener el linaje salto por salto. Recomputar las
  funciones deterministas sobre el testigo. Si la nueva llave no es
  recomputable (secuencias, identificadores generados), correlacionar por
  atributos y ventana temporal y bajar la certeza máxima a causa probable,
  salvo que exista una tabla de mapeo persistida.
- **Agregaciones.** El testigo pasa a ser una contribución. Verificar la llave
  de grupo calculada para el testigo, recomputar el agregado solo para ese
  grupo y comparar el total con y sin el testigo.
- **Neteos.** Buscar la contrapartida dentro del mismo grupo (signo opuesto,
  reverso, anulación). Un registro neteado no está `AUSENTE`: está `NETEADO`.
- **Procesos asíncronos.** Identificar el disparador, la programación, la
  última ejecución, su estado y su marca de agua o cursor incremental. No
  declarar `AUSENTE` antes de que haya terminado la ejecución que debía
  incluirlo; hasta entonces el estado es `PENDIENTE`.
- **Múltiples fuentes.** Un testigo por rama relevante. Revisar en los cruces
  si existe la pareja del testigo y, en uniones o deduplicaciones, la regla de
  prioridad que decide qué registro sobrevive.
- **Datos temporales o versionados.** Comparar las fechas de vigencia del
  testigo con la fecha de consulta de cada etapa.
- **Resultados precalculados o en caché.** Registrar el momento del último
  refresco y compararlo con el momento del testigo.

## 10. Reglas de costo

1. Toda sonda se acota por la llave del testigo (o por su grupo o ventana en
   etapas agregadas) y lleva un límite de filas.
2. No usar conteos totales, proyecciones completas ni recorridos de tablas o
   registros grandes sin ventana temporal. Las búsquedas en el código se acotan
   por propietario, tipo de objeto y nombre.
3. Agrupar las sondas de una ronda en un solo lote de solo lectura cuando la
   plataforma lo permita. Cada ronda responde una pregunta sobre el intervalo.
4. Primero lo barato: extremos, después bisección. Detenerse en la primera
   divergencia.
5. Presupuesto: hasta tres rondas sin justificación adicional. A partir de la
   cuarta, indicar qué pregunta responde cada ronda.
6. En producción rigen las mismas reglas, con especial cuidado en registros e
   historiales.

## 11. Solo lectura

Durante la TE2E todo es lectura. No se crean objetos de apoyo, no se reejecutan
procesos, tareas ni APIs para "ver qué pasa" y no se cambian parámetros
persistidos. La simulación se hace con lecturas que replican la lógica. Si el
usuario autoriza explícitamente una corrección, el contexto (mapa, etapa `k` y
mecanismo) se conserva y pasa al protocolo de cambios sin repetir el
descubrimiento.

## 12. Ejemplos genéricos

1. **Archivo → staging → consolidado → tablero.** Un registro del archivo no
   se ve en el tablero. Los extremos dan E0 `PRESENTE` y En `AUSENTE`. Por
   bisección, staging y consolidado están `PRESENTE`. La fuente del tablero
   filtra `fecha_proceso = hoy` y el testigo tiene la fecha de carga de ayer,
   mientras que el control de hoy aparece → `D5 CONSOLIDADO_NO_VISIBLE`, causa
   raíz confirmada.
2. **API → cola → servicio → base de datos, con llave transformada.** Un pedido
   aparece con otro importe. El linaje `id_pedido → id_mensaje → id_interno`
   está persistido (correlación `exacta`). La cola tiene el importe original y
   el destino el alterado. La regla de conversión usa el tipo de cambio de la
   fecha de proceso en vez de la del pedido; al recomputarla se obtiene el
   importe observado, y el control (misma moneda) no cambia → `D3 TRANSFORMADO`,
   causa raíz confirmada.
3. **Movimientos → agregado diario → reporte.** Un movimiento "no suma". La
   llave de grupo (cuenta, día) es correcta y hay un reverso con signo opuesto
   en el mismo grupo → `D6 AGREGADO_NETEADO` si el neteo es un error, o
   `DX EXPECTATIVA_INCORRECTA` si la regla documentada lo exige.
4. **Limitación.** Una transformación en memoria sin persistencia intermedia
   ni registro deja el intervalo [extracción `PRESENTE`, consolidado `AUSENTE`].
   Se declara la limitación de evidencia y lo que la cerraría: un registro de
   la etapa o una lectura que replique la transformación sobre la entrada.
