# Project layout

Use `docs/estructura-estandar-proyecto.md` from the canonical skills repository as the source layout. Create only folders relevant to the current project; do not create placeholders for unrelated work.

Every change folder must retain rollback material and reproducible evidence.
For a diagnosed, bounded change this is `change.json` plus snapshot, preflight,
apply, verify and rollback artifacts. Multi-object, migration and high-impact
work additionally retains the numbered execution sequence, decision record and
implementation plan required by `oracle-data-change-governance-final`.
Start the compact manifest from `../assets/change.template.json` and replace
every placeholder with observed evidence before execution.
