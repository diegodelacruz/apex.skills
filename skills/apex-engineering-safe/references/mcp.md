# Portable MCP activation

Install the local `apex-mcp` source in a dedicated environment. Configure `python -m apex_mcp` with an absolute working directory and secrets from an environment/secret store, never Git. Use `.mcp.json` for Claude Code, `.cursor/mcp.json` for Cursor, `.gemini/settings.json` for Gemini CLI, or an equivalent MCP configuration. Verify status/list/describe first and enable dry-run before a permitted change. Keep HTTP localhost until TLS and authentication are separately managed.
