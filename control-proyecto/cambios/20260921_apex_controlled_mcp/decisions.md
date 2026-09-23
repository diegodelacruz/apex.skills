# Decisiones — MCP controlado y diagnóstico de privilegios

## Objetivo y alcance

Comprobar en TEST el runtime local, identidad Oracle y privilegios efectivos
de la cuenta conectada a través de `apex-controlled-mcp`. La primera ejecución
validada fue sólo de lectura. El servidor también expone ejecución de artefactos
SQL y despliegue de exports APEX mediante herramientas marcadas como destructivas;
no se invocan durante el setup. El cliente debe solicitar confirmación para esas
herramientas y Oracle conserva la autoridad final de permisos.

## Decisiones aplicables

- La cuenta Oracle autenticada es la fuente de verdad para permisos. Un
  perfil, workspace o script no constituye una concesión de privilegios.
- El MCP expone SQL versionado dentro del repositorio, no SQL en línea ni DML
  directo sobre `APEX_240100.WWV_FLOW_*`. Los artefactos ejecutables pueden
  contener DDL/DML ordinario; su selección y confirmación deben corresponder a
  la petición explícita del usuario.
- TEST es el ambiente inicial. Producción no se sondea ni modifica en esta
  actividad.
- Una prueba posterior de escritura se hará paso a paso, sobre un objeto
  temporal explícito en el esquema observado y con su reversión documentada.

## Riesgos y reversión

La consulta de privilegios lee vistas de sesión y diccionario. No tiene
transacción ni rollback porque no altera datos. Si Oracle niega una vista, el
resultado se conserva como evidencia de permiso insuficiente, no como fallo
genérico ni como éxito.

## Hallazgo de seguridad documentado — B608

El 2026-09-22 Bandit reportó `B608` en
`scripts/apex_controlled_mcp.py`, función `_apex_context_query`, por formar
la consulta de metadatos con una f-string que incorpora `application_id`.

- **Alcance observado:** la ruta MCP pública `inspect_apex_context` acepta
  únicamente un entero positivo antes de invocar la función; no se demostró
  una inyección explotable por esa ruta.
- **Riesgo residual:** la consulta sigue dependiendo de que toda llamada futura
  conserve esa validación, y Bandit no considera dicha validación una
  sustitución de parámetros enlazados.
- **Corrección:** la consulta usa `:application_id` como variable enlazada de
  SQLcl; el valor entero se inicializa en un bloque PL/SQL separado después de
  validar nombre y tipo del bind.
- **Validación:** se añadió una prueba que inspecciona el script SQLcl generado
  y confirma que el ID no se interpola en la consulta.
