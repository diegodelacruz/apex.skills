# Perfiles seguros TEST y Producción

Los secretos se almacenan por usuario en el keyring seguro del sistema operativo. Nunca se guardan en Git, skills, decisiones, planes ni artefactos de release.

## Preparación explícita de TEST

1. En la raíz del repositorio, copie .env.example como .env.
2. Complete DB_TESTING_USER, DB_TESTING_PASSWORD, DB_TESTING_HOST, DB_TESTING_PORT y DB_TESTING_SID con datos de TEST.
3. Importe el perfil: ./.venv/Scripts/python.exe ./scripts/manage_apex_credentials.py import-env --environment test.
4. Valídelo: ./.venv/Scripts/python.exe ./scripts/manage_apex_credentials.py validate --environment test.

El importador descubre workspace y schema mediante consultas de solo lectura y guarda el resultado en el keyring. Si falla, revise red/VPN, host, puerto, SID, usuario y contraseña; la salida solo muestra el tipo de error, nunca el secreto.



Para una conexión directa definida en el `.env` local, importe sin introducir secretos manualmente:

```powershell
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py import-env --environment test
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py validate --environment test
```

Se importa el perfil del ambiente que el usuario necesita utilizar. La validación del perfil es informativa y no impone modo de solo lectura:

```powershell
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py import-env --environment production
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py validate --environment production
```

Si una operación no puede conectarse o el servicio deniega privilegios, informe el error real sin sustituir silenciosamente el ambiente. Nunca registre valores del perfil.
