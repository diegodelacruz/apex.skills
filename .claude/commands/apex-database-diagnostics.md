Diagnose Oracle database performance, errors, and object health.

For a full APEX page review, use `execute_readonly_batch` with the verified
queries in `skills/apex-database-diagnostics/references/page-snapshot-queries.md`.
Keep identity and page metadata in the same read-only SQLcl session; use
`execute_readonly_query` for a single targeted SELECT.

When data exists at a source but is missing or wrong downstream, follow
`skills/apex-database-diagnostics/references/trazabilidad-end-to-end.md` with
its Oracle/APEX adapter and trace-map template; stay read-only.

Read and follow the instructions in `skills/apex-database-diagnostics/SKILL.md`.
Also read `skills/apex/SKILL.md` for the Fluency Policy.

User request: $ARGUMENTS
