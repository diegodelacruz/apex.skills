---
name: oracle-data-change-governance-final
category: "Oracle Data Governance"
order: 13
tags: ["database", "governance", "audit"]
description: "Govern DATA changes with decisions, rollback, validation, and audit evidence."
---

# Final DATA Change Governance

## Required records and decision precedence

Follow the global read and mutation rules in `skills/apex/SKILL.md`. A review or request to show object data/specifications is an immediate read, not a change workflow. Before a mutation, ask once for confirmation of the environment, target, exact operation, and backup choice. Do not execute until the user explicitly confirms the action and answers yes or no about backup. If either decision is missing or ambiguous, ask only for that decision and wait; silence never means no backup. No backup or snapshot is created unless the user answers yes. The complete response is the single confirmation; do not add another approval. Do not inspect grants before, during, or after a requested operation; execute it and report the actual service response, including privilege errors. Inspect grants only when explicitly requested or diagnosing an observed access error. Do not count affected rows before INSERT, UPDATE, DELETE, MERGE, or another transaction unless the user asks or a concrete ambiguity makes it necessary. Record the actual operation and result without requiring a project plan for a single DML request.

## Object and script rules

- Official objects live in `data` unless the user explicitly names another owner; backups are created in the current user's schema. Qualify DATA object names in generated DDL and never fall back to the connected user's schema after an authorization error.
- SQL filenames and non-literal identifiers are lower-case. Use physical four-column tabs, not spaces. Preserve the required casing of string literals, comments, prompts, and quoted identifiers. Document persistent objects with purpose, owner, dependencies, and applicable validation; do not create project documentation for an ephemeral one-off DML statement.
- Never use `alter` to correct a table or view. Reconstruct a table only after explicit user request. For a compatible view replacement, prefer `create or replace view` after capturing prior DDL and inspecting dependents; use drop/create only when replacement is not viable and document the availability impact.
- A backup exists only when the user explicitly requested or accepted it. If created,
  identify it and retain it until the user requests its removal; never create a backup
  merely because this skill mentions rollback.
- On non-migration table recreation, reset identifier sequencing. On a user-declared migration, preserve sequential continuity and disable/re-enable the documented triggers.
- Default PK generation is the trigger call `data.pk_commons.sp_secuencia('data.<table_name>', :new.id)`. Use it without asking unless the user explicitly requests a database sequence.
- Default table order is `id`, `usercrea varchar2(25)`, `fechcrea timestamp`, `usermodi varchar2(25)`, `fechmodi timestamp`, `compania varchar2(5)`, then business columns.
- Populate audit fields with `nvl(v('user'), 'ORCL')`. Include `compania` for a new DATA business table by default. If the user supplies exact SQL that omits it, preserve the supplied definition and report the convention difference; do not stop to ask.
- Do not create any key, constraint, or index unless the user explicitly requests it and it is recorded.
- Infer missing technical details from the target schema, comparable objects, and these defaults. Ask one concise question only when a missing business rule or target cannot be inferred and would make execution incorrect.

## UTF-8 Character Encoding

Preserve Unicode text exactly. The detailed checks below apply when a retained
SQL artifact or stored object contains non-ASCII text; do not run database
source-text readbacks or create an implementation plan for an ASCII-only
one-off DML transaction.

**CRITICAL: Unicode text must be preserved exactly through every step.**

Texts like "agrupación", "Parámetros", "conciliación" contain accented characters (á, ó, ó) that MUST remain intact. Corrupted versions like "agrupaciÃ³n", "ParÃ¡metros", "conciliaciÃ³n" indicate byte sequences were misinterpreted as Windows-1252 or ISO-8859-1.

### Before writing SQL/PL/SQL that contains non-ASCII text:

1. **Verify the source file encoding**
   - Your text editor/IDE must save as UTF-8 (no BOM)
   - Confirm: file contains bytes `c3 a1` for á, `c3 a9` for é, `c3 b1` for ñ, etc.
   - If your tool shows "ANSI", "Windows-1252", or "ISO-8859-1": stop and convert first

2. **Verify the MCP/transport encoding**
   - The agent's MCP server must handle UTF-8 natively
   - Claude Code, Codex CLI, and `apex-mcp` all support UTF-8
   - If using a different transport, verify UTF-8 capability before proceeding

3. **Never depend on system defaults**
   - PowerShell: explicitly use `-Encoding UTF8` on Get-Content, Set-Content
   - Python: explicitly specify `encoding='utf-8'` on open(), read_text(), write_text()
   - Bash: ensure `LANG` and `LC_ALL` are set to a UTF-8 locale (e.g., `en_US.UTF-8`)
   - SQL*Plus/SQL Developer: set `NLS_LANG=.UTF8` in environment

### During SQL/PL/SQL generation:

4. **Preserve literal text exactly**
   - Comments with accents: `-- Agrupación de datos` (not `-- Agrupacion de datos`)
   - String literals: `'Parámetros de entrada'` (not `'Parametros de entrada'`)
   - Messages and prompts: `v_msg := 'Conciliación completada';` (preserve accents)
   - Do NOT convert "á" → "a", "ñ" → "n", "ü" → "u"

5. **Verify text integrity before submitting**
   - Before running the validator, inspect the file contents
   - Search for mojibake sequences: `Ã`, `Â`, `â`, `ð`, `Ã©`, `Ã¡`, `Ã±`, `Ã¼`
   - If found: STOP, report encoding error, do NOT proceed
   - If clean: continue to validation

### During validation:

6. **Run the style validator with UTF-8**
   ```
   python <skill-root>/scripts/validate_sql_style.py <file>
   ```
   - Output must display accented characters correctly
   - If validator output shows mojibake: encoding problem detected
   - Do NOT accept STYLE_PASS if text is corrupted

### After deploying a stored program/view that contains non-ASCII text:

7. **Verify stored text in database**
   - Query `ALL_SOURCE` or object definitions:
     ```sql
     select text from all_source where owner='DATA' and name='<OBJECT>';
     ```
   - Check that á, é, í, ó, ú, ñ, ü appear intact
   - If stored as corrupted bytes (Ã©, Ã¡, etc.): stop further deployment, preserve the observed evidence, and report the affected object. Do not promise or attempt an automatic rollback unless a recovery mechanism for this exact change is available and verified. If recovery needs a new mutation, obtain the required confirmation before executing it.
   - Oracle should store UTF-8 natively if NLS_CHARACTERSET=AL32UTF8

8. **Document encoding for formal delivery when relevant**
   - Local file: "UTF-8 (no BOM), verified in [editor name]"
   - MCP transport: "UTF-8 via Claude Code MCP"
   - Oracle: "Stored as AL32UTF8, verified in ALL_SOURCE"
   - Include this in implementation-plan.md

### If UTF-8 cannot be guaranteed:

9. **STOP and report the problem**
   - Do NOT replace accented characters with ASCII equivalents
   - Do NOT use HTML entities (`&aacute;`, `&ntilde;`) in SQL text
   - Do NOT ignore mojibake and proceed anyway
   - Raise the issue with the user: "UTF-8 integrity cannot be verified at [stage]. Aborting deployment."

## Completion gate

Run `validate_sql_style.py` on retained/generated SQL deliveries when the SQL
is nontrivial or the user asks for a script. A single live DML request does not
require a versioned project folder, `change.json`, snapshot, preflight, rollback
file, or manual implementation plan. Use a direct SQL execution route after
the user's one confirmation and retain the normal audit event. Use a bundle and
formal records for multi-object changes, migrations, or existing-object
corrections where a fingerprint preflight materially protects the operation.
Include a snapshot only when the user requested a backup. Report the result;
discuss rollback only on request or when a concrete limitation requires it.
