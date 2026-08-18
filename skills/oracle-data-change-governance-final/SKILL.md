---
name: oracle-data-change-governance-final
description: Govern documented Oracle DATA object changes for TEST and production using the final project rules for backup, rebuild, audit fields, identifier triggers, decisions, plans, and rollback. Use for any table, view, sequence, trigger, index, constraint, package, or deployment script change.
---

# Final DATA Change Governance

## Required records and decision precedence

Create `control-proyecto/cambios/<id>/decisions.md` and `implementation-plan.md` before executable SQL. First present applicable canonical skill decisions to the user. An explicit decision recorded for the current project then takes precedence for that project; do not silently override it.

## Object and script rules

- Official objects live in `data`; backups are created in the current user's schema.
- SQL filenames/content are lower-case and use physical four-column tabs, not spaces. Document every created object with purpose, owner, dependencies, rules, validation, rollback, and deployment order.
- Never use `alter` to correct a table or view. Reconstruct a table only after explicit user request. For views use `drop`, `commit`, `create`, `commit`; capture prior DDL/backup before drop and inspect dependents.
- Retain every backup until the user explicitly decides to purge it. Never purge automatically.
- On non-migration table recreation, reset identifier sequencing. On a user-declared migration, preserve sequential continuity and disable/re-enable the documented triggers.
- Default PK generation is the trigger call `data.pk_commons.sp_secuencia('data.<table_name>', :new.id)`. Ask only if the user wants a database sequence instead.
- Default table order is `id`, `usercrea varchar2(25)`, `fechcrea timestamp`, `usermodi varchar2(25)`, `fechmodi timestamp`, `compania varchar2(5)`, then business columns.
- Populate audit fields with `nvl(v('user'), 'ORCL')`. If supplied table SQL lacks `compania` or an equivalent, ask whether to add it; exclude it only by explicit project decision.
- Do not create any key, constraint, or index unless the user explicitly requests it and it is recorded.

## Completion gate

Keep implementation-plan checkboxes updated. Mark a step complete only with evidence path, environment, timestamp, and result. Deliver scripts, decision record, plan status, validation, rollback procedure, and backup retention state.
