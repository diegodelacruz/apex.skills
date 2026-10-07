# Decisión: taxonomía, compatibilidad y cobertura de auditoría

## Objetivo y necesidad

Resolver discrepancias actuales en el inventario de 31 `SKILL.md`, la
clasificación funcional, el estado retirado de `apex-api-client-safe`, los
adaptadores de comando y el alcance del auditor Markdown sin renombrar skills.
Las fachadas Python heredadas de REST y SQLcl deben fallar cerradas y no deben
conservar credenciales recibidas.

## Decisiones y alternativas

- Clasificar cada skill por su función primaria y documentar `status` como un
  eje separado. Resultado: 1 coordinador L0, 4 roles amplios L1, 3 flujos
  enfocados L2, 22 especialistas activos L3 y 1 entrada de compatibilidad
  retirada. La alternativa de contar la entrada retirada como especialista
  activo fue descartada porque atribuye una capacidad que no existe.
- Mantener los dos `order: 3.5` hasta verificar consumidores de descubrimiento
  externos. No hay lector ejecutable local conocido; la UI externa sigue sin
  evidencia. Cambiarlos a valores únicos podría alterar compatibilidad.
- Conservar la skill retirada y su nombre de invocación; agregar el comando
  Claude que faltaba para que todas las 31 carpetas tengan una ruta local
  equivalente.
- Si hay submódulos registrados, hacer fallar el auditor del padre hasta que
  cada raíz tenga auditoría anidada. Es preferible a contar contenido de otro
  repositorio bajo las reglas de rutas del padre.

## Impacto y riesgos

Las modificaciones sincronizan catálogos, routing, guías de contribución,
matriz de dependencias, arquitectura, changelog y una prueba de cobertura de
comandos. El adaptador nuevo invoca el `SKILL.md` existente; no cambia su
comportamiento. El validador sólo añade una condición de cobertura para futuros
submódulos. No se modificaron upstreams ni snapshots.

Riesgos pendientes: el orden externo no se puede confirmar desde este checkout;
el grafo de dependencias completo y sus ciclos aún no están probados; el host
no pudo validar directamente una URL de Anthropic por error TLS; no hay revisión
independiente en esta sesión. Por estas limitaciones, el resultado global es
`AUDIT_INCOMPLETE`.

## Validación y rollback

La validación ejecutada y el estado final de CI se reportan en la entrega de
esta tarea. El auditor cubre Markdown versionado y mantenido no versionado,
informa las exclusiones, y falla si detecta un submódulo sin raíz auditada.
Rollback: retirar el adaptador Claude y su regresión; revertir el chequeo de
submódulos, su prueba y el texto que lo describe; restaurar las versiones
anteriores de los documentos y el changelog, preservando por separado la línea
base de cambios preexistentes guardada en `%TEMP%`.
