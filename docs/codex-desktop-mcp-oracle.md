# Oracle MCP en Codex Desktop

Codex Desktop registra servidores MCP por usuario, disponibles desde cualquier proyecto. Las skills guían el flujo; no crean por sí solas una conexión Oracle.

Use primero [el inicializador](inicializacion-automatica-codex.md). Si necesita registrar manualmente un servidor, reemplace `<RUTA_APEX_SKILLS>` por la ruta absoluta del repositorio:

```powershell
codex mcp add apex-mcp-test -- "<RUTA_APEX_SKILLS>\.venv\Scripts\python.exe" "<RUTA_APEX_SKILLS>\scripts\run_apex_mcp_with_profile.py" --environment test
```

Para un diagnóstico comparativo autorizado:

```powershell
codex mcp add apex-mcp-production -- "<RUTA_APEX_SKILLS>\.venv\Scripts\python.exe" "<RUTA_APEX_SKILLS>\scripts\run_apex_mcp_with_profile.py" --environment production
```

Compruebe el registro con `codex mcp list` y abra una tarea nueva en Codex Desktop. `Unsupported` en `Auth` es normal para un MCP local `stdio`; no representa un error.

El wrapper lee el perfil desde el keyring del sistema y no coloca secretos en `config.toml`, comandos, documentación, repositorios ni chat. APEX 24.1.3 limita el upstream 24.2 a inspección/dry-run hasta aprobar compatibilidad en TEST.
