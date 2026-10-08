---
name: apex-project-workspace
category: "Apex Project Management"
order: 10
tags: ["workspace", "organization", "documentation"]
description: "Create and maintain the control-proyecto project workspace."
---

# APEX Project Workspace

## Workflow

Create and maintain the structure in `references/project-layout.md` at the root of every APEX project.

- Create `control-proyecto/decisiones/decisiones-globales.md` at project start and record each user/agent decision with date, source, rationale, impact, and status.
- Create `control-proyecto/planes/plan-maestro.md` and track every change with Markdown checkboxes/statuses.
- Delegate each data-object or APEX live change to a separate `control-proyecto/cambios/<id-cambio>/` folder. A diagnosed, bounded change may use the compact `change.json` package; multi-object, migration or high-impact work uses the full governance templates.
- Store evidence, QA screenshots, traces, and reports in the matching `<id-cambio>` folder.
- Store the final Word manual and its editable source under `control-proyecto/manuales/`; only approved QA evidence may enter the manual.
- Do not store credentials, browser authentication state, wallets, or sensitive production data in the workspace.
