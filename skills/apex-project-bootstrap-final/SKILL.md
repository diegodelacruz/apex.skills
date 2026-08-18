---
name: apex-project-bootstrap-final
description: Start every Oracle APEX project with the final canonical workspace, dependency, source-cloning, decision-precedence, and compatibility policies. Use before design, implementation, QA, or documentation work in any new APEX project.
---

# Final APEX Project Bootstrap

1. Create the visible `control-proyecto/` workspace and global decision/master-plan files.
2. Clone all three canonical upstreams for every new project through `Initialize-ApexSkillUpstreams-V2.ps1`: `apex-mcp`, `zaimella-skill`, and `zaimella-apex-oracle`. Record revisions in the global decision record.
3. Use the shared `<skills-repository>/.venv` by default. Create a project `.venv` only for project-specific dependencies, isolated CI, or explicit user instruction.
4. If a dependency is absent and automatic approval is enabled, install it in the applicable environment and record it. Otherwise ask once before installing.
5. Present relevant canonical decisions before implementation. A documented explicit project decision overrides a canonical default only for that project.
6. APEX target is 24.1.3. The 24.2 `apex-mcp` upstream is inspection/dry-run only until a compatibility test in TEST is explicitly approved and passes. Do not execute its mutating tools against APEX 24.1.3.
7. Continue with `apex-delivery-lifecycle-safe`, using `oracle-data-change-governance-final` for DATA changes.
