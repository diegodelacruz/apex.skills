# Perfiles seguros TEST y Producción

Los secretos se almacenan por usuario en el keyring seguro del sistema operativo. Nunca se guardan en Git, skills, decisiones, planes ni artefactos de release.

Para una conexión directa definida en el `.env` local, importe sin introducir secretos manualmente:

```powershell
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py import-env --environment test
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py validate --environment test
```

Producción se importa sólo para usuarios autorizados y se usa inicialmente en lectura:

```powershell
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py import-env --environment production
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py validate --environment production
```

Un usuario sin acceso a Producción desarrolla y valida en TEST; el proyecto registra estado y limitación, nunca valores del perfil.
