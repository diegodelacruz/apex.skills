# Project layout

Use `docs/estructura-estandar-proyecto.md` from the canonical skills repository as the source layout. Create only folders relevant to the current project; do not create placeholders for unrelated work.

Simple reads create no change folder. A one-off confirmed DML request uses the
direct SQL route and normal execution audit; it does not require a bundle,
snapshot, preliminary count, rollback file or implementation plan. Use a
`change.json` package when a fingerprint preflight or coordinated object work
materially requires it. A snapshot is optional and only included when the user
requested a backup. Multi-object and migration work retains the decision and
implementation records that fit its scope. Start a bundle from
`../assets/change.template.json` and replace every placeholder with observed
evidence before execution.
