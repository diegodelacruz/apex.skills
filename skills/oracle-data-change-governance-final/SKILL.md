---
name: oracle-data-change-governance-final
category: "Oracle Data Governance"
order: 13
tags: ['database', 'governance', 'audit']
---

# Final DATA Change Governance

## Required records and decision precedence

Create `control-proyecto/cambios/<id>/decisions.md` and `implementation-plan.md` before executable SQL. First present applicable canonical skill decisions to the user. An explicit decision recorded for the current project then takes precedence for that project; do not silently override it.

## Object and script rules

- Official objects live in `data`; backups are created in the current user's schema.
- SQL filenames and non-literal identifiers are lower-case. Use physical four-column tabs, not spaces. Preserve the required casing of string literals, comments, prompts, and quoted identifiers. Document every created object with purpose, owner, dependencies, rules, validation, rollback, and deployment order.
- Never use `alter` to correct a table or view. Reconstruct a table only after explicit user request. For views use `drop`, `commit`, `create`, `commit`; capture prior DDL/backup before drop and inspect dependents.
- Retain every backup until the user explicitly decides to purge it. Never purge automatically.
- On non-migration table recreation, reset identifier sequencing. On a user-declared migration, preserve sequential continuity and disable/re-enable the documented triggers.
- Default PK generation is the trigger call `data.pk_commons.sp_secuencia('data.<table_name>', :new.id)`. Ask only if the user wants a database sequence instead.
- Default table order is `id`, `usercrea varchar2(25)`, `fechcrea timestamp`, `usermodi varchar2(25)`, `fechmodi timestamp`, `compania varchar2(5)`, then business columns.
- Populate audit fields with `nvl(v('user'), 'ORCL')`. If supplied table SQL lacks `compania` or an equivalent, ask whether to add it; exclude it only by explicit project decision.
- Do not create any key, constraint, or index unless the user explicitly requests it and it is recorded.

## UTF-8 Character Encoding

**CRITICAL: Unicode text must be preserved exactly through every step.**

Texts like "agrupación", "Parámetros", "conciliación" contain accented characters (á, ó, ó) that MUST remain intact. Corrupted versions like "agrupaciÃ³n", "ParÃ¡metros", "conciliaciÃ³n" indicate byte sequences were misinterpreted as Windows-1252 or ISO-8859-1.

### Before you write SQL/PL/SQL:

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
   python <skill-root>/scripts/validate_sql_style.py <file> --encoding utf-8
   ```
   - Output must display accented characters correctly
   - If validator output shows mojibake: encoding problem detected
   - Do NOT accept STYLE_PASS if text is corrupted

### After Oracle deployment:

7. **Verify stored text in database**
   - Query `ALL_SOURCE` or object definitions:
     ```sql
     select text from all_source where owner='DATA' and name='<OBJECT>';
     ```
   - Check that á, é, í, ó, ú, ñ, ü appear intact
   - If stored as corrupted bytes (Ã©, Ã¡, etc.): rollback immediately
   - Oracle should store UTF-8 natively if NLS_CHARACTERSET=AL32UTF8

8. **Document encoding at each step**
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

Run `python <skill-root>/scripts/validate_sql_style.py <sql-file-or-directory>` on every generated or changed SQL delivery before handoff. A `STYLE_FAIL` blocks delivery; correct every finding rather than waiving it. Keep its output as validation evidence in the implementation plan.

Keep implementation-plan checkboxes updated. Mark a step complete only with evidence path, environment, timestamp, and result. Deliver scripts, decision record, plan status, validation, rollback procedure, backup retention state, and SQL style result.
