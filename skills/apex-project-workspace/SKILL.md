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

- Create decision and master-plan files when the user requests project workspace/bootstrap or the project scope requires formal lifecycle tracking; they are not prerequisites for a punctual object request.
- Track formal, coordinated project changes in `control-proyecto/planes/plan-maestro.md`; a one-off confirmed DML operation uses the direct SQL route and normal audit event without a plan entry or change folder.
- Create `control-proyecto/cambios/<id-cambio>/` only when a bundle/preflight, multi-object coordination, migration plan, or material delivery evidence is warranted. Do not route a punctual DML request through this workspace workflow.
- Store formal change evidence, QA screenshots, traces, and reports in the matching `<id-cambio>` folder; retain the normal execution audit for punctual changes.
- Store the final Word manual and its editable source under `control-proyecto/manuales/`; only approved QA evidence may enter the manual.
- Do not store credentials, browser authentication state, wallets, or sensitive production data in the workspace.
