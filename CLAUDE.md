# apex.skills - Oracle APEX Development Framework

> Regla obligatoria: leer y cumplir [la política canónica de evolución](docs/POLITICA-EVOLUCION-ECOSISTEMA.md) antes de modificar este repositorio. Ningún archivo puede obligar técnicamente a un agente externo arbitrario; la aplicación efectiva combina política canónica, adaptadores, hooks, CI y revisión independiente.

## Overview

**apex.skills** is a canonical framework for Oracle APEX application development and deployment. It provides:

- **30 skills** (24 technical + 6 orchestrators) for design, engineering, QA, governance, lifecycle management, project methodology, and workflow coordination
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
│   └── [other reference docs]
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
│   ├── README.md              # Master navigation guide (30 skills: 24 technical + 6 orchestrators)
│   ├── SKILLS-QUICK-REFERENCE.md  # Quick lookup tables
│   ├── apex/                  # Maestro coordinator (routes requests)
│   ├── apex-application-generator-complete/  # Orchestrator for end-to-end APEX app generation
│   ├── apex-data-orchestrator-safe/  # Orchestrator for data workflows
│   ├── apex-design-review-orchestrator/  # Orchestrator for design review
│   ├── apex-qa-orchestrator-safe/  # Orchestrator for QA workflows
│   ├── apex-delivery-lifecycle-zaimella/  # Orchestrator for Zaimella + APEX delivery
│   ├── apex-audit-decisions-log/  # Audit trail viewer
│   ├── apex-database-diagnostics/
│   ├── apex-delivery-lifecycle-complete/
│   ├── apex-delivery-lifecycle-safe/
│   ├── apex-engineering-safe/
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
│   │   └── apex-exports/      # APEX export ZIP files (f109.zip, f130.zip)
│   ├── test_cli_utils.py
│   ├── test_apex_metadata.py
│   ├── test_path_setup.py
│   ├── test_apex_export_utilities.py
│   └── [23 test files total]
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

All 30 skills (24 technical + 6 orchestrators) are organized with:
- **"Apex" prefix** (no emojis) for clear branding
- **Alphabetical ordering** in menus
- **Unique order numbers** for display sequencing
- **Comprehensive tags** for filtering by workflow, access level, cost
- **3-level orchestration hierarchy:** 1 Maestro (apex) → 5 Coordinators → 24 Technical Skills

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

#### Technical Skills (24)
| Category | Skills | Order |
|----------|--------|-------|
| Apex Audit & Decisions | apex-audit-decisions-log | 0 |
| Apex Database & Diagnostics | apex-database-diagnostics | 1 |
| Apex Delivery & Lifecycle | apex-delivery-lifecycle-complete, apex-delivery-lifecycle-safe | 2, 3 |
| Apex Engineering & Design | apex-engineering-safe, apex-solution-design, apex-blueprint-design-safe, apex-page-automation-safe, apex-code-generation-safe | 4, 11, 15, 19, 24 |
| Apex Environment & Alignment | apex-environment-alignment-complete | 5 |
| Apex Export & QA | apex-export-qa-safe | 6 |
| Apex Page Range Governance | apex-page-range-governance | 7 |
| Apex Pattern Mining | apex-pattern-mining-safe | 8 |
| Apex Project Management | apex-project-bootstrap-final, apex-project-workspace | 9, 10 |
| Apex Documentation | apex-user-manual | 12 |
| Oracle Data Governance | oracle-data-change-governance-final | 13 |
| Apex Integration | apex-rest-source-catalogs-safe, apex-api-client-safe (retired) | 16, 22 |
| Apex UX Craft | apex-ui-craft-safe | 17 |
| Zaimella Methodology | apex-zaimella-gestion-proyectos | 18 |
| Apex Database & Schema | apex-schema-automation-safe | 20 |
| Apex Testing & QA | apex-automated-testing-safe | 21 |
| Apex Data Integration | apex-data-migration-safe | 25 |

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

Automatically run on every commit:

1. **detect-secrets** - Scan for private keys and credentials
2. **Black** - Format Python code (120-char line length)
3. **isort** - Sort imports consistently
4. **Bandit** - Security linting (73 checks)
5. **Flake8** - Code quality linting
6. **validate-exception-handling** - Reject bare `except:` blocks
7. **audit-trail-capture** - Record changes in `.bitacora.json` (zero-token)

### 3. Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Run specific test markers
pytest tests/ -m unit              # Unit tests only
pytest tests/ -m requires_oracle   # Tests needing Oracle connection
```

### 4. Code Quality Standards

- **Type hints** on all functions (PEP 484)
- **Docstrings** on all public functions
- **Black formatting** (120-char lines, consistent style)
- **No bare except** blocks (caught by pre-commit)
- **No hardcoded secrets** (caught by detect-secrets)
- **Security checks** via Bandit (no dangerous functions)

### 5. Audit Trail

Every commit automatically captures:
- Timestamp (ISO 8601)
- Author and email
- Branch name
- Files changed (count + list)
- Stored in: `control-proyecto/.bitacora.json`

**View audit trail:**
```bash
/apex-audit-decisions-log
```

This runs the new skill to visualize, filter, and export audit data.

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
- Credentials storage via system keyring

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

repo = get_repo_root()  # /home/user/apex.skills
scripts_dir = get_script_dir()  # /home/user/apex.skills/scripts
```

---

## Testing & Coverage

- **453 unit tests** (451 pass, 2 skipped by environment)
- **Target coverage:** 80% (current: ~59%)
- **Test markers:** unit, integration, slow, requires_oracle
- **Frameworks:** pytest (main), pytest-cov (coverage)

Run coverage report:
```bash
pytest tests/ --cov=scripts --cov-report=html
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

**NEVER** hardcode credentials. Use secure per-user profiles:

```bash
python3 scripts/manage_apex_credentials.py set --environment test
# Credentials stored in system keyring (not git, not files)

python3 scripts/manage_apex_credentials.py probe --environment test
# Read-only session identity check against dual
```

---

## Documentation

- `docs/MANUAL-DE-USO.md` - User manual and getting started guide
- `docs/GUIA-CREAR-NUEVA-SKILL.md` - Normative procedure for creating skills
- `docs/TESTING.md` - Testing procedures and coverage information
- `skills/README.md` - Master catalog of all 30 skills
- `skills/SKILLS-QUICK-REFERENCE.md` - Decision matrix and quick lookup

---

## Next Steps

1. **Read skills/README.md** - Understand the 30 available skills
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

**Last Updated:** 2026-09-18
**Version:** 1.1 (Audit + SQLcl execution channel)
**Status:** Production Ready
