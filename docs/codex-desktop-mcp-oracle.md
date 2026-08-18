# Oracle MCP en Codex Desktop

Codex Desktop registra los servidores MCP en la configuración del usuario, por lo que la configuración está disponible desde cualquier proyecto abierto por ese usuario. Las skills orientan al agente; no crean por sí mismas una conexión a Oracle.

Complete primero el bootstrap de [conexión segura a Oracle](conectar-agente-a-oracle.md), incluida la creación y validación del perfil `test`. Después, en PowerShell, ejecute el siguiente comando reemplazando las rutas si el repositorio está en otra ubicación:

```powershell
codex mcp add apex-mcp-test -- "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills\.venv\Scripts\python.exe" "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills\scripts\run_apex_mcp_with_profile.py" --environment test
```

Verifique el registro sin mostrar credenciales:

```powershell
codex mcp list
```

Abra una tarea nueva en Codex Desktop después de registrar el servidor. Esa tarea debe mostrar `apex-mcp-test` entre sus herramientas. No se puede añadir retroactivamente a una tarea que ya empezó.

Para diagnóstico de producción se registra un segundo servidor, únicamente con un perfil autorizado y para lectura:

```powershell
codex mcp add apex-mcp-production -- "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills\.venv\Scripts\python.exe" "D:\Users\ddelacruz\Desktop\Python\codex\apex.skills\scripts\run_apex_mcp_with_profile.py" --environment production
```

El wrapper lee el perfil desde el keyring del sistema y nunca inyecta credenciales en `config.toml`, comandos, documentación, repositorios ni chat. Para APEX 24.1.3, el upstream APEX 24.2 se limita a inspección/dry-run hasta aprobar compatibilidad en TEST.
