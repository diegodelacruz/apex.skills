# Decisiones canónicas finales

| ID | Decisión | Estado |
| --- | --- | --- |
| DC-001 | El target histórico fue Oracle APEX 24.1.3; `apex-mcp` 24.2 se restringía a inspección y dry-run hasta prueba aprobada. | sustituida por DC-007 |
| DC-002 | Los triggers de auditoría usan `nvl(v('user'), 'ORCL')` para `usercrea` y `usermodi`. | vigente |
| DC-003 | Solo se crean backups de objetos DATA cuando el usuario los solicita o acepta; los backups creados se conservan hasta que el usuario pida depurarlos. | vigente |
| DC-004 | Todo proyecto nuevo clona `apex-mcp`, `zaimella-skill` y `zaimella-apex-oracle` con el inicializador canónico. | vigente |
| DC-005 | Las decisiones explícitas documentadas del proyecto prevalecen sobre los defaults de skills para ese proyecto. | vigente |
| DC-006 | El nivel de evidencia y documentación es proporcional al cambio: una operación puntual conserva el evento de auditoría normal; planes y paquetes formales se reservan para cambios coordinados, migraciones o trabajo materialmente complejo. | vigente |
| DC-007 | La solicitud directa define acción, ambiente y alcance. Se usa la credencial configurada para ese ambiente; Oracle/APEX determina los permisos efectivos al ejecutar. No inspeccionar grants como validación previa, intermedia o final; informar el error real. Consultar grants solo a petición explícita o para diagnosticar un error de acceso observado. No hardcodear usuarios ni matrices de permisos. Para una lectura puntual, verificar identidad/destino una vez si hace falta y consultar inmediatamente; no agregar inventarios o validaciones rutinarias. | vigente |
| DC-008 | Revisar, consultar o mostrar datos/especificaciones es implícitamente read-only e inmediato. Antes de mutar se solicita una sola confirmación con ambiente, objeto, operación, confirmación de ejecución y decisión explícita sí/no de backup. No ejecutar hasta tener ambas respuestas; el silencio no equivale a rechazar el backup. Crear backup solo tras respuesta afirmativa; no exigir conteos previos. | vigente |
| DC-009 | Todas las rutas mutativas controladas por el repositorio requieren la confirmación de acción y respuesta sí/no de backup. Si backup=yes, se exige un artefacto explícito y se ejecuta o valida antes del cambio; la mutación se bloquea si falta o falla. Los argumentos del adaptador reflejan la respuesta del agente/cliente, no autentican criptográficamente al usuario. | vigente |

Registro ampliado, alternativas, impacto, permisos, compatibilidad y reversión: [decisión 2026-09-28](decisiones/20260928-autoridad-credenciales-oracle-apex.md), [decisión 2026-10-12 sobre lecturas y confirmaciones](decisiones/20261012-lecturas-inmediatas-mutaciones-confirmadas.md) y [decisión 2026-10-12 sobre gates y backups del adaptador](decisiones/20261012-gates-mutacion-backup-adaptadores.md).
