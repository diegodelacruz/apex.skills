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
3. Run `Initialize-ApexCodexProject.ps1 -ProjectPath <project-root>` only to prepare local resources and observe the separate Oracle/APEX profile states. The bootstrap does not register MCP, run a handshake, or alter the managed upstream. Use `-SkipRemoteProbe` when no Oracle connection is authorized; otherwise a ready profile may receive only the read-only `dual` probe.
4. Use the shared `<skills-repository>/.venv` by default. Create a project `.venv` only for project-specific dependencies, isolated CI, or explicit user instruction.
5. Present relevant canonical decisions before implementation. A documented explicit project decision overrides a canonical default only for that project.
6. APEX target is 24.1.3. The 24.2 `apex-mcp` upstream is inspection/dry-run only until a compatibility test in TEST is explicitly approved and passes. Do not execute its mutating tools against APEX 24.1.3.
7. Before reporting any milestone, release, documentation update, or skill change as complete, run the applicable audit. At minimum run `python scripts/audit_skill_ecosystem.py` in the skills repository, plus syntax/tests relevant to the modified artifact. Record the evidence and resolve broken links or references before handoff.
8. Continue with `apex-delivery-lifecycle-safe`, using `oracle-data-change-governance-final` for DATA changes.

Consult the repository document `docs/auditoria-obligatoria.md` for audit criteria and evidence requirements.
