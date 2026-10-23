Route this Oracle APEX request to the appropriate specialist workflow.

Read and follow the full coordinator instructions in `skills/apex/SKILL.md`.
Then read the specialist skill's SKILL.md as needed based on the request type;
`skills/apex/references/routing.md` maps request types to specialists. Data
present at a source but missing or wrong downstream goes to
`apex-database-diagnostics` and
`skills/apex-database-diagnostics/references/trazabilidad-end-to-end.md`.
For an explicitly confirmed change that follows a diagnosis, retain the
live-change context instead of restarting discovery.

User request: $ARGUMENTS
