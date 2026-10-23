# Uso de APEX Skills desde Codex CLI

Antes de modificar este repositorio, consulte la [política de evolución](POLITICA-EVOLUCION-ECOSISTEMA.md).

El inicializador prepara recursos locales y reporta los estados de perfiles.
No cambia registros MCP existentes. Un estado faltante o fallido del bootstrap
no limita MCP, SQLcl, App Builder u otros canales configurados.

Use cualquier MCP Oracle/APEX registrado, incluido
`run_apex_mcp_with_profile.py` con el ambiente elegido. Las lecturas son
inmediatas. Antes de una mutación rige la confirmación única y la regla de
ejecutor de [el protocolo paso a paso](../skills/apex/references/step-mode.md);
una orden descriptiva no es confirmación. La conexión y sus privilegios reales
determinan el resultado. Mantenga los secretos en el
archivo `.env` local ignorado por Git en la raíz del repositorio.
