# Informe de capacidades controladas — 2026-09-17

## Veredicto

**BOOTSTRAP LOCAL CORREGIDO; VALIDACIÓN REMOTA TEST PENDIENTE**

## Estado comprobado localmente

El inicializador no registra `apex-mcp-test`, tampoco como efecto de
`-ValidateOracleTest`. La inspección de fuentes confirma que su wrapper ejecuta
el upstream completo y que éste contiene DML interno sobre `APEX_240100` y
`wwv_flow_page_dev.delete_page`; por ello TEST reporta
`MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE`. Si existiera una inscripción previa,
el bootstrap sólo la informa como `MCP_REGISTRATION_PREEXISTING_UNVERIFIED` y
no la altera. Producción reporta
`MCP_REGISTRATION_NOT_SUPPORTED_IN_THIS_BOOTSTRAP`.

El validador del adaptador sólo lee fuentes: comprueba `connect_kwargs`,
`oracledb.connect(**connect_kwargs)` y wallet condicional. Un
`MCP_ADAPTER_READY` prueba exclusivamente ese contrato local; no prueba una
conexión Oracle ni declara segura la superficie MCP. La superficie actual se
reporta por separado como `MCP_SURFACE_UNSAFE`.

El `probe` Oracle conserva una única consulta contra `dual` con `sys_context`.
Clasifica perfil ausente, incompleto o inválido; autenticación; conexión; y
fallo de sonda sin mostrar secretos, DSN ni mensajes del driver. No acredita
privilegios DDL, cuota, objetos ni capacidades APEX.

## Capacidades bloqueadas

- APEX CRUD continúa bloqueado hasta contar con un runner App Builder auténtico
  y autenticado.
- Oracle DDL continúa bloqueado hasta implementar preflights reales de
  privilegios efectivos, cuota, dependencias, respaldo y recuperación.
- TEST requiere autorización explícita para conexión. Producción requiere una
  autorización separada, y no se registra desde este bootstrap.

`Apply-ApexMcpDirectConnectionPatch.py`, si se requiere, es una preparación
explícita y versionada del upstream fuera del bootstrap; no es un mecanismo
automático ni una demostración de seguridad.

## Validación local

Las pruebas y auditorías locales se ejecutan y registran en el control vigente
[capacidades-controladas-20260917.md](capacidades-controladas-20260917.md).
No se ejecutó el inicializador, `probe`, handshakes MCP ni conexión a
TEST/Producción en este ciclo.
