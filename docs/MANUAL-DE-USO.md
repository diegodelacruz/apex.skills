# Manual de uso — APEX Skills

## Inicio seguro

Use la [guía canónica de inicialización](inicializacion-automatica-codex.md). Los perfiles Oracle y APEX son independientes y no se deben compartir en chat ni repositorio. El bootstrap consulta el perfil Oracle de TEST y Producción y, sólo si está listo, realiza la sonda mínima de lectura contra `dual`. Las advertencias no bloquean la preparación local.

El upstream MCP completo permanece sin registro por superficie insegura. APEX App Builder no está autenticado sin runner real; APEX CRUD y Oracle DDL están bloqueados. Producción no realiza más que la sonda Oracle de lectura.

## Operación

Describa el objetivo y el ambiente. Para cambios, solicite explícitamente el alcance y siga los controles de gobierno aplicables. Las capacidades bloqueadas no se sustituyen mediante registro manual de un MCP ni parches internos.

## Índice de documentación

### Guías operativas

- [Iniciar un proyecto APEX](iniciar-proyecto-apex.md) — flujo para crear aplicación o agregar páginas
- [Credenciales y alineación de ambientes](credenciales-y-alineacion-ambientes.md) — perfiles TEST/Producción
- [Perfiles de credenciales seguros](perfiles-credenciales-seguros.md) — almacenamiento en keyring del SO
- [Entornos Python para proyectos](entornos-python-proyectos.md) — regla de entorno único compartido
- [GitHub Setup & Release](GITHUB-SETUP.md) — configuración de repositorio y versionado semántico
- [Reglas de formateo canónicas](reglas-formateo-canonicas.md) — estilo de código para todos los lenguajes

### Referencias técnicas

- [APEX UX Craft](APEX-UX-CRAFT.md) — referencia de diseño, usabilidad y accesibilidad
- [Oracle/APEX Examples](ORACLE-APEX-EXAMPLES.md) — ejemplos concretos de políticas de documentación
- [Base de conocimiento de exports](base-conocimiento-exports-apex.md) — patrones extraídos de exports ZIP
- [Referencia MCP Claude](referencia-mcp-claude.md) — hallazgos históricos de revisión del upstream MCP
- [Estado canónico actual](estado-canonico-actual.md) — punto de entrada y estado del ecosistema

### Scripts utilitarios

- [`Apply-ApexMcpOpenAppPatch.py`](../scripts/Apply-ApexMcpOpenAppPatch.py) — parche canónico para agregar `apex_open_app` al upstream MCP

### Documentos históricos (retirados)

- [Plan page-automation](PLAN-APEX-PAGE-AUTOMATION.md) — diseño histórico retirado, no operativo
- [Solicitud permisos DBA](SOLICITUD-PERMISOS-DBA-APEX-2413.md) — solicitud histórica retirada, no ejecutar
