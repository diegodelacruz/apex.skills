# Conectar un agente a Oracle para diagnóstico APEX

Decir “usa las skills y conéctate a la base” no configura un conector automáticamente. Deben cumplirse cuatro condiciones:

1. El repositorio de skills tiene upstreams inicializados y dependencias instaladas en `.venv`.
2. El usuario guarda su perfil TEST/Producción en el keyring seguro.
3. El perfil valida una conexión de solo lectura.
4. El cliente de IA tiene configurado `apex-mcp` mediante el wrapper de perfil seguro.

Los comandos y ejemplo MCP están en `skills/apex-database-diagnostics/references/connection-bootstrap.md`.

Una vez conectado, use este prompt:

```text
Usa la skill apex-database-diagnostics y el servidor apex-mcp-test.
Analiza este error en modo solo lectura. Identifica ambiente, aplicación,
página, componentes y objetos DATA afectados. No ejecutes cambios; entrega
causa probable, evidencia, plan de corrección, validación TEST y rollback.
```
