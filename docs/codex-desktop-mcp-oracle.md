# Oracle y APEX MCP en Codex Desktop

Codex Desktop puede usar los MCP Oracle/APEX que el usuario tenga registrados.
El inicializador prepara los recursos locales y reporta los estados de perfil;
no agrega, quita ni altera registros MCP existentes.

La solicitud define acción, alcance y ambiente. Todas las rutas MCP locales de
este repositorio leen el perfil de ese ambiente desde el `.env` de su raíz; no
se consulta una fuente de credenciales alternativa. Los permisos efectivos
concedidos por el DBA/APEX administrator deciden qué
operaciones proceden. No hardcodees usuarios ni una matriz de permisos por
ambiente, y no confundas la superficie visible del MCP con los permisos de la
cuenta conectada.

Antes de leer contenido, identifica una vez el usuario de sesión y el destino
real con una sonda mínima (`inspect_oracle_session` o metadata equivalente), a
menos que ya estén verificados en la conexión activa. Luego consulta el objeto
solicitado enseguida. No ejecutes `inspect_environment`, inventario de grants ni
diagnóstico de workspace como preflight rutinario de una lectura puntual;
resérvalos para una ambigüedad o error actual. Si la identidad/destino no
coincide, no leas ni presentes datos de esa ruta. Para APEX, comprueba el
contexto de aplicación/workspace solo si la lectura o la ruta lo requiere.
El wrapper `run_apex_mcp_with_profile.py`, los validadores y el MCP controlado
leen el mismo `.env`. Los conectores pueden coexistir, pero no mantienen copias
separadas de las credenciales. Un error de perfil debe diagnosticarse en ese
archivo local sin mostrar sus valores.

```powershell
python scripts/run_apex_mcp_with_profile.py --environment production
```

La sonda de `Initialize-ApexCodexProject.ps1` comprueba conectividad de
bootstrap; no demuestra todos los privilegios de ejecución. La inspección de
sesión y grants informa lo observable; Oracle/APEX devuelve el permiso efectivo
al ejecutar. Un estado `MISSING`, `FAIL` o `NOT_PRESENT` en un perfil no bloquea
otras rutas configuradas para el mismo ambiente. Nunca imprimas ni guardes
contraseñas en archivos versionados.
