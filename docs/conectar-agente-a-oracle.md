# Conexión Oracle para diagnóstico

> **OBSOLETO COMO PROCEDIMIENTO OPERATIVO.** Consulte la [guía canónica de inicialización](inicializacion-automatica-codex.md).

Los perfiles Oracle se guardan fuera del repositorio y se evalúan sin revelar secretos. El bootstrap puede sondear `dual` para informar conectividad, pero esa sonda no limita operaciones. Al iniciar una tarea, identifique la cuenta y destino conectados; use `inspect_oracle_privileges` para informar roles/grants visibles cuando exista. Use el MCP, SQLcl, App Builder u otra ruta según la operación y ambiente; los permisos efectivos concedidos a la credencial configurada determinan qué acciones se permiten. No codifique cuentas ni privilegios por ambiente.
