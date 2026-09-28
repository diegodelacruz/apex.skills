# Inicialización Codex — guía canónica

> **BOOTSTRAP LOCAL CORREGIDO; VALIDACIÓN REMOTA TEST PENDIENTE**

El inicializador prepara snapshots/upstreams, Python y skills en la misma ejecución y presenta una matriz de TEST y Producción. Un remoto inaccesible usa la copia incluida o conserva la copia previa. No importa credenciales, no realiza handshake y no registra ni elimina MCP.

```powershell
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>"
```

Para una comprobación enteramente local use `-SkipRemoteProbe`. Sin esa opción, el bootstrap consulta el estado de cada perfil Oracle y ejecuta solamente `probe` cuando el perfil está listo. La sonda abre la sesión configurada y lee `session_user` y `current_schema` desde `dual`; no prueba privilegios, cuota, acceso APEX ni DDL.

Los perfiles Oracle y APEX se almacenan por separado. Un perfil faltante, incompleto, inválido o una sonda fallida produce un estado informativo y no detiene el bootstrap. La sonda de `dual` solo describe la comprobación inicial: no restringe operaciones posteriores por MCP, SQLcl u otra ruta configurada.

El inicializador no cambia registros MCP existentes. Skills y agentes usan las herramientas disponibles sin imponer restricciones locales por operación, versión o ambiente. La falta del perfil App Builder solo afecta las rutas que requieren iniciar sesión en App Builder; el acceso por Oracle/SQLcl depende del perfil Oracle y de sus privilegios reales.
