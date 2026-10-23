# Mapa de trazabilidad: <id del caso>

Plantilla de [la metodología TE2E](../references/trazabilidad-end-to-end.md).
El mapa es un documento Markdown para personas, sin un bloque de datos
duplicado. No incluyas credenciales ni datos sensibles; si un atributo
identifica a una persona, usa solo su llave técnica.

## Encabezado

| Campo | Valor |
|---|---|
| Ambiente e identidad verificada | <ambiente> · <usuario de sesión / servicio> |
| Fecha y hora del diagnóstico | <AAAA-MM-DD HH:MM> |
| Registro testigo | <llave en origen> · <atributos discriminantes> |
| Testigo de control | <llave en origen> · <atributos> · o "no existe: <razón>" |
| Resultado esperado | <punto de observación> · <valor> · <forma> |
| Resultado observado | <qué se ve> · <parámetros, filtros, usuario, momento> |
| Proceso o ejecución relacionada | <corrida / lote / tarea> · o "N/A: flujo síncrono" |
| Modo | ligero / completo |

## Etapas

| Id | Tipo | Artefacto (versión desplegada) | Llave entrada → salida | Cardinalidad | Sincronía | Condiciones | Representación esperada | Sonda | Estado | Conforme |
|---|---|---|---|---|---|---|---|---|---|---|
| E0 | fuente | | | — | — | — | fila | S0 | NO_VERIFICADO | — |
| E1 | | | | | | | fila / contribución / compensación | | NO_VERIFICADO | — |
| En | presentacion | | | | | | | | NO_VERIFICADO | — |

## Linaje de llaves

| Salto | De → a | Correlación | Evidencia |
|---|---|---|---|
| E0→E1 | `<llave_origen>` → `<llave_e1>` | exacta / determinista / por_atributos / inferida | S<n> |

## Ramas podadas

| Rama | Razón |
|---|---|
| | |

## Evidencia por etapa

```text
S0 · Etapa E0 · adelante
Pregunta:       ¿El testigo existe en el origen con los atributos declarados?
Sonda:          <lectura>, acotada por <llave>; límite <n filas>
Ambiente:       <ambiente> · identidad verificada
Momento:        <fecha y hora> · versión del artefacto <…>
Resultado:      <hecho observado>
Esperado aquí:  <valor o forma>
Control:        <resultado del control>
Estado:         PRESENTE | ALTERADO | AUSENTE | AGREGADO | NETEADO | PENDIENTE | NO_OBSERVABLE
Conforme:       sí | no (testigo) · sí | no (control)
Interpretación: <inferencia o "ninguna">
Costo:          <filas / tiempo>
```

## Veredicto

| Campo | Valor |
|---|---|
| Primera divergencia | E<k> (<tipo>) · o intervalo [E<i>, E<j>] |
| Clasificación | D0 NO_EXISTE_EN_FUENTE / D1 NO_LEIDO / D2 LEIDO_EXCLUIDO / D3 TRANSFORMADO / D4 PERSISTIDO_NO_CONSOLIDADO / D5 CONSOLIDADO_NO_VISIBLE / D6 AGREGADO_NETEADO / D7 PENDIENTE / DX EXPECTATIVA_INCORRECTA |
| Certeza | causa raíz confirmada / causa probable / limitación de evidencia |
| Mecanismo | <regla, condición, cruce, mapeo o ventana concreta en E<k>> |
| Evaluación sobre testigo y control | <resultado predicho vs. observado> |
| Hipótesis no verificadas | <rotuladas como hipótesis> |
| Evidencia faltante | <qué sonda cerraría la duda> |
| Rondas y costo | <n rondas> · <justificación a partir de la cuarta> |
