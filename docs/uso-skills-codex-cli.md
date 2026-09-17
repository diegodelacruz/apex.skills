# Uso de APEX Skills desde Codex CLI

Antes de modificar el repositorio, cumpla la [política de evolución](POLITICA-EVOLUCION-ECOSISTEMA.md). Para preparar el entorno consulte la [guía canónica](inicializacion-automatica-codex.md).

El inicializador instala o verifica únicamente recursos locales y muestra el estado de perfiles; no registra MCP, hace handshake ni repara el upstream. `-SkipRemoteProbe` evita toda conexión Oracle. Sin él, cada perfil Oracle listo puede recibir sólo la sonda contra `dual`; Producción queda limitada a ella.

No use comandos de registro manual para el wrapper `run_apex_mcp_with_profile.py`. El upstream completo está deliberadamente bloqueado por superficie insegura.
