# Compatibilidad del MCP con APEX 24.1.3

> **BOOTSTRAP LOCAL CORREGIDO; VALIDACIÓN REMOTA TEST PENDIENTE**

## Estado del upstream completo

La inspección local de `.upstreams/managed/apex-mcp/apex_mcp/tools/` detecta
operaciones `UPDATE` y `DELETE` contra `APEX_240100` y la llamada
`wwv_flow_page_dev.delete_page`. El wrapper
`scripts/run_apex_mcp_with_profile.py` inicia ese upstream completo. Por ello,
el bootstrap no registra automáticamente `apex-mcp-test`, ni siquiera cuando
se solicita `-ValidateOracleTest`.

El estado local para una inscripción ausente es
`MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE`. Una inscripción previa no se elimina
ni modifica: se informa como `MCP_REGISTRATION_PREEXISTING_UNVERIFIED`.
Producción no se registra desde el bootstrap y reporta
`MCP_REGISTRATION_NOT_SUPPORTED_IN_THIS_BOOTSTRAP`.

## Contrato de conexión y límites

`scripts/validate_apex_mcp_adapter.py` lee el código administrado sin importarlo
ni ejecutarlo. Comprueba la construcción `connect_kwargs`,
`oracledb.connect(**connect_kwargs)` y wallet condicional. El resultado
`MCP_ADAPTER_READY` sólo confirma el contrato de conexión directa por lectura
local. La superficie se informa independientemente y la ausencia de una
allowlist aplicable no equivale a seguridad.

No se ejecuta `Apply-ApexMcpDirectConnectionPatch.py` desde el bootstrap. Toda
preparación que escriba el upstream debe ser una operación explícita,
versionada y revisada fuera del bootstrap.

## Operación pendiente

APEX CRUD sigue bloqueado hasta disponer de una fachada que aplique una
allowlist técnica, no cargue herramientas internas, no permita SQL/DDL/DML
arbitrario y pruebe el inventario efectivamente expuesto. La validación remota
TEST requiere autorización explícita. Producción requiere autorización separada
y permanece sin registro ni handshake.
