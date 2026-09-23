# Inicialización Codex — guía canónica

> **BOOTSTRAP LOCAL CORREGIDO; VALIDACIÓN REMOTA TEST PENDIENTE**

El inicializador prepara snapshots/upstreams, Python y skills en la misma ejecución y presenta una matriz de TEST y Producción. Un remoto inaccesible usa la copia incluida o conserva la copia previa. No importa credenciales, no realiza handshake y no registra ni elimina MCP.

```powershell
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>"
```

Para una comprobación enteramente local use `-SkipRemoteProbe`. Sin esa opción, el bootstrap consulta el estado de cada perfil Oracle y ejecuta solamente `probe` cuando el perfil está listo. La sonda abre la sesión configurada y lee `session_user` y `current_schema` desde `dual`; no prueba privilegios, cuota, acceso APEX ni DDL.

Los perfiles Oracle y APEX se almacenan por separado. Un perfil faltante, incompleto, inválido o una sonda fallida produce una advertencia y no detiene el bootstrap. Producción se limita a esa sonda Oracle de sólo lectura.

El upstream `apex-mcp` completo no se registra: su superficie incluye operaciones APEX internas inseguras. APEX CRUD requiere un runner App Builder auténtico; DDL requiere preflights reales. Ambos continúan bloqueados.
