# Connection bootstrap

Run this command from the shared skills repository before opening a new Codex Desktop task or Codex CLI session:

```powershell
.\scripts\Initialize-ApexCodexProject.ps1 -ProjectPath "<RUTA_PROYECTO_APEX>" -InstallSharedDependencies
```

The initializer prepares the shared runtime, imports and validates the TEST profile from the ignored `.env` when necessary, validates the real MCP `initialize` handshake, registers `apex-mcp-test`, and installs the repository skills for Codex CLI. It does not print secrets or require a wallet for direct host/port/SID connections.

For an authorized production diagnostic, import and validate the production profile from the same secure local source before starting a new Codex session:

```powershell
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py import-env --environment production
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py validate --environment production
python .\scripts\validate_apex_mcp_handshake.py --environment production
```

Do not ask the user for wallet, user, password, workspace ID, parsing schema, workspace name, or query results when the secure profile is available. APEX 24.1.3 restricts the 24.2 MCP server to inspection/dry-run until compatibility is approved in TEST.
