---
name: apex-project-workspace
description: Initialize and maintain the visible control-proyecto workspace for Oracle APEX projects. Use at project start, when organizing agent-generated decisions, implementation plans, numbered DATA change scripts, QA evidence, screenshots, traces, or final manuals. Creates a traceable, versionable project control structure without changing Oracle or APEX.
---

# APEX Project Workspace

Create and maintain the structure in `references/project-layout.md` at the root of every APEX project.

- Create `control-proyecto/decisiones/decisiones-globales.md` at project start and record each user/agent decision with date, source, rationale, impact, and status.
- Create `control-proyecto/planes/plan-maestro.md` and track every change with Markdown checkboxes/statuses.
- Delegate each data-object change to a separate `control-proyecto/cambios/<id-cambio>/` folder using `oracle-data-change-governance` templates.
- Store evidence, QA screenshots, traces, and reports in the matching `<id-cambio>` folder.
- Store the final Word manual and its editable source under `control-proyecto/manuales/`; only approved QA evidence may enter the manual.
- Do not store credentials, browser authentication state, wallets, or sensitive production data in the workspace.
