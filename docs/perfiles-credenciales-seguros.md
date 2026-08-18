# Perfiles seguros TEST y Producción

Los secretos se almacenan por usuario en el keyring seguro del sistema operativo. Nunca se guardan en Git, `.env`, skills, decisiones, planes ni artefactos de release.

Instale el conjunto completo:

```powershell
python -m pip install -r requirements-complete.txt
```

Registre cada perfil de manera interactiva; el comando no imprime contraseñas:

```powershell
python .\scripts\manage_apex_credentials.py set --environment test
python .\scripts\manage_apex_credentials.py set --environment production
```

Compruebe disponibilidad o conexión de solo lectura:

```powershell
python .\scripts\manage_apex_credentials.py status --environment test
python .\scripts\manage_apex_credentials.py validate --environment test
```

Un usuario sin perfil o sin acceso a Producción puede desarrollar y validar en TEST. El proyecto registra solamente el estado del perfil, nunca sus valores.
