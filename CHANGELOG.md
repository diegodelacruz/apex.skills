# Changelog

All notable changes to apex.skills are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

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

- Skills inventory: 21 → **30 skills** (26 technical + 4 orchestrators).
- Orchestration hierarchy: flat → **3-level** (1 Maestro → 5 Coordinators → 26 Technical).
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

### Added

#### Core Framework (Phases 1-5)
- **15 specialized Oracle APEX skills** with hierarchical organization.
- **Coordinator skill** (`apex`) for intelligent routing to specialized skills.
- **Apex prefix naming convention** (no emojis) for consistent display.
- **Alphabetical ordering** with unique order numbers for sequencing.

#### Security Hardening (Phase 1)
- Pre-commit hooks with 8 integrated checks: detect-secrets, Black, isort, Bandit, Flake8, exception validation, audit trail capture, large file detection.
- Credentials management via system keyring (`manage_apex_credentials.py`).
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
- Credentials stored in system keyring (per-user, encrypted).

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
