# Decisiones canónicas finales

| ID | Decisión | Estado |
| --- | --- | --- |
| DC-001 | El target histórico fue Oracle APEX 24.1.3; `apex-mcp` 24.2 se restringía a inspección y dry-run hasta prueba aprobada. | sustituida por DC-007 |
| DC-002 | Los triggers de auditoría usan `nvl(v('user'), 'ORCL')` para `usercrea` y `usermodi`. | vigente |
| DC-003 | Los backups de objetos DATA se conservan hasta decisión explícita del usuario de depurarlos. | vigente |
| DC-004 | Todo proyecto nuevo clona `apex-mcp`, `zaimella-skill` y `zaimella-apex-oracle` con el inicializador canónico. | vigente |
| DC-005 | Las decisiones explícitas documentadas del proyecto prevalecen sobre los defaults de skills para ese proyecto. | vigente |
| DC-006 | Cada cambio mantiene decisiones, plan de implementación, evidencia, rollback y estado visibles bajo `control-proyecto/`. | vigente |
| DC-007 | La solicitud directa define acción, ambiente y alcance. Se usa la credencial configurada para ese ambiente; los privilegios efectivos concedidos por el DBA/APEX administrator determinan las operaciones Oracle/APEX posibles. No hardcodear usuario ni matriz fija de permisos; validar al inicio identidad/destino mediante rutas de solo lectura cuando estén disponibles, sin agregar aprobaciones ni delegar consultas al usuario. | vigente |

Registro ampliado, alternativas, impacto, permisos, compatibilidad y reversión: [decisión 2026-09-28](decisiones/20260928-autoridad-credenciales-oracle-apex.md).
