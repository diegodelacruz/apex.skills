# Conexión Oracle para diagnóstico

> **OBSOLETO COMO PROCEDIMIENTO OPERATIVO.** Consulte la [guía canónica de inicialización](inicializacion-automatica-codex.md).

Los perfiles Oracle se guardan fuera del repositorio y se evalúan sin revelar secretos. El bootstrap sólo ejecuta una sonda contra `dual` cuando el perfil está listo. No configure ni registre el upstream MCP completo para obtener acceso; Producción se limita a una sonda Oracle de sólo lectura.
