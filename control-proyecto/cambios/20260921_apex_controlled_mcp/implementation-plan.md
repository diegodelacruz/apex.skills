# Plan de implementación — MCP controlado y diagnóstico de privilegios

- [x] Definir runtime per-user de Java/SQLcl, manifiesto e integridad.
- [x] Implementar y verificar handshake local del MCP STDIO.
- [x] Registrar `apex-controlled` sin modificar registros heredados.
- [x] Confirmar identidad TEST por lectura: `DDELACRUZ` / `DDELACRUZ`.
- [x] Ejecutar `sql/01_inspeccion_privilegios.sql` en TEST. Evidencia:
      sesión `DDELACRUZ`/`DDELACRUZ`; privilegios efectivos incluyen
      `CREATE`, `ALTER`, `DROP`, `INSERT`, `UPDATE` y `DELETE ANY TABLE`.
- [ ] Presentar privilegios observados y proponer una prueba temporal de
      escritura con objeto, reversión y validación exactos.
- [ ] Ejecutar la prueba de escritura sólo tras confirmación paso a paso.

## Validación y rollback

La validación de la consulta es su salida Oracle y el registro local de
ejecución sin secretos. No existe rollback para una consulta. Una futura
prueba de escritura incluirá un objeto temporal y eliminación explícita sólo
después de verificar el resultado.

## Hallazgo de auditoría pendiente

- [ ] B608 documentado en `decisions.md`: Bandit identifica interpolación de
      `application_id` en la consulta de contexto APEX. La ruta pública valida
      entero positivo y no se demostró explotación, pero el hallazgo no se
      corrige en este cambio. Requiere revisión independiente y decisión de
      publicación antes de declarar el control de seguridad en `PASS`.

## Evidencia local

El runtime per-user verificó Temurin Java 21 y SQLcl 26.2.2.233.1901. El
handshake STDIO pasó sin conexión Oracle. La suite completa registró 461
pruebas correctas, las auditorías de ecosistema/calidad pasaron y la auditoría
de seguridad pasó después de excluir sólo la huella pública del runtime y la
bitácora generada sin secretos.
