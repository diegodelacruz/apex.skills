# Connection bootstrap

> **Deprecated operational instructions.** Follow `docs/inicializacion-automatica-codex.md`.

The bootstrap keeps the full upstream unregistered, starts no MCP handshake, and does not import credentials. It reads the separate Oracle/APEX profile states; an Oracle profile that is ready may receive only the read-only `dual` probe. Production is limited to that probe. Missing or invalid profiles are warnings, not bootstrap failures.
