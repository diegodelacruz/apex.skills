# Fuente única local para credenciales Oracle y APEX

- **Fecha:** 2026-10-07
- **Estado:** adoptada
- **Objetivo y necesidad:** evitar que los scripts locales de Oracle/APEX usen perfiles desactualizados, variables de proceso o parámetros directos, lo que producía credenciales distintas para un mismo ambiente.
- **Decisión:** el `.env` ignorado en la raíz de `apex.skills` es la fuente única local para credenciales y selección predeterminada del ambiente. Scripts, wrappers MCP, validadores y PowerShell deben leerlo; las variables de proceso pueden transportar credenciales ya cargadas al proceso hijo, pero no originarlas.
- **Alternativas consideradas:** sincronizar `.env` con un segundo almacén en cada inicio (mantiene dos fuentes y exige detectar divergencias); preferir variables del proceso o argumentos directos (permite fuentes implícitas distintas); dejarlo en `.env` (selección explícita y uniforme en el checkout local).
- **Impacto y riesgos:** `.env` contiene secretos en texto plano, aunque está ignorado por Git. El usuario debe restringir permisos locales y no compartirlo. El cambio elimina fuentes de credenciales alternas y overrides de conexión PowerShell. El wrapper del MCP administrado puede consultar Oracle para descubrir metadata de workspace cuando no está almacenada en el perfil.
- **Permisos y datos:** utiliza solo los perfiles de TEST/Producción configurados localmente y respeta los privilegios efectivos de Oracle/APEX. Las comprobaciones de conexión siguen siendo de solo lectura.
- **Compatibilidad:** `.env.example` documenta los campos Oracle y App Builder. Scripts Python y PowerShell leen el mismo archivo; se mantienen los nombres `test`/`testing` y `prod`/`production`.
- **Validación prevista:** revisar entradas de credenciales alternas, compilar los módulos Python modificados, comprobar sintaxis/diff y actualizar las pruebas existentes para perfiles temporales. No ejecutar conexión real ni revelar valores locales durante esta revisión.
- **Rollback:** restaurar juntos los lectores Python/PowerShell, adaptadores, documentación y requisitos desde el diff de este cambio; no requiere modificar Oracle ni recrear perfiles externos.
- **Descontinuación:** conservar `import-env` como alias de validación por compatibilidad de CLI; retirar el alias en una decisión posterior si ya no tiene consumidores.
