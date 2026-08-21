# Configuration Guide

Complete guide to all configuration files in apex.skills.

## Quick Reference

| File | Purpose | Location |
|------|---------|----------|
| `.claude/settings.json` | Audit & skills config | `./.claude/settings.json` |
| `.pre-commit-config.yaml` | Git hooks setup | `./.pre-commit-config.yaml` |
| `.bandit.yaml` | Security checks | `./.bandit.yaml` |
| `.mcp.json.example` | MCP servers | `./.mcp.json.example` |
| `pyproject.toml` | Python project config | `./pyproject.toml` |
| `pytest.ini` | Testing config | `./pytest.ini` |
| `requirements.txt` | Dependencies | `./requirements.txt` |
| `.gitignore` | Git ignore rules | `./.gitignore` |
| `.env.example` | Environment template | `./.env.example` |

---

## .claude/settings.json

**Purpose:** Central configuration for audit system, hooks, and skills organization

**Location:** `./.claude/settings.json`

**Configuration:**

```json
{
  "audit": {
    "enabled": true,
    "auto_capture": true,
    "smart_analysis": true,
    "storage_location": "control-proyecto/.bitacora.json",
    "description": "Automatic decision and audit trail capture"
  },
  "hooks": {
    "pre_commit": {
      "enabled": true,
      "script": ".hooks/pre-commit.sh",
      "description": "Captures audit trail on each commit"
    }
  },
  "skills_organization": {
    "format": "apex_prefix",
    "use_emojis": false,
    "alphabetical": true,
    "description": "Skills organized with 'Apex' prefix, no emojis, alphabetical order"
  },
  "documentation": {
    "skills_readme": "skills/README.md",
    "skills_quick_reference": "skills/SKILLS-QUICK-REFERENCE.md",
    "audit_template": "control-proyecto/.bitacora.template.md"
  }
}
```

### Configuration Options

- **audit.enabled**: Enable/disable automatic audit trail capture
- **audit.auto_capture**: Automatically capture on commit (zero-token)
- **audit.smart_analysis**: Enable on-demand Claude analysis via skill
- **skills_organization.format**: "apex_prefix" (current standard)
- **skills_organization.use_emojis**: User preference (false = no emojis)

---

## .pre-commit-config.yaml

**Purpose:** Define all git pre-commit hooks that run automatically on commit

**Location:** `./.pre-commit-config.yaml`

### Hook Details

#### 1. detect-secrets (Yelp)
Prevents committing API keys, passwords, SSH keys

**What it detects:**
- AWS keys, API tokens
- Private SSH keys
- Database connection strings
- OAuth tokens

#### 2. Code Formatting & Quality Checks
- **trailing-whitespace**: Remove trailing spaces
- **end-of-file-fixer**: Ensure files end with newline
- **check-added-large-files**: Reject files >1000 KB
- **check-yaml**: Validate YAML syntax
- **check-json**: Validate JSON syntax

#### 3. Black (Code Formatter)
**Line length:** 120 characters (enforced)

**Why 120?**
- Modern widescreen monitors
- More readable than 80 chars
- Consistent with project standard

#### 4. isort (Import Sorting)
Organizes imports: stdlib → third-party → local

#### 5. Flake8 (Linting)
Checks for undefined variables, unused imports, indentation, style

#### 6. Bandit (Security Linting)
**73 security checks** including:
- SQL injection patterns
- Hardcoded passwords
- Insecure temp files
- Weak cryptography
- Command injection

#### 7. Exception Validation (Custom)
Rejects bare `except:` blocks. Requires specific exception handling:

```python
# ❌ REJECTED
try:
    do_something()
except:  # Bare except
    pass

# ✅ ACCEPTED
try:
    do_something()
except Exception as e:
    logger.error(f"Error: {e}")
```

#### 8. Audit Trail Capture (Custom)
Records every commit:
- Timestamp (ISO 8601)
- Author and email
- Branch name
- Files changed (count + names)

### How to Run Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for emergency (⚠️ rarely use)
git commit --no-verify
```

---

## .bandit.yaml

**Purpose:** Configure security checks (73 total)

**Location:** `./.bandit.yaml`

**Severity levels:**
- LOW: Minor issues
- MEDIUM: Notable security concerns
- HIGH: Critical vulnerabilities

**Common checks enabled:**
- B201: Flask debug mode
- B301-B302: Pickle/tempfile usage
- B303-B325: Cryptography patterns
- B401-B413: Dangerous imports
- B501-B506: Request validation
- B601-B607: Cryptography
- B701-B702: Assert usage

---

## .mcp.json.example

**Purpose:** Configure MCP (Model Context Protocol) servers

**Location:** `./.mcp.json.example`

**How to use:**
```bash
# Copy to actual config
cp .mcp.json.example .mcp.json

# Configure your environment with real values
```

**Important:** Never commit `.mcp.json` (contains credentials)

### MCP Servers Configured

1. **oracle-apex-skills**: Manages credentials and validation
2. **apex-project-utilities**: Audits skill ecosystem
3. **apex-export-processing**: Processes APEX exports

### Resource Servers

- **Docs**: `file://./docs` (Markdown documentation)
- **Examples**: `file://./tests/fixtures/apex-exports` (APEX export ZIPs)

---

## pyproject.toml

**Purpose:** Central Python project configuration

**Tools configured:**

### Black (Formatter)
```toml
line-length = 120
target-version = ['py38']
```

### isort (Import Sorting)
```toml
profile = "black"
line_length = 120
```

### pytest (Testing)
```toml
testpaths = ["tests"]
python_files = "test_*.py"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
    "requires_oracle: Requires Oracle connection"
]
```

### Coverage (Test Coverage)
```toml
branch = true
source = ["scripts"]
target = 80
```

---

## pytest.ini

**Purpose:** Pytest-specific configuration

**Markers:**
```ini
markers =
    unit: Unit tests (fast)
    integration: Integration tests
    slow: Slow tests (skip with -m "not slow")
    requires_oracle: Tests requiring Oracle
```

**Usage:**
```bash
pytest tests/ -m unit              # Only unit tests
pytest tests/ -m "not slow"        # Skip slow tests
pytest tests/ -m requires_oracle   # Only Oracle tests
```

---

## requirements.txt

**Purpose:** Python dependencies

**Current dependencies:**

```
# MCP integration
-e ./.upstreams/apex-mcp

# Credentials
keyring>=25.0.0

# Word documents
python-docx>=1.1.0
Pillow>=10.0.0

# Testing
pytest>=8.0.0
pytest-cov>=5.0.0

# Code quality
black>=23.12.1
isort>=5.13.2
flake8>=6.1.0
bandit>=1.7.5
pylint>=3.0.0
```

**Why each package:**
- keyring: Secure credential storage
- python-docx: Generate Word manuals
- Pillow: Embed screenshots in docs
- pytest: Testing framework
- pytest-cov: Coverage reporting
- black: Code formatting
- isort: Import sorting
- flake8: Linting
- bandit: Security scanning
- pylint: Code quality analysis

---

## .gitignore

**Purpose:** Tell git what NOT to commit

**Critical patterns:**

```
# Secrets (NEVER commit these)
.env              # Real environment
credentials.json  # Credential files
*.wallet          # Oracle wallet files

# Cache
__pycache__/
.pytest_cache/

# OS
.DS_Store
Thumbs.db

# Audit trail (auto-generated)
control-proyecto/.bitacora.json

# Screenshots (sensitive)
control-proyecto/**/screenshots/
control-proyecto/**/traces/

# Upstreams (large, managed separately)
.upstreams/
```

---

## .env.example

**Purpose:** Template for environment variables

**IMPORTANT:** No real values, just examples and instructions

```
# TEST Environment
APEX_TEST_HOST=apex-test.example.com
APEX_TEST_PORT=8080
APEX_TEST_USERNAME=ADMIN
APEX_TEST_PASSWORD=CHANGE_ME

# Production Environment (READ-ONLY)
APEX_PROD_HOST=apex.example.com
APEX_PROD_PORT=8080
APEX_PROD_USERNAME=READ_ONLY_USER
APEX_PROD_PASSWORD=CHANGE_ME

# Development
LOG_LEVEL=DEBUG
PYTHONPATH=.

# ⚠️ NEVER commit real credentials
# Use: python3 scripts/manage_apex_credentials.py set
# Credentials stored in system keyring (OS-specific)
```

---

## Validation

### Check all configurations are valid:

```bash
python3 scripts/validate-config.py
```

**Output on success:**
```
✅ .claude/settings.json is valid JSON
✅ .mcp.json.example is valid JSON
✅ All configuration files are valid!
```

---

## Troubleshooting

### Pre-commit hooks not running?
```bash
pre-commit install
pre-commit run --all-files
```

### Credentials leak detected?
```bash
# Remove the secret from file
# Use system keyring: 
python3 scripts/manage_apex_credentials.py set <profile>

# Update baseline:
detect-secrets scan --baseline .secrets.baseline
```

### Test coverage below 80%?
```bash
pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html  # View missing coverage
```
