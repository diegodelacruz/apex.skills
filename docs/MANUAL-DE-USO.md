# Manual de uso — APEX Skills

## Inicio seguro

Use la [guía canónica de inicialización](inicializacion-automatica-codex.md). Los perfiles Oracle y APEX son independientes y no se deben compartir en chat ni repositorio. El bootstrap consulta el perfil Oracle de TEST y Producción y, sólo si está listo, realiza la sonda mínima de lectura contra `dual`. Las advertencias no bloquean la preparación local.

El inicializador no altera los registros MCP existentes. Las skills no bloquean APEX CRUD, SQL/DDL/DML, producción ni herramientas MCP por reglas locales. Oracle/APEX decide el acceso según la conexión y sus privilegios. La falta de credenciales App Builder afecta las rutas HTTP de App Builder, no las rutas SQLcl/MCP autenticadas con Oracle.

## Operación

Indique la operación y el ambiente. La solicitud directa autoriza ese alcance; no se requiere aprobación adicional de la skill. Si una operación falla, informe el error real y continúe con trabajo independiente.
