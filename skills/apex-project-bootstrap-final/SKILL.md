---
name: apex-project-bootstrap-final
category: "Apex Project Management"
order: 9
tags: ["setup", "initialization", "bootstrap", "governance"]
description: "Initialize an APEX project with workspace and governance foundations."
---

# Final APEX Project Bootstrap

## Workflow

1. Create the visible `control-proyecto/` workspace and global decision/master-plan files.
2. Run `Setup-ApexSkills.ps1` once for the workstation. It prepares the three managed upstreams from bundled snapshots, checks remotes, backs up before updating, and preserves a usable local copy when a remote is unavailable. Record the selected revisions in the global decision record.
3. Run `Initialize-ApexCodexProject.ps1 -ProjectPath <project-root>` to prepare local resources and report separate Oracle/APEX profile states. It does not alter MCP registration. Existing MCP registrations and any other configured database route remain usable regardless of bootstrap status.
4. Use the shared `<skills-repository>/.venv` by default. Create a project `.venv` only for project-specific dependencies, isolated CI, or explicit user instruction.
5. Apply relevant project decisions as context; do not require a separate approval before carrying out a direct user request.
6. Use the APEX version present in the target environment. A version mismatch is reported from an actual tool/database error and is not a skill-level execution veto.
7. Before reporting any milestone, release, documentation update, or skill change as complete, run the applicable audit. At minimum run `python scripts/audit_skill_ecosystem.py` in the skills repository, plus syntax/tests relevant to the modified artifact. Record the evidence and resolve broken links or references before handoff.
8. Continue with `apex-delivery-lifecycle-safe`, using `oracle-data-change-governance-final` for DATA changes.

Consult the repository document `docs/auditoria-obligatoria.md` for audit criteria and evidence requirements.
