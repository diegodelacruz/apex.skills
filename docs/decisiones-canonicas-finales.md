# Decisiones canónicas finales

| ID | Decisión | Estado |
| --- | --- | --- |
| DC-001 | El target es Oracle APEX 24.1.3; `apex-mcp` 24.2 solo puede usarse para inspección y dry-run hasta prueba explícita y aprobada de compatibilidad en TEST. | vigente |
| DC-002 | Los triggers de auditoría usan `nvl(v('user'), 'ORCL')` para `usercrea` y `usermodi`. | vigente |
| DC-003 | Los backups de objetos DATA se conservan hasta decisión explícita del usuario de depurarlos. | vigente |
| DC-004 | Todo proyecto nuevo clona `apex-mcp`, `zaimella-skill` y `zaimella-apex-oracle` con el inicializador canónico. | vigente |
| DC-005 | Las decisiones explícitas documentadas del proyecto prevalecen sobre los defaults de skills para ese proyecto, luego de que el agente presente los defaults aplicables. | vigente |
| DC-006 | Cada cambio mantiene decisiones, plan de implementación, evidencia, rollback y estado visibles bajo `control-proyecto/`. | vigente |
