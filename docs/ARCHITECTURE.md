# APEX Skills Framework - Architecture

## System Overview

apex.skills is a canonical framework for Oracle APEX development with 18 specialized skills,
security-hardened pre-commit hooks, and an automatic audit trail system.

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    COORDINATOR SKILL                     │
│            (Routes requests to specialists)              │
└────────────┬────────────────────────────────────────────┘
             │
     ┌───────┴──────────┬─────────────┬──────────────┐
     │                  │             │              │
┌────▼─────┐  ┌────────▼──┐  ┌──────▼──┐  ┌───────▼──┐
│ Design   │  │ Engineering│ │QA/Export│  │Governance│
│ Skills   │  │ Skills     │ │ Skills  │  │ Skills   │
│          │  │            │ │         │  │          │
│ · Solution│ · Engineering│ · Export QA │ · Page Range
│ · Pattern │ · Database   │ · Pattern  │ · DATA Change
└──────────┘ │ Diagnostics │ └─────────┘ │ · Environment
             └────────────┘              └────────────
                    │
     ┌──────────────┴──────────────┐
     │                             │
┌────▼──────────────┐   ┌─────────▼────────┐
│ UTILITIES LAYER   │   │  HOOKS LAYER     │
│ ───────────────   │   │ ─────────────    │
│ • CLIParser       │   │ • detect-secrets │
│ • ApexMetadata    │   │ • Bandit         │
│ • path_setup      │   │ • Black/isort    │
│ • manage_credentials│  │ • Audit capture  │
└───────────────────┘   └──────────────────┘
         │                       │
    ┌────▴───────────────────────▴────┐
    │      GIT HOOKS (Pre-commit)      │
    │ Auto-captures changes to JSON    │
    │ Zero tokens, automatic           │
    └─────────────────────────────────┘
```

## Layers

### 1. Skills Layer (Highest Level)
- **18 specialized Oracle APEX skills**
- Each skill = SKILL.md file with frontmatter (name, category, order, tags, description)
- Examples:
  - `apex-engineering-safe` → Inspect and design APEX apps
  - `apex-delivery-lifecycle-safe` → End-to-end workflow
  - `apex-audit-decisions-log` → View audit trail
  - `oracle-data-change-governance-final` → Govern DATA changes

### 2. Coordinator Skill
- Entry point: `skills/apex/SKILL.md`
- Routes requests to specialized skills
- Understands context and intent

### 3. Utilities Layer
These are reusable Python modules imported by skills:

**CLIParser** (`scripts/cli_utils.py`)
- Unified argument parsing
- Consistent CLI interface
- DRY principle (no duplication)

**ApexMetadata** (`scripts/apex_metadata.py`)
- Extract YAML frontmatter from SKILL.md
- Validate metadata structure
- Used by skill discovery and menu organization

**path_setup** (`scripts/path_setup.py`)
- Centralized path handling
- Works from any working directory
- Finds repo root via .git detection

**manage_apex_credentials** (`scripts/manage_apex_credentials.py`)
- Secure per-user credential profiles
- Stored in system keyring (not git, not files)
- Never expose credentials

### 4. Hooks Layer
**Pre-commit Hooks** (run automatically on every `git commit`)

```
Secrets Detection (detect-secrets)
  └─ Prevents committing API keys, passwords, etc.

Code Formatting (Black)
  └─ Enforces consistent style (120-char lines, tabs)

Import Sorting (isort)
  └─ Organizes imports alphabetically and by type

Security Linting (Bandit)
  └─ 73 checks for dangerous Python patterns

Exception Validation (custom)
  └─ Rejects bare except: blocks (must handle exceptions)

Audit Trail Capture (.hooks/pre-commit.sh)
  └─ Records timestamp, author, files changed to JSON
```

### 5. Storage Layer

**control-proyecto/**
- Project-level decisions and master plans
- `.bitacora.json` - Auto-generated audit trail (NOT committed)
- `.bitacora.template.md` - Audit report template

**tests/fixtures/apex-exports/**
- Test data: f109.zip, f130.zip (actual APEX exports)
- Used for integration testing

## Data Flow Example

```
User Input
    │
    ▼
Coordinator Skill (/apex)
    │
    ├─ Analyzes request
    │
    ├─ Determines needed skill
    │  (e.g., "inspect this export" → apex-engineering-safe)
    │
    ▼
Specialized Skill
    │
    ├─ Imports from Utilities Layer
    │  (CLIParser, ApexMetadata, path_setup)
    │
    ├─ Uses system keyring for credentials
    │  (via manage_apex_credentials)
    │
    ├─ Processes input
    │
    ▼
Output (Document/Report)
    │
    ├─ Written to control-proyecto/
    │
    ▼
Git Commit
    │
    ├─ Pre-commit hooks run:
    │  • Formatting check (Black)
    │  • Import sorting (isort)
    │  • Security check (Bandit)
    │  • Secrets scan (detect-secrets)
    │  • Audit capture (.hooks/pre-commit.sh)
    │
    ▼
Commit Created
    │
    └─ .bitacora.json updated with:
       • Timestamp
       • Author
       • Files changed
       • Branch name
```

## Extensibility: Adding a New Skill

The complete normative procedure is in
[`docs/GUIA-CREAR-NUEVA-SKILL.md`](GUIA-CREAR-NUEVA-SKILL.md). In summary,
first justify the separation from existing skills, then create the portable
`SKILL.md`, integrate routing and every affected catalog, and run the complete
ecosystem audit before independent review. A minimal directory is:

```text
skills/<nombre-de-skill>/
└── SKILL.md
```

Do not publish a skill that is orphaned, duplicated, missing from a catalog, or
not covered by reproducible validation and rollback evidence.

## Security Boundaries

### What We Protect
- Credentials: TEST and Production connection strings (stored in system keyring)
- Export files: APEX application schemas and configurations
- Decision logs: Project decisions and audit trail
- Screenshots: User interface screenshots (excluded from git)

### How We Protect It
1. **Pre-commit Secrets Detection**
   - Scans every commit for patterns matching credentials
   - Blocks commit if secrets detected
   - Maintains `.secrets.baseline` for known secrets

2. **System Keyring Storage**
   - Credentials never in git
   - Never in environment variables
   - Never in .env files
   - Stored securely in OS credential manager

3. **Pre-commit Hooks Enforcement**
   - All developers must use hooks
   - Exceptions are logged in audit trail
   - Audit trail is tamper-proof (git-backed)

4. **Access Control**
   - TEST environment: read-write for developers
   - Production: read-only validation, then explicit approval required
   - Screenshots and traces: excluded from version control

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Skills | Claude + Python | Oracle APEX expertise + orchestration |
| Utils | Python 3.8+ | Reusable components |
| Hooks | Bash + Python | Git integration, audit trail |
| Credentials | system-keyring | Secure storage |
| Testing | pytest + fixtures | 122 tests, 100% pass rate |
| Documentation | Markdown | GitHub-friendly docs |
| Version Control | Git + GitHub | History and collaboration |

## Deployment Architecture

```
Developer Machine
    │
    ├─ Clone apex.skills repo
    ├─ Run: pip install -r requirements.txt
    ├─ Run: pre-commit install
    │
    ▼
Local Development
    │
    ├─ Edit skills/
    ├─ Run: pytest tests/ -v
    ├─ Git commit (hooks run automatically)
    │
    ▼
GitHub
    │
    ├─ Push to feature branch
    ├─ Create PR
    ├─ GitHub Actions runs CI (future)
    ├─ Review and merge
    │
    ▼
Production Ready
    │
    ├─ main branch updated
    ├─ Users pull latest
    ├─ Audit trail recorded
```

## Performance Characteristics

- **Audit Trail Capture**: <100ms per commit (pure bash/JSON)
- **Pre-commit Hooks**: ~2-5 seconds total (Black, isort, Bandit)
- **Test Suite**: ~200ms (122 tests)
- **Skill Execution**: Depends on task (typically 30s-5min)

## Future Enhancements

1. GitHub Actions CI/CD pipeline (automated testing)
2. Type hints completion (100% coverage)
3. Integration tests for workflows
4. API documentation and SDK
5. Skill marketplace/registry
6. Analytics dashboard for audit trail
