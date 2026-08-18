# Conectar un agente a Oracle para diagnóstico APEX

Las skills no configuran un conector automáticamente. El repositorio obtiene la conexión desde su `.env`, guarda el perfil en el keyring del sistema y descubre los datos APEX mediante consultas de sólo lectura. No solicite ni copie al chat usuario, contraseña, wallet, workspace ID, parsing schema ni workspace name.

Use el inicializador documentado en [inicialización automática de Codex](inicializacion-automatica-codex.md). Para un `.env` con conexión directa `HOST`/`PORT`/`SID`, el comando de perfil es:

```powershell
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py import-env --environment test
```

El importador toma las variables `DB_TESTING_*`, construye el DSN, consulta el workspace funcional y parsing schema visibles en APEX, y guarda el perfil seguro. Wallet es opcional y no se solicita para conexiones directas.

Una vez conectado, use este prompt:

```text
Usa la skill apex-database-diagnostics y el servidor apex-mcp-test.
Analiza este error en modo solo lectura. Identifica ambiente, aplicación,
página, componentes y objetos DATA afectados. No ejecutes cambios; entrega
causa probable, evidencia, plan de corrección, validación TEST y rollback.
```
