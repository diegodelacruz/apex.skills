# Manual de uso — APEX Skills

## Inicio seguro

Use la [guía canónica de inicialización](inicializacion-automatica-codex.md). Los perfiles Oracle y APEX son independientes y no se deben compartir en chat ni repositorio. El bootstrap consulta el perfil Oracle de TEST y Producción y, sólo si está listo, realiza la sonda mínima de lectura contra `dual`. Las advertencias no bloquean la preparación local.

El upstream MCP completo permanece sin registro por superficie insegura. APEX App Builder no está autenticado sin runner real; APEX CRUD y Oracle DDL están bloqueados. Producción no realiza más que la sonda Oracle de lectura.

## Operación

Describa el objetivo y el ambiente. Para cambios, solicite explícitamente el alcance y siga los controles de gobierno aplicables. Las capacidades bloqueadas no se sustituyen mediante registro manual de un MCP ni parches internos.
