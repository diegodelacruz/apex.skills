# Credenciales locales desde `.env`

El `.env` de la raíz de `apex.skills` es la única fuente de credenciales para
Oracle, SQLcl, el MCP controlado, los wrappers del MCP administrado y App
Builder. Los lectores operativos solo consultan este archivo.

`.env` está excluido de Git, pero es un archivo local de texto y no está cifrado
por la aplicación. Mantén el archivo en el checkout local, restringe el acceso
al usuario que ejecuta Codex y nunca pegues sus valores en chat, logs, skills,
decisiones, planes o archivos versionados.

## Variables

- Oracle TEST: `DB_TESTING_USER`, `DB_TESTING_PASSWORD`, `DB_TESTING_HOST`,
  `DB_TESTING_PORT`, `DB_TESTING_SID`.
- Oracle Production: `DB_PRODUCTION_USER`, `DB_PRODUCTION_PASSWORD`,
  `DB_PRODUCTION_HOST`, `DB_PRODUCTION_PORT`, `DB_PRODUCTION_SID`.
- App Builder usa las variables `APEX_TESTING_*` y `APEX_PRODUCTION_*` del
  archivo `.env.example`.
- `DB_ENV` selecciona el ambiente predeterminado. Un argumento explícito
  `--environment` lo reemplaza para esa ejecución.

## Preparación y validación

1. Copia `.env.example` como `.env` en la raíz del repositorio y reemplaza los
   valores de ejemplo localmente.
2. Comprueba que el perfil contiene los campos necesarios, sin conectarse:

   ```powershell
   .\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py status --environment test
   ```

3. Prueba la autenticación y lee únicamente la identidad de sesión desde
   `dual`:

   ```powershell
   .\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py probe --environment test
   ```

4. Repite con `production` solo cuando necesites comprobar ese ambiente.

`validate` conserva una consulta de solo lectura para revisar el perfil. El
comando histórico `import-env` se mantiene como alias de comprobación del
archivo; ya no copia credenciales a otro almacén. `set` y `set-apex` escriben
los valores introducidos en el `.env` local.

## Rutas MCP

- `apex-controlled` lee directamente Oracle desde este `.env`.
- `run_apex_mcp_with_profile.py` obtiene de este mismo archivo las credenciales
  Oracle y prepara el contexto APEX necesario antes de lanzar el wrapper.
- Los validadores de conexión y App Builder consultan este mismo archivo.

Si una conexión falla, el comando informa el código Oracle sin mostrar la
contraseña ni el mensaje completo del driver. Actualiza las variables del
ambiente correspondiente en `.env`.
