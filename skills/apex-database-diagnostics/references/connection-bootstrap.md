# Connection bootstrap

Run these commands from the shared skills repository first:

```powershell
.\scripts\Initialize-ApexSkillUpstreams-V2.ps1
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py set --environment test
.\.venv\Scripts\python.exe .\scripts\manage_apex_credentials.py validate --environment test
```

The profile command prompts locally for the connection details and stores them in the operating-system keyring. Never place those values in the MCP JSON, `.env`, source code, commits, or chat.

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

Use the client-native location: `.mcp.json` for Claude Code, `.cursor/mcp.json` for Cursor, or `.gemini/settings.json` for Gemini CLI. Restart/reload the client, confirm the MCP server is connected, and only then ask for database analysis.

For production, use `--environment production` only for authorized read-only diagnostics. APEX 24.1.3 restricts the 24.2 MCP server to inspection/dry-run until compatibility is approved in TEST.
