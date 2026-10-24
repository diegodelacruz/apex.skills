# Changelog

All notable changes to apex.skills are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Security
- Stop printing the Oracle password from `manage_apex_credentials.py sqlcl-conn`, which now reports only user and DSN; the bootstrap SQLcl probe uses the new `sqlcl-probe` action, which sends credentials to SQLcl over stdin instead of PowerShell variables, command-line arguments, or temporary files. The probe disables SQLcl substitution before `connect`, so passwords containing `&` work, and accepts Oracle user names containing `$` or `#`.
- Reject external-repository identifiers that would read, write, or delete files outside `control-proyecto/external-repos/` or overwrite its index.
- Record the reconciliation of the 2026-10-01 audit branch against `main`, including which findings are fixed, ported, obsolete, or still open, in `docs/decisiones/20261023-reconciliacion-auditoria-seguridad.md`.

### Added
- Add `scripts/audit_semantic_checks.py`, a read-only diagnostic salvaged from PR #15 that reports tracked scripts and top-level docs no other tracked file mentions (SM08) and key docs whose labelled update date is older than 180 days (SM09); it never changes files, exits 1 on findings, and is not a CI gate until its current findings are reviewed with the user. The per-commit classification of PR #15 is in `docs/decisiones/20261023-rescate-pr15-auditoria-semantica.md`.

### Fixed
- Remove an unreachable legacy block from `Update-ApexSkillUpstreams-V2.ps1` that used the undefined `$repos` variable; a successful `-IncludeReferences` update no longer creates a second empty backup directory or prints `UPDATE_COMPLETE` twice.

### Changed
- Update development tooling consolidating the open Dependabot updates: Black 26.5.1, isort >=9.0.1, flake8 >=7.3.0, pylint >=4.0.7, python-docx >=1.2.0, and GitHub Actions `actions/checkout@v7`, `actions/setup-python@v7`, `codecov/codecov-action@v7`; align the pre-commit hook revisions and configuration guides, and apply Black 26 formatting to one docstring.
- Define who executes an Oracle/APEX change and what counts as the single confirmation: a descriptive request is not a confirmation, `paso a paso` defaults to user execution, and `confirmed=true` requires an explicit agent-execution phrase or an affirmative reply; remove documentation that said a direct request needs no further approval.
- Document the proposed read-only `inspect_apex_page` tool (not implemented), with measured evidence, design, acceptance criteria, and the related pending backlog.
- Remove the fixed five-step cap from Oracle/APEX step-by-step mode; plans now announce `M` total steps, and all-steps execution stops at its first execution error while reporting unexecuted steps explicitly.
- Validate separate column and table comment steps through `ALL_COL_COMMENTS` and `ALL_TAB_COMMENTS` templates.
- Define the default Oracle/APEX step-by-step and all-steps modes, including one initial decision, baseline comparison, bounded checkpoints, consolidated validation, and no automatic correction on failure.
- Preserve the classified SQLcl process-failure code for every read-only batch query and its global result.
- Make `execute_readonly_batch` fail closed on missing output markers, SQL*Plus/SQLcl errors, and pre-marker Oracle connection/authentication failures; preserve query results and report an audit warning if batch audit persistence fails.
- Make `rollback.sql` optional in coordinated change bundles and clarify that a declared rollback script is not executed automatically.
- Reject a bundle that declares `snapshot` when the user declines a backup.
- Update `Deploy-ApexPage.ps1` help examples to include the required action confirmation and backup choice.
- Make object reviews, data reads, and specification requests immediate and read-only, with only a minimal destination check when needed.
- Require one mutation confirmation covering environment, target, exact operation, and backup choice; backups and preliminary row counts are no longer routine prerequisites.
- Route isolated DML and one-object DDL directly, reserving change bundles for coordination or meaningful fingerprint checks.
- Record `profile_load`, `sqlcl_process`, and `route_total` timings for controlled SQL execution so profile loading, SQLcl process time, and total route time can be distinguished.
- Align Oracle/APEX skills, adapters, project templates, capability documentation, and tests with these rules; clarify that migration rollback markers are in-memory prototype metadata, not backups or database restoration, and route migration planning separately from coordinated schema changes.
- Require independent repository audits to report contradictions with source, rationale/history, scope, and implications, without changing findings before they are reviewed with the user.
- Require explicit action confirmation and backup choice in all controlled MCP write tools; execute an accepted SQL backup or bundle snapshot before the requested mutation, and stop if it is missing or fails.
- Align workspace, lifecycle, APEX use-case and recovery guidance with the single global mutation confirmation, optional scoped backups, and the direct path for punctual DML; rename the application-generator's simulated recovery marker.
- Apply the mutation decision gate to the controlled SQLcl MCP and PowerShell entry points; execute accepted SQL/bundle backups before changes and block the change if the backup is missing or fails.
- Ignore local `.codex-tmp/` execution artifacts in Git and exclude them from secret scanning, which uses `--all-files` and otherwise scans those temporary files.
- Persist correlated start and completion events with hashes, result, exit code, and timings from the controlled PowerShell SQL, APEX page, and change-bundle routes; block before execution if start logging fails and warn against automatic retry if completion logging fails.
- Keep the local audit log in JSON Lines across the optional manual pre-commit script, and correct documentation that described the ignored mutable file as automatic or Git-backed.
- Keep the full SQLcl runtime probe on the explicit `doctor()` diagnostic route; normal reads and executions attempt the requested operation directly and report runtime startup errors from that attempt.
- Do not inspect Oracle/APEX grants before, during, or after requested operations; report the service response and inspect grants only when explicitly requested or diagnosing an observed access error.
- Clarify that the SQLcl workspace inventory and TEST/Production context checks in the DBA request guide apply to initial provisioning, not routine reads or each later operation.

- Added a live Oracle/APEX change protocol that retains a confirmed diagnostic
  context, validates a versioned `change.json` bundle, and records bounded
  preflight/apply/verify execution evidence without secrets. Existing SQL and
  native APEX deployment routes remain compatible.
- Centralized Oracle and App Builder profile reads and writes on the ignored repository-root `.env`; removed alternate credential-source fallback and direct PowerShell connection overrides, aligned MCP wrappers, validators, setup guidance, and credential regressions with the single source.
- Retired the legacy APEX REST/SQLcl client facades, made them fail closed without retaining supplied credentials, and aligned their skill metadata and regression tests with the retired status.
- Corrected stale architecture counts and hierarchy labels; synchronized catalog descriptions and tags from all skill frontmatter; distinguished the retired compatibility entry from 22 active specialists; aligned order authoring guidance with the documented duplicate-order compatibility exception; added the missing external-context Claude command adapter; made Markdown audit fail closed for un-audited submodules; removed unsupported approver assignments, stale synchronization and cycle-certification claims; labeled old release counts as historical; renamed a presence-only test that had claimed to prove acyclic dependencies.
- Corrected `CLAUDE.md` to match the configured 15 pre-commit hooks, current role/status taxonomy, local-only audit trail, test markers, and named documentation references; retained the documented duplicate skill order values pending external-consumer verification.
- Marked all six development-status skills in the repository tree and clarified the retired API compatibility entry and supported APEX deployment route.
- Replaced the nonexistent `v1.0.0` release examples in `docs/GITHUB-SETUP.md` with explicit placeholders after confirming the public repository has no tags or releases.
- Made the ecosystem subaudit label documented external-link N/A results explicitly and scoped the quality Q03 evidence to local links.
- Corrected application-generation and data-orchestration catalogs, skill instructions, dependency maps, and regression expectations so the retired API adapter is not described as an operational deployment, sync, or test-setup dependency; preserved its historical invocation entry.
- Made the standalone SQLcl fallback use the current user's profile path, removed the machine-specific `mcp` checkout location from historical documentation, and replaced hard-coded repository path examples with explicit root-path placeholders.
- Propagated the default Oracle schema owner `DATA` through the coordinator, agent prompt, schema automation, and data orchestrator; explicit schema names override it, related DDL/DML must be owner-qualified, and governed backup objects retain their connected-schema exception.
- Updated `.env.example` with the configured TEST Oracle/APEX endpoints and commented production APEX endpoint/workspace reference; credential values remain placeholders.
- Reduced routine preflight for focused Oracle/APEX reads to one minimal identity check followed immediately by the target query, reusing live-session evidence; clarified that historical failures are context only and must be rechecked on the current route.

### Added

- Added the domain-agnostic Trazabilidad End-to-End (TE2E) diagnostic method for data present at a source but missing or wrong downstream: witness and mandatory control records, a bidirectional Markdown trace map, per-stage evidence, divergence measured against each stage's expected representation (conformity), so verified aggregation or netting is not a divergence and wrong-value or duplicate destinations are traced, D0–D7/DX divergence taxonomy, root-cause/probable/evidence-limitation criteria, an anti-"configuration" rule, cost bounds, and read-only operation. It includes an Oracle/APEX probe adapter verified in TEST, a trace-map template, coordinator, routing, and adapter links, manual behavior scenarios, a decision record, and regressions.
- Added `execute_readonly_batch` for up to 25 validated SELECT statements in one read-only SQLcl session, with per-query Oracle errors, same-session identity, timings, and digest-only audit; documented and verified APEX page snapshot queries for TEST.
- Added a whole-repository Markdown coverage and link auditor with fragment checks, explicit exclusions, external URL status reporting, regression tests, and shared CI/pre-commit invocation.
- Added a bound, single-SELECT SQLcl route in an Oracle read-only transaction, with hash-only audit logging, so metadata reads do not depend on a repository SQL artifact.
- Added regressions for inline read-only query validation, ORA-20987-independent metadata routing, and the default DATA schema owner.
- Restricted inline SQLcl reads to a single physical line and rejected control characters to prevent SQLcl client-command injection.
- Added a shared local CI runner and aligned GitHub Actions with Python 3.13.
- Added `.python-version` and documented the local CI workflow and Python baseline.
- Added an initial 55% combined coverage gate, with 80% retained as a gradual target.
- Added tests for whitespace detection in staged and untracked files.
- Synchronized SKILLS-QUICK-REFERENCE.md with 4 missing skills (apex-code-generation-safe, apex-api-client-safe, apex-automated-testing-safe, apex-data-migration-safe).
- Re-enabled `validate-exception-handling` pre-commit hook (Python-based, cross-platform).
- Added 12 new tests for `manage_apex_credentials.py` (coverage 35% → 77%).
- Documented 7 infrastructure scripts with Status/Tests/Dependencies metadata.
- Added Infrastructure Scripts table to root README.md.
- Updated `skills/README.md` alphabetical list to all 30 skills.
- Added return type annotations to `path_setup.py` functions.

### Removed

- Removed stale milestone files (`HITO-0-DIAGNOSTICO.md`, `HITO-0-RESULTADO.md`, `HITO-2-RESULTADO.md`, `HITO-3-RESULTADO.md`, `PLAN-LARGO-PLAZO.md`).
- Removed redundant `skills/CANONICAL-SKILLS-ULTIMATE.md` (superseded by `skills/README.md`).
- Removed tracked `.DS_Store` and added it to `.gitignore`.
- Cleaned up `.upstream-backups/` directory.

### Fixed

- Fail closed before SQLcl starts when a write artifact contains characters not representable in CP1252; read-only queries and batches report explicit input substitutions when they opt into replacement.
- Preserve Spanish SQL literals sent through the Windows SQLcl standard-input code page, while decoding SQLcl output as tolerant UTF-8 so malformed bytes cannot abort controlled results.
- Read `runtime-state.json` with UTF-8 BOM tolerance so Windows PowerShell 5.1 runtime state is recognized by the local doctor.
- Closed a routing gap that allowed omitted Oracle object owners to inherit the connected user's schema despite the existing DATA governance default; added a regression for coordinator and workflow instructions.
- Fixed SQLcl read-only query execution by terminating `SET TRANSACTION READ ONLY` before the SELECT statement.
- Clarified that new Oracle objects default to the DATA schema, and that repository-backed SQL tools require temporary artifacts inside the MCP checkout with a same-environment APEX SQL fallback after artifact or context-helper failures.
- Changed `ApexSchemaSpec` to default generated Oracle objects to `DATA`, matching the DATA governance skill while preserving explicit owner overrides.
- Stopped treating a SQLcl login that differs from an APEX workspace parsing schema as a metadata-access denial; APEX diagnostics now retry the verified same-environment APEX MCP route and fall back to public metadata views when a page-detail adapter is incompatible.
- Restored the regular-expression import used by the MCP adapter contract validator after it was removed from the active working copy, preventing a Python `NameError` during project initialization.
- Clarified that remote Oracle/APEX source inspection may use a repository-backed read-only SQL artifact when required by the configured production connector; a non-Git project folder does not block the requested inspection.
- Fixed upstream setup failing after successful synchronization when Windows cannot remove a locked staging file; cleanup now warns and preserves staging for later inspection.
- Fixed cross-platform secret-baseline matching and excluded Git internals from full repository scans; replaced a credential-shaped documentation example that triggered GitHub CI.
- Fixed local CI failures in formatting, lint, and type checks for external-repository context tooling.
- Fixed test expectation from 21 → 30 skills in `test_quality_audit.py`.
- Fixed stale reference in `docs/setup-claude-code.md` pointing to removed file.

### Changed

- Replaced the hardcoded Oracle/APEX environment permission matrix with the effective grants of the credential configured for the selected environment; added read-only session/destination and privilege inspection at task start when available.
- Removed the environment-only block from native APEX import so Oracle/APEX can return the actual result for the selected credential; generic SQL and APEX routes do not grant privileges beyond that account's grants.
- Made SQLcl environment selection use the requested environment or `DB_ENV`; it no longer falls back silently to TEST when no target is configured.
- Removed stale approval language from APEX page/schema examples and made DATA governance defaults inferable so routine schema work does not stop for avoidable questions.
- Aligned APEX delivery/data orchestrators and engineering prompts with configured credentials and DBA/APEX-granted privileges; removed fixed per-environment permission statements.
- Restored concrete design-review and QA orchestration phases and deliverables while keeping them advisory and non-blocking; clarified boundaries with specialist implementation and test skills.
- Documented tool routing for Oracle inspection/execution and APEX inspection/import by operation, including that connector surfaces do not grant privileges and connector labels do not prove target identity.
- Required the local CI runner before integration and clarified repository-wide audit requirements before GitHub publication.
- Made changelog updates part of the required change and publication workflow.
- Updated architecture, security, and GitHub setup documentation to reflect the current test suite, CI status, and changelog version.
- Hardened the local secret scan to inspect upstream metadata and removed global line exclusions.
- Added only verified public upstream commit and archive hashes to the secret-scanner baseline.
- Removed secret-scan exclusions from pre-commit and the security audit script.
- Corrected temporary baseline filtering and resolved Git executable lookup for security linting.
- Aligned the quality auditor with the runner's resolved Git executable and whitespace checks.

---

## [1.2.0] - 2026-09-17

> Historical release record. Its capability descriptions and inventory counts
> reflect the claims made at that time; use the current frontmatter inventory
> and current workflow maps as the source of truth.

### Added

- **4 new technical skills** (HITOs 1-5):
  - `apex-code-generation-safe` — Safe code generation with validation
  - `apex-api-client-safe` — REST API client with OAuth2 and retry logic
  - `apex-automated-testing-safe` — Selenium test generation for APEX UI
  - `apex-data-migration-safe` — Data migration with rollback support
- **1 new orchestrator**: `apex-application-generator-complete` — End-to-end APEX app generation (HITOs 1-5)
- **4 new coordinator orchestrators**:
  - `apex-data-orchestrator-safe` — Coordinates schema → migration → sync
  - `apex-design-review-orchestrator` — Coordinates design review workflow
  - `apex-qa-orchestrator-safe` — Coordinates QA workflows
  - `apex-delivery-lifecycle-zaimella` — Integrates GPZ + APEX delivery
- Orchestrator hierarchy tests (`test_orchestrator_hierarchy.py`, `test_orchestration_coordination.py`).
- Skill dependency matrix (`docs/SKILL-DEPENDENCY-MATRIX.md`).
- Cross-skill integration guide (`docs/CROSS-SKILL-INTEGRATION.md`).
- Orchestrator audit documentation (`docs/ORCHESTRATOR-AUDIT.md`).
- Agent-neutral quality matrix and deterministic `audit_quality_score.py` gate.

### Changed

- Historical skills inventory claim: 21 → **30 skills** (26 technical + 4 orchestrators); not the current inventory.
- Historical hierarchy claim: flat → **3-level** (1 Maestro → 5 Coordinators → 26 Technical); superseded by the current L0-L3 role taxonomy.
- Test suite: 202 → **426 tests** (100% pass rate).
- Quality audit score: 85/100 → **100/100** (all Q01-Q09 passing).

---

## [1.1.0] - 2026-09-17

### Added

- **2 new skills**: `apex-page-automation-safe`, `apex-schema-automation-safe`.
- Corresponding script modules: `apex_page_generator.py`, `apex_schema_generator.py`, `apex_application_generator.py`, `apex_code_generators.py`, `apex_rest_client.py`, `apex_test_generators.py`, `apex_data_migration.py`.
- Zaimella Methodology (GPZ) skill (`apex-zaimella-gestion-proyectos`).
- Input validation for `apex_export_utilities.py`.
- Ecosystem evolution policy (`docs/POLITICA-EVOLUCION-ECOSISTEMA.md`).
- Upstream provenance and governance controls.
- Quality gate integration in CI.
- APEX 24.1.3 MCP compatibility documentation and patches.

### Changed

- Skills inventory: 15 → 21.
- Test suite expanded with coverage for new modules.
- Aligned quality matrix scoring across agents.

---

## [1.0.0] - 2026-08-21

> Historical release record; statements below describe the release snapshot, not current metadata policy.

### Added

#### Core Framework (Phases 1-5)
- **15 specialized Oracle APEX skills** with hierarchical organization.
- **Coordinator skill** (`apex`) for intelligent routing to specialized skills.
- **Apex prefix naming convention** (no emojis) for consistent display.
- Alphabetical ordering with order values for sequencing (uniqueness was the original release claim; current duplicate-order compatibility is documented separately).

#### Security Hardening (Phase 1)
- Pre-commit hooks with 8 integrated checks: detect-secrets, Black, isort, Bandit, Flake8, exception validation, audit trail capture, large file detection.
- Credential profile setup through `manage_apex_credentials.py`.
- `.secrets.baseline` for known credential detection.

#### Code Quality & Testing (Phases 2-3)
- 46 comprehensive tests (100% passing).
- 3 reusable utility modules: CLIParser, ApexMetadata, path_setup.
- Type hints and docstrings across all modules.
- Test fixtures: f109.zip and f130.zip (actual APEX exports).

#### Skills Organization (Phase 4)
- 15 skills with complete YAML frontmatter (name, category, order, tags, description).
- Skills catalog (`skills/README.md`) and quick reference (`skills/SKILLS-QUICK-REFERENCE.md`).

#### Audit Trail System (Phase 5)
- Git-based automatic audit trail capture (zero tokens).
- `apex-audit-decisions-log` skill for visualization and export.
- Configuration in `.claude/settings.json`.

#### Repository Organization
- CLAUDE.md, CONTRIBUTING.md, ARCHITECTURE.md, CONFIGURATION-GUIDE.md.
- PR template, CI workflow, security audit script.

### Security

- No hardcoded secrets in codebase.
- Pre-commit secrets detection, Bandit scanning (73 checks), private key detection.
- Credential profiles managed locally per user.

---

## Metrics

| Metric | Value |
|--------|-------|
| Skills | 30 (26 technical + 4 orchestrators) |
| Tests | 426 (100% pass rate) |
| Coverage | 62.68% |
| Quality Score | 100/100 |
| Pre-commit Hooks | 14/14 passing |

---

**Last Updated**: 2026-09-24
