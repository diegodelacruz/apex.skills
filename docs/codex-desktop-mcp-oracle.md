# Oracle y APEX MCP en Codex Desktop

Codex Desktop puede usar los MCP Oracle/APEX que el usuario tenga registrados.
El inicializador prepara los recursos locales y reporta los estados de perfil;
no agrega, quita ni altera registros MCP existentes.

La solicitud define acción, alcance y ambiente. Usa el perfil configurado para
ese ambiente en `.env` o en el almacén de credenciales asociado al MCP. Los
permisos efectivos concedidos por el DBA/APEX administrator deciden qué
operaciones proceden. No hardcodees usuarios ni una matriz de permisos por
ambiente, y no confundas la superficie visible del MCP con los permisos de la
cuenta conectada.

Al comenzar, identifica el usuario de sesión y el destino real con las
herramientas de solo lectura disponibles (`inspect_oracle_session`,
`inspect_environment`, `inspect_oracle_privileges` o metadata equivalente).
Para APEX, comprueba el contexto de aplicación/workspace si la ruta lo permite.
El wrapper `run_apex_mcp_with_profile.py` obtiene el perfil APEX/Oracle que le
corresponde desde el keyring; el MCP controlado usa los perfiles Oracle del
`.env`. Los conectores pueden coexistir. Una falta de perfil para un conector no
demuestra que otro canal del mismo ambiente carezca de acceso.

```powershell
python scripts/run_apex_mcp_with_profile.py --environment production
```

La sonda de `Initialize-ApexCodexProject.ps1` comprueba conectividad de
bootstrap; no demuestra todos los privilegios de ejecución. La inspección de
sesión y grants informa lo observable; Oracle/APEX devuelve el permiso efectivo
al ejecutar. Un estado `MISSING`, `FAIL` o `NOT_PRESENT` en un perfil no bloquea
otras rutas configuradas para el mismo ambiente. Nunca imprimas ni guardes
contraseñas en archivos versionados.
