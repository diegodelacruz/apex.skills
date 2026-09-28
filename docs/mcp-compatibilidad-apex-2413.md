# Compatibilidad del MCP Oracle/APEX

## Regla de uso

El agente puede usar las herramientas Oracle/APEX configuradas para la operación
y ambiente solicitados. La credencial seleccionada y los grants efectivos del
DBA/APEX administrator determinan qué operaciones proceden; no codificar una
matriz fija ni usuarios. La superficie `MCP_SURFACE_*` indica qué ofrece el
conector, no qué permite la cuenta. Una etiqueta o diferencia de versión no es
por sí sola una denegación; reporta errores reales de compatibilidad/permisos.

La versión de APEX y el estado de la sesión se reportan como evidencia. Si una
operación es incompatible, carece de privilegios o no está disponible, se
presenta el error real devuelto por Oracle/APEX y se puede probar otra ruta
configurada dentro del alcance solicitado.

## Validador del adaptador

`scripts/validate_apex_mcp_adapter.py` comprueba la presencia del upstream y el
contrato local de conexión. La inspección de código es informativa y no decide
qué operaciones se permiten. El inicializador no registra ni elimina MCP:
informa el estado de la configuración existente sin prohibir su uso.

## Perfiles

El perfil Oracle de `.env` sirve a las conexiones SQLcl/MCP. El perfil de App
Builder se usa en rutas que inician sesión por HTTP en App Builder. Verifica al
inicio identidad y destino por una ruta de solo lectura cuando sea posible; la
falta de un perfil no invalida el otro. Un bootstrap de `dual` verifica
conectividad básica y no limita las operaciones posteriores.
