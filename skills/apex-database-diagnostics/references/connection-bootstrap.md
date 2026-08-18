# Connection bootstrap

Run these commands from the shared skills repository first:

```powershell
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\manage_apex_credentials.py import-env --environment test
.\.venv\Scripts\manage_apex_credentials.py validate --environment test
```

`import-env` reads the direct TEST connection from the ignored `.env`, discovers APEX metadata using read-only queries, and stores the resulting profile in the operating-system keyring. It does not print secrets. Wallet fields are optional and are not required for direct host/port/SID connections.

Then configure the AI client MCP entry with absolute paths. Example for TEST:

```json
{
  "mcpServers": {
    "apex-mcp-test": {
      "command": "<ABSOLUTE_PATH_TO_apex.skills/.venv/Scripts/python.exe>",
      "args": [
        "<ABSOLUTE_PATH_TO_apex.skills/scripts/run_apex_mcp_with_profile.py>",
        "--environment",
        "test"
      ]
    }
  }
}
```

For Codex Desktop, use the repository guide `docs/codex-desktop-mcp-oracle.md` instead of a project JSON file. Restart/reload the client or open a new task after registration. For production, use `--environment production` only for authorized read-only diagnostics. APEX 24.1.3 restricts the 24.2 MCP server to inspection/dry-run until compatibility is approved in TEST.
