# Uso de APEX Skills desde Codex CLI

Antes de modificar este repositorio, consulte la [política de evolución](POLITICA-EVOLUCION-ECOSISTEMA.md).

El inicializador prepara recursos locales y reporta los estados de perfiles.
No cambia registros MCP existentes. Un estado faltante o fallido del bootstrap
no limita MCP, SQLcl, App Builder u otros canales configurados.

Use cualquier MCP Oracle/APEX registrado, incluido
`run_apex_mcp_with_profile.py` con el ambiente elegido. Una solicitud directa
del usuario no requiere aprobación adicional de una skill. La conexión y sus
privilegios reales determinan el resultado. Mantenga los secretos en el
archivo `.env` local ignorado por Git en la raíz del repositorio.
