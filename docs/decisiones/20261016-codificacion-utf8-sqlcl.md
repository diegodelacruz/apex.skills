# Decisión: codificación entre Python y SQLcl en Windows

## Objetivo y alcance

Corregir la comunicación de `scripts/apex_controlled_mcp.py` con el SQLcl
administrado en Windows sin cambiar Oracle, APEX, credenciales ni SQL de
mutación. El cambio aplica a la codificación de entrada y salida de
`sqlcl_result` y al cierre de entrada de las rutas de escritura.

## Evidencia inicial (F0)

El 2026-10-16 en TEST, Python y la consola informaron `cp1252`. La base
reportó `NLS_CHARACTERSET=WE8MSWIN1252`. Con la implementación inicial,
SQLcl produjo un `UnicodeDecodeError` al intentar Python leer `0x81` como
CP1252; después de forzar ambos sentidos a UTF-8, la salida
`óÁÑü` se leyó correctamente pero las cuatro comparaciones de entrada
(`ó`, `Á`, `Ñ`, `ü`) devolvieron `KO`.

La inspección local de SQLcl 26.2.2.233.1901 confirmó que `SET ENCODING`
existe. `set encoding utf8` no cambia la interpretación del `stdin`, pero,
enviado como comando ASCII antes de conectar, sí hizo que la salida fuera
UTF-8 cuando la entrada se normalizó a CP1252. `LANG=en_US.UTF-8` no cambió la
entrada; `JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8` tampoco corrigió las
comparaciones y añadió `Picked up JAVA_TOOL_OPTIONS` a `stderr`.

Al enviar la entrada como CP1252 y decodificar los bytes de salida como UTF-8,
las cuatro comparaciones devolvieron `OK`; la implementación de ese momento
normalizaba también `→` a `?`. La salida UTF-8 tolerante conserva `óÁÑü` y
convierte bytes inválidos en el carácter de reemplazo, evitando que oculten el
resultado del proceso.

La comparación con el padre de `2dab8ff` verificó que antes de esa
normalización `sqlcl_result` pasaba `input=script` con `text=True` y sin
`encoding`/`errors` explícitos. En Windows CP1252, un `→` provocaba
`UnicodeEncodeError` al preparar stdin y SQLcl no se iniciaba. Por tanto, la
afirmación previa de que no cambiaban las rutas de escritura era inexacta:
`2dab8ff` permitió que un literal mutativo no representable llegara como `?`.

El dato real solicitado no estuvo disponible: TEST 109.131 devolvió los
botones `AGREGAR`, `Codigos_ISD` y `HISTORICO`; por tanto, el predicado exacto
`button_name = 'Histórico'` devolvió cero filas. Es una discrepancia observada
de metadata, no evidencia de una falla de codificación ni autorización para
modificar APEX.

## Decisión y alternativas

Se envía primero `set encoding utf8`, se usa `surrogateescape` para recuperar
los bytes de sus flujos y se decodifican como UTF-8 con reemplazo. Por defecto,
`sqlcl_result` cuenta los caracteres no representables en CP1252 y devuelve
`UNREPRESENTABLE_CHARACTERS` antes de iniciar el proceso o abrir una conexión.
Las rutas de escritura (`execute_sql_file`, bundle y despliegue APEX) conservan
sus gates y además revisan sus artefactos antes de ejecutar cualquier fase. Solo
`execute_readonly_query` y `execute_readonly_batch` pasan `strict_input=False`:
pueden sustituir explícitamente y devuelven `input_substitutions`, por lo que
sus literales sustituidos no deben interpretarse como predicados semánticos.
Esto preserva los literales españoles representables y mantiene `stderr` limpio.

Se descartaron UTF-8 en ambos sentidos (entrada `KO`), `LANG` (sin efecto) y
`JAVA_TOOL_OPTIONS` (sin efecto y con ruido en `stderr`). No se incorporan
dependencias, upstreams, variables Java persistentes ni opciones de SQLcl no
verificadas.

## Riesgos, compatibilidad y rollback

Los caracteres fuera de CP1252 se reemplazan solo en lecturas explícitamente
tolerantes, por lo que no son seguros para predicados semánticos. Las escrituras
fallan cerradas antes de SQLcl. La compatibilidad verificada corresponde a
Windows, Python 3.13 y SQLcl 26.2.2.233.1901. El rollback es revertir las
funciones de normalización/decodificación y su gate de entrada en
`scripts/apex_controlled_mcp.py`; no requiere cambio de base, backup ni
restauración.

## Validación

La regresión nueva cubre la salida real de un hijo UTF-8 leída como texto
CP1252 con `surrogateescape`, la entrada real de bytes `ó`/`ñ`, el cierre de
SQL, bundle y despliegue con `→`, la sustitución contada del lote de lectura y
los acentos CP1252. La revalidación TEST es solo lectura y se registra junto
con este cambio. Queda pendiente la revisión independiente obligatoria antes de
integrar.
