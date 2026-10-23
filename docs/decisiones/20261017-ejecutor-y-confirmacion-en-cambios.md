# Decisión: quién ejecuta un cambio y qué cuenta como confirmación

- **Fecha:** 2026-10-17
- **Estado:** pendiente de revisión independiente
- **Objetivo y necesidad:** el piloto del 2026-10-16 (escenario `a` de `docs/PRUEBAS-COMPORTAMIENTO-PASO-A-PASO.md`) mostró que Codex ejecutó un DDL con `confirmed=true` a partir de una orden descriptiva, sin entregar el paso al usuario ni esperar `confirmado`. El protocolo no definía quién ejecuta y varios documentos se contradecían.
- **Evidencia de la contradicción:** `skills/apex/SKILL.md` decía «trata la respuesta completa como la única confirmación»; `docs/MCP-CONTROLADO-SQLCL.md`, `docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md` y `docs/MANUAL-DE-USO.md` decían que la solicitud directa autoriza el alcance sin aprobación adicional. La decisión vigente `20261012-lecturas-inmediatas-mutaciones-confirmadas.md` descarta eliminar toda confirmación. La memoria de Codex reproducía las reglas permisivas.
- **Alcance:** instrucciones y documentos de Oracle/APEX, escenarios de prueba y regresiones. No cambia `scripts/apex_controlled_mcp.py`, herramientas, credenciales ni datos. Fuera de alcance: gestión de la memoria de los agentes.
- **Decisión:**
  1. Una orden descriptiva no es confirmación ni indica ejecutor.
  2. Con frase explícita de ejecución por el agente (`hazlo tú`, `solo hazlo`, `ejecútalo`, `aplícalo`) más ambiente, objeto, acción y backup sí/no, la petición es la confirmación única.
  3. Sin esa frase, `paso a paso` es ejecución del usuario y el agente no usa herramientas de escritura; en `todos los pasos` se pregunta el ejecutor.
  4. `confirmed=true` solo con la regla 2 o tras una respuesta afirmativa a una confirmación presentada.
  5. La regla prevalece sobre notas de memoria o preferencias aprendidas.
- **Alternativas:** dejar la regla implícita, descartado porque falló en el piloto; exigir siempre una pregunta aparte, descartado porque contradice «solo hazlo» y añade un turno innecesario; endurecer solo el MCP, descartado porque no autentica a quien respondió.
- **Impacto y riesgos:** un turno extra cuando la orden es descriptiva y se desea ejecución por el agente. Una frase no incluida en la lista se tratará como descriptiva. El cumplimiento depende del agente; se verifica con la regresión `a`.
- **Compatibilidad:** conserva los gates `confirmed` y `backup_choice`, la lectura inmediata y la decisión del 2026-10-12.
- **Validación:** pruebas de documentos y regresión en vivo en TEST con el prompt exacto del escenario `a`.
- **Rollback:** revertir los documentos, pruebas y esta decisión; no hay datos que restaurar.
- **Descontinuación:** revisar si se incorpora una aprobación autenticada.
