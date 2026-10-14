# Conexión Oracle para diagnóstico

> **OBSOLETO COMO PROCEDIMIENTO OPERATIVO.** Consulte la [guía canónica de inicialización](inicializacion-automatica-codex.md).

Los perfiles Oracle se guardan fuera del repositorio y se evalúan sin revelar secretos. El bootstrap puede sondear `dual` para informar conectividad, pero esa sonda no limita operaciones. Para ejecutar una solicitud, use el MCP, SQLcl, App Builder u otra ruta según la operación y ambiente; no inspeccione grants como validación previa, intermedia o final. Oracle determina los permisos efectivos de la credencial y el agente informa el resultado real, incluidos errores de privilegios. Use `inspect_oracle_privileges` solo si el usuario solicita ver los grants o pide diagnosticar un error de acceso observado. No codifique cuentas ni privilegios por ambiente.
