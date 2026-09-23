# Oracle MCP en Codex Desktop

> **BOOTSTRAP LOCAL CORREGIDO; VALIDACIÓN REMOTA TEST PENDIENTE**

Codex Desktop registra servidores MCP por usuario, pero el upstream
`apex-mcp` administrado en este repositorio no debe registrarse mediante
`run_apex_mcp_with_profile.py`. El wrapper inicia el upstream completo y la
inspección local de sus herramientas detecta DML interno APEX y una API de
eliminación de páginas.

El inicializador no agrega ni modifica registros MCP. Si detecta un registro
TEST anterior, lo informa como `MCP_REGISTRATION_PREEXISTING_UNVERIFIED`; si no
existe, informa `MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE`. El mismo criterio
aplica a Producción: registro previo se informa como
`MCP_REGISTRATION_PREEXISTING_UNVERIFIED`; sin registro, como
`MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE`.

Un futuro registro sólo será admisible tras construir una fachada que aplique
una allowlist técnica, no cargue las herramientas internas, bloquee SQL/DDL/DML
arbitrario y compruebe el inventario realmente expuesto. Esa evaluación es
independiente de un perfil de keyring y de una sonda Oracle.

TEST requiere autorización explícita para conexión. Producción requiere una
autorización separada y permanece sin registro ni handshake desde este
bootstrap.

## Fachada aprobada: `apex-controlled-mcp`

El repositorio incluye una fachada STDIO distinta del upstream bloqueado. Se
instala con `Setup-ApexControlledMcp.ps1`, valida Java/SQLcl mediante `doctor`
y se registra manualmente con `Register-ApexControlledMcp.ps1`. Sus operaciones
usan archivos SQL del repositorio y exports APEX nativos; no exponen las
herramientas internas del upstream.
