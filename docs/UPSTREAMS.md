# External Upstreams

## Oracle APEX reference repository

- **Repository:** `https://github.com/oracle/apex`
- **Owner:** Oracle
- **Reference branch:** `26.1`
- **Purpose:** official examples, starter and utility applications, plug-ins, code samples,
  application blueprints, and Fusion Apps REST source catalogs.
- **License:** Universal Permissive License 1.0 (UPL-1.0).
- **Retrieved:** 2026-08-25
- **Pinned commit (26.1):** cf20339ffd2d9f70daa88b90267201f5cc2bf14f
- **Classification:** reference only
- **Target APEX:** 26.1 reference review; runtime target remains APEX 24.1.3; validate compatibility in TEST before promotion.

### REST Source Catalogs branch

- **Branch:** rest-source-catalogs
- **Pinned commit:** 5df5693849f3cd4194c589abd0b3637fc88271b1
- **Retrieved:** 2026-08-25
- **Classification:** adapt for reviewed integration contracts only; separate approval is required for endpoint configuration.

### Use policy

This upstream is a **reference source**, not a runtime dependency and not an import target.
Pin every analysis to an APEX release branch that matches the target environment. Inspect
application exports, SQL, plug-ins, credentials, data samples, privileges, and licensing before
reusing an artifact. Preserve the UPL notice when copying a substantial portion of an upstream
file.

The `rest-source-catalogs` branch is scoped to Fusion Apps REST Source Catalogs and must be
evaluated independently from the versioned APEX branches.

### Local review procedure

1. Record the upstream URL, branch, commit SHA, retrieval date, and target APEX version.
2. Classify every candidate as **adopt**, **adapt**, or **reference only**.
3. Do not import database objects, sample data, secrets, application IDs, workspace IDs, or
   authorization assumptions without explicit approval and environment validation.
4. Keep managed clones under `.upstreams/managed/` and optional reference clones under `.upstreams/references/`; both are intentionally ignored by tooling.

The canonical registry is `upstreams.lock.json`. Managed sources support runtime,
QA, or integration workflows. Their recoverable snapshots are stored in
`vendor/upstreams/` and verified by `manifest.json`. Install or update them with
`scripts/Sync-ApexSkillUpstreams.ps1`; this preserves a working copy when a
remote is unavailable and creates a verified backup before replacing a copy.
`Setup-ApexSkills.ps1` and `Initialize-ApexCodexProject.ps1` run this step for
the user. Reference sources remain optional and are used only for consultation
or adaptation. Initialize references with
`Initialize-ApexSkillUpstreams-V2.ps1 -IncludeReferences` and update them with
`Update-ApexSkillUpstreams-V2.ps1 -IncludeReferences`.

To refresh the bundled fallback itself, first review the upstream diff,
compatibility, security and redistribution rights. Then run
`scripts/Export-ApexSkillUpstreamSnapshots.ps1`. The exporter backs up the
previous bundle and lock before replacing the snapshots and pinned commits. If
the `apex-mcp` overlay changed, review it and pass
`-AcceptCurrentApexMcpOverlay` explicitly.


## emilkowalski/skills design reference

- **Repository:** https://github.com/emilkowalski/skills
- **Owner:** Emil Kowalski
- **Reference branch:** main
- **License:** MIT
- **Retrieved:** 2026-08-25
- **Pinned commit:** d23d7f88a2e21c9e4b1418c7abe420f5c1052ba7
- **Target APEX:** Universal Theme-based APEX UX only
- **Classification:** adapt selected design-engineering, motion-review, and restraint principles; React, Expo, Swift, Sonner, and unrelated library workflows are out of scope.

This is a design reference, not a runtime dependency, plug-in source, CDN, or authorization model.
