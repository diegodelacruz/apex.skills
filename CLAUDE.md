# apex.skills - Oracle APEX Development Framework

> Regla obligatoria: leer y cumplir [la política canónica de evolución](docs/POLITICA-EVOLUCION-ECOSISTEMA.md) antes de modificar este repositorio. Ningún archivo puede obligar técnicamente a un agente externo arbitrario; la aplicación efectiva combina política canónica, adaptadores, hooks, CI y revisión independiente.

## Overview

**apex.skills** is a canonical framework for Oracle APEX application development and deployment. It provides:

- **31 skill entries** (1 entry coordinator, 7 orchestrators, 22 active specialists, and 1 retired compatibility entry); development outlines are labeled in their metadata
- **Security-hardened pre-commit hooks** for code quality, secrets detection, and exception validation
- **Comprehensive audit trail system** (Git-based, zero-token automatic capture)
- **Governance templates** for page ranges, DATA changes, and environment alignment
- **Development patterns** extracted from production deployments
- **Zaimella Methodology (GPZ)** integration for comprehensive project management

---

## APEX Behavioral Rules (always active)

These rules apply to every conversation in this project. They are NOT optional
and do NOT require the user to invoke a skill or say "usa apex".

### Notation

- `<number>.<number>` in APEX context = application ID + page ID. Example:
  `109.100` means application 109, page 100. Never interpret as a decimal number.
- Words like "page", "pagina", "página", "application", "aplicación" before a
  dotted pair confirm APEX context.

### Fluency

- **Act immediately.** The user's request IS the authorization. Never ask
  "should I connect?", "do you want me to query?", or "can I check the metadata?".
- **Infer, don't interview.** Derive application, page, environment, schema, and
  version from context and the database. Only ask when genuinely ambiguous.
- **Route silently.** Never ask which skill/workflow to use.
- **No browser.** Inspect and verify APEX objects via SQL against APEX metadata
  views (`apex_application_pages`, `apex_application_page_regions`,
  `apex_application_page_items`, etc.) and Oracle data dictionary views
  (`ALL_OBJECTS`, `ALL_TAB_COLUMNS`, etc.). Never open a browser to App Builder.

### Environment

- **Default: TEST.** If the user does not specify, use `--environment test`.
- If the user says production, respect immediately — no extra confirmation.
- Never silently switch from test to production.

### Modifications

- Before the first write in a session, ask: "paso a paso o todos los pasos?"
  Default to step-by-step. Do not ask again after that.
- In step-by-step: instruct one change, wait for confirmation, verify via
  database query, then advance. See `skills/apex/SKILL.md` for full details.

### Skills (invocable via `/skill-name`)

Skills are in `.claude/commands/`. The coordinator `/apex` routes to specialists.
For the full catalog see `skills/README.md`.

---

## Repository Structure

```
apex.skills/
├── .claude/
│   └── settings.json           # Skills organization, audit config, hooks setup
├── .hooks/
│   └── pre-commit.sh           # Auto-capture audit trail on every commit
├── .pre-commit-config.yaml     # Git hooks configuration (Black, isort, Bandit, detect-secrets)
├── .bandit.yaml                # Security linting rules
├── .gitignore                  # Git ignore patterns
├── .mcp.json.example           # MCP (Model Context Protocol) configuration template
├── .env.example                # Environment variables template (no secrets!)
│
├── docs/
│   ├── MANUAL-DE-USO.md       # User manual (Spanish)
│   ├── TESTING.md             # Testing guide and coverage info
│   ├── ARCHITECTURE.md        # System architecture documentation
│   ├── GUIA-CREAR-NUEVA-SKILL.md # Normative guide for new skills
│   ├── POLITICA-EVOLUCION-ECOSISTEMA.md # Mandatory ecosystem evolution policy
│   ├── SECURITY-THREATS.md   # Security threat model and risks
│   ├── ORACLE-APEX-DOCUMENTATION-POLICY.md # APEX documentation and standards policy
│   └── [other guides and policies; see docs/ for the complete inventory]
│
├── scripts/
│   ├── cli_utils.py           # Unified argument parsing (CLIParser class)
│   ├── apex_metadata.py       # YAML field extraction (ApexMetadata class)
│   ├── path_setup.py          # Centralized path setup functions
│   ├── manage_apex_credentials.py  # Secure credential management
│   ├── validate_apex_mcp_*.py # MCP connection validation
│   └── [other utility scripts]
│
├── skills/
│   ├── README.md              # Master navigation guide (31 entries: 1 coordinator + 7 workflow roles + 22 active specialists + 1 retired entry)
│   ├── SKILLS-QUICK-REFERENCE.md  # Quick lookup tables
│   ├── apex/                  # Maestro coordinator (routes requests)
│   ├── apex-application-generator-complete/  # DEVELOPMENT - API deployment phase is non-operational
│   ├── apex-data-orchestrator-safe/  # DEVELOPMENT - APEX import is separate
│   ├── apex-design-review-orchestrator/  # Orchestrator for design review
│   ├── apex-qa-orchestrator-safe/  # Orchestrator for QA workflows
│   ├── apex-delivery-lifecycle-zaimella/  # DEVELOPMENT - GPZ + APEX delivery workflow
│   ├── apex-audit-decisions-log/  # Audit trail viewer
│   ├── apex-database-diagnostics/
│   ├── apex-delivery-lifecycle-complete/
│   ├── apex-delivery-lifecycle-safe/
│   ├── apex-automated-testing-safe/  # DEVELOPMENT - Selenium testing framework
│   ├── apex-engineering-safe/
│   ├── apex-code-generation-safe/  # DEVELOPMENT - code generation framework
│   ├── apex-data-migration-safe/  # DEVELOPMENT - ETL/migration framework
│   ├── apex-blueprint-design-safe/  # Reviewable blueprints
│   ├── apex-environment-alignment-complete/
│   ├── apex-export-qa-safe/
│   ├── apex-page-range-governance/
│   ├── apex-pattern-mining-safe/
│   ├── apex-project-bootstrap-final/
│   ├── apex-project-workspace/
│   ├── apex-rest-source-catalogs-safe/
│   ├── apex-ui-craft-safe/
│   ├── apex-page-automation-safe/  # Page creation and management
│   ├── apex-schema-automation-safe/  # Database schema creation and management
│   ├── apex-solution-design/
│   ├── apex-user-manual/
│   ├── apex-zaimella-gestion-proyectos/  # Zaimella Methodology (GPZ)
│   └── oracle-data-change-governance-final/
│
├── tests/
│   ├── fixtures/
│   │   ├── apex-exports/      # APEX export ZIP files (f109.zip, f130.zip)
│   │   └── sql-examples/      # SQL/PL-SQL test cases
│   ├── test_cli_utils.py
│   ├── test_apex_metadata.py
│   ├── test_path_setup.py
│   ├── test_apex_export_utilities.py
│   └── test_apex_mcp_manager.py
│
├── control-proyecto/
│   └── .bitacora.json        # Audit trail (auto-generated, added to .gitignore)
│   └── .bitacora.template.md # Audit report template
│
├── pyproject.toml            # Python project configuration (Black, isort, pytest, coverage)
├── pytest.ini                # pytest configuration
├── requirements.txt          # Python dependencies
├── README.md                 # Project overview
└── upstreams.lock.json       # Upstream dependencies lock file
```

---

## Skills Organization

All 31 skill entries (1 entry coordinator + 7 workflow roles + 22 active specialists + 1 retired compatibility entry) are organized with:
- **"Apex" prefix** (no emojis) for clear branding
- **Alphabetical ordering** in menus
- **Order values** for display sequencing; the duplicate `3.5` values are intentionally retained pending verification of external discovery consumers. Do not renumber from this document alone.
- **Comprehensive tags** for filtering by workflow, access level, cost
- **4-level role hierarchy:** L0 entry coordinator (`apex`) → L1 broad orchestrators (4 lifecycle/application flows) → L2 focused orchestrators (3 workflows) → L3 active specialists (22); the retired compatibility entry is outside active routing. Development status is a separate metadata field.

### Skill Categories

#### Orchestrators (Coordinators & Maestro)
| Category | Skills | Order |
|----------|--------|-------|
| Maestro (Entry Point) | apex | 14 |
| Delivery Orchestration | apex-delivery-lifecycle-zaimella | 3.5 |
| Application Generation Orchestrator | apex-application-generator-complete | 23 |
| Design Review Orchestrator | apex-design-review-orchestrator | 11.5 |
| QA Orchestrator | apex-qa-orchestrator-safe | 6.5 |
| Data Orchestrator | apex-data-orchestrator-safe | 13.5 |

#### Technical Skills (25)
| Category | Skills | Order |
|----------|--------|-------|
| Apex Audit & Decisions | apex-audit-decisions-log | 0 |
| Apex Database & Diagnostics | apex-database-diagnostics | 1 |
| Apex Delivery & Lifecycle | apex-delivery-lifecycle-complete, apex-delivery-lifecycle-safe | 2-3 |
| Apex External Context & Learning | apex-external-context-learn | 3.5 |
| Apex Engineering & Design | apex-engineering-safe, apex-solution-design | 4, 11 |
| Apex Environment & Alignment | apex-environment-alignment-complete | 5 |
| Apex Export & QA | apex-export-qa-safe | 6 |
| Apex Page Range Governance | apex-page-range-governance | 7 |
| Apex Pattern Mining | apex-pattern-mining-safe | 8 |
| Apex Project Management | apex-project-bootstrap-final, apex-project-workspace | 9-10 |
| Apex Documentation | apex-user-manual | 12 |
| Oracle Data Governance | oracle-data-change-governance-final | 13 |
| Apex Blueprint Design | apex-blueprint-design-safe | 15 |
| Apex Integration | apex-rest-source-catalogs-safe | 16 |
| Apex UX | apex-ui-craft-safe | 17 |
| Zaimella Methodology | apex-zaimella-gestion-proyectos | 18 |
| Apex Page Automation | apex-page-automation-safe | 19 |
| Apex Database & Schema | apex-schema-automation-safe | 20 |
| Apex Testing | apex-automated-testing-safe | 21 |
| Apex Integration (Retired) | apex-api-client-safe | 22 |
| Apex Code Generation | apex-code-generation-safe | 24 |
| Apex Data Migration | apex-data-migration-safe | 25 |

`apex-api-client-safe` is a retired compatibility entry with no operational
REST deployment capability. Its invocation name remains for historical
context; do not use it for Oracle APEX deployment. Use the authenticated
App Builder or native export/import workflow documented in
`docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`.

---

## Development Workflow

### 1. Setup

```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Verify setup
python3 -m pytest tests/ -v
```

### 2. Pre-Commit Hooks

The `.pre-commit-config.yaml` defines 15 pre-commit hooks. The separate
`.hooks/pre-commit.sh` script captures the local audit trail when installed as
the Git pre-commit hook; it is not one of those 15 configured pre-commit hooks.

**File validation:** `detect-secrets` (v1.5.0), `detect-private-key`,
`check-yaml`, `check-json`, `check-added-large-files` (6000 KB limit),
`end-of-file-fixer`, `trailing-whitespace`, and `mixed-line-ending` (fix to LF).

**Code quality and security:** `black` (Python 3.13, 120 characters), `isort`
(Black profile, 120 characters), `flake8` (120 characters), and `bandit`
(`.bandit.yaml` configuration; tests excluded).

**Repository validation:** `ecosystem-audit`, `markdown-link-audit`, and
`validate-exception-handling` (Python files only).

### 3. Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage (pytest.ini configures scripts and skills)
pytest tests/ --cov-report=html

# Run specific test markers (integration tests may require Oracle)
pytest tests/ -m unit
pytest tests/ -m integration
pytest tests/ -m requires_oracle
pytest tests/ -m e2e
```

### 4. Code Quality Standards

- **Type hints** on all functions (PEP 484)
- **Docstrings** on all public functions
- **Black formatting** (120-char lines, consistent style)
- **No bare except** blocks (caught by pre-commit)
- **No hardcoded secrets** (caught by detect-secrets)
- **Security checks** via Bandit (no dangerous functions)

### 5. Audit Trail

When the repository's Git pre-commit capture hook is installed, it records
staged changes locally before each commit:
- Timestamp (ISO 8601)
- Author and email
- Branch name
- Files changed (count + list)
- Stored in: `control-proyecto/.bitacora.json`

**View audit trail:**
```bash
/apex-audit-decisions-log
```

The file is ignored by Git, so it remains local to this checkout and is not a
centralized team audit record. Use Git history as the versioned record; export
the local audit data explicitly when it needs to be shared.

---

## Configuration Files

### `.claude/settings.json`

Centralized configuration for:
- Audit system (enabled, auto-capture, smart-analysis)
- Pre-commit hook path and settings
- Skills organization (Apex prefix, no emojis, alphabetical)
- Documentation paths

### `.pre-commit-config.yaml`

Defines all git hooks:
- External hooks (detect-secrets, Black, isort, Bandit)
- Local hooks (exception validation, audit capture)
- Exclusion patterns (tests/, docs, etc.)

### `.bandit.yaml`

Security scanning configuration:
- 73 security checks enabled
- Exclude patterns for safe code sections
- Severity levels and confidence thresholds

### `.mcp.json.example`

Template for MCP (Model Context Protocol) configuration:
- Environment variables for MCP profiles
- Connection settings for TEST and production
- Credentials are read from the repository-root `.env`

---

## Key Utilities

### CLIParser (cli_utils.py)

Unified argument parsing for all scripts:

```python
from scripts.cli_utils import CLIParser

parser = CLIParser()
parser.add_argument('--output', default='output.json')
args = parser.parse_args()
```

### ApexMetadata (apex_metadata.py)

Extract and normalize YAML frontmatter from SKILL.md:

```python
from scripts.apex_metadata import ApexMetadata

meta = ApexMetadata('skills/apex-engineering-safe/SKILL.md')
print(meta.category)  # "Apex Engineering & Design"
print(meta.order)     # 4
print(meta.tags)      # ['inspection', 'design', 'export', 'read-only']
```

### path_setup.py

Centralized path handling:

```python
from scripts.path_setup import get_repo_root, get_script_dir

repo = get_repo_root()  # <ruta-a-la-raiz-del-repositorio>
scripts_dir = get_script_dir()  # <ruta-a-la-raiz-del-repositorio>/scripts
```

---

## Testing & Coverage

- **509 tests** (latest recorded complete suite: 100% pass rate)
- **Coverage floor:** 55% (latest combined result: 57.94%); long-term target: 80%
- **Test markers:** unit, integration, slow, requires_oracle, e2e (see `pytest.ini`)
- **Frameworks:** pytest (main), pytest-cov (coverage)

Run coverage report:
```bash
pytest tests/ --cov-report=html
open htmlcov/index.html
```

---

## Security

### Pre-Commit Security

1. **Secrets Detection** - Prevent credentials from being committed
2. **Exception Validation** - Enforce proper error handling (no bare `except:`)
3. **Bandit Linting** - 73 security checks for dangerous patterns
4. **Private Key Detection** - Scan for SSH keys, API tokens, passwords

### Credentials Management

**NEVER** hardcode credentials. Use the ignored repository-root `.env`:

```bash
python3 scripts/manage_apex_credentials.py set --environment test
# Writes credentials to the ignored local .env; do not commit or share it

python3 scripts/manage_apex_credentials.py probe --environment test
# Read-only session identity check against dual
```

---

## Documentation

- `docs/MANUAL-DE-USO.md` - User manual and getting started guide
- `docs/GUIA-CREAR-NUEVA-SKILL.md` - Normative procedure for creating skills
- `docs/TESTING.md` - Testing procedures and coverage information
- `skills/README.md` - Master catalog of all 31 skills
- `skills/SKILLS-QUICK-REFERENCE.md` - Decision matrix and quick lookup

---

## Next Steps

1. **Read skills/README.md** - Understand the 31 available skills
2. **Run `pytest tests/`** - Verify test suite passes
3. **Review audit trail** - Run `/apex-audit-decisions-log` to see project history
4. **Explore a skill** - Pick one skill and read its SKILL.md for detailed workflow
5. **Set up credentials** - Use `manage_apex_credentials.py` for secure MCP profiles

---

## Project Health

**Overall Score: 82/100**

| Category | Score | Status |
|----------|-------|--------|
| Skill Metadata | 100/100 | Perfect ✅ |
| Security | 95/100 | Excellent ✅ |
| Structure | 95/100 | Excellent ✅ |
| Git Practices | 90/100 | Excellent ✅ |
| Documentation | 90/100 | Excellent ✅ |
| Code Quality | 75/100 | Good ⚠️ |
| Testing | 80/100 | Good ⚠️ |
| Audit Trail | 85/100 | Configured ✅ |

---

## Questions?

- **Skills menu:** See `skills/README.md` and `skills/SKILLS-QUICK-REFERENCE.md`
- **Testing:** See `docs/TESTING.md`
- **Setup issues:** Check `docs/MANUAL-DE-USO.md`
- **Audit trail:** Run `/apex-audit-decisions-log` skill

---

**Last Updated:** 2026-08-21
**Version:** 1.0 (Phase 4+5 Complete)
**Status:** Production Ready (with noted code quality improvements)
