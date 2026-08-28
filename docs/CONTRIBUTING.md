# Contributing to APEX Skills

Thank you for your interest in contributing to apex.skills!

This guide explains how to contribute code, documentation, and improvements.

Before making any change, read [the canonical ecosystem evolution policy](POLITICA-EVOLUCION-ECOSISTEMA.md). It applies to every agent and session. No file can technically force an arbitrary external agent; compliance is reinforced through the canonical policy, agent adapters, hooks, CI, and independent review.

## Before You Start

### Prerequisites

1. **Read the documentation:**
   - `CLAUDE.md` - Repository structure and overview
   - `docs/ARCHITECTURE.md` - System design and components
   - `docs/CONFIGURATION-GUIDE.md` - How everything is configured

2. **Install dependencies:**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

4. **Run tests to verify setup:**
   ```bash
   pytest tests/ -v
   # Should show: 119 passed
   ```

## Development Workflow

### Step 1: Create a Feature Branch

```bash
git checkout -b feature/description-of-change
git checkout -b fix/bug-description
git checkout -b docs/documentation-improvement
```

**Branch naming conventions:**
- `feature/` - New skill or feature
- `fix/` - Bug fix
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Test improvements

### Step 2: Make Your Changes

Follow the code standards (see below).

### Step 3: Run Pre-commit Hooks

Before committing, validate your changes:

```bash
pre-commit run --all-files
```

**Expected output:**
```
detect-secrets............................PASSED
Black....................................PASSED
isort....................................PASSED
flake8...................................PASSED
Bandit...................................PASSED
validate-exception-handling..............PASSED
audit-trail-capture.......................PASSED
```

### Step 4: Run Tests

```bash
pytest tests/ -v
# Expected: 119 passed
```

### Step 5: Commit Your Changes

```bash
git commit -m "type(scope): description"
```

**Commit message format:**
```
<type>(<scope>): <subject>

<body>

Closes #issue_number
```

**Types:**
- `feat` - New feature or skill
- `fix` - Bug fix
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `test` - Test additions
- `chore` - Maintenance

**Examples:**
```
feat(skills): Add apex-new-feature skill

Create new skill for handling custom workflow.
Includes SKILL.md documentation and references.

Closes #123
```

### Step 6: Push to Remote

```bash
git push origin feature/description-of-change
```

### Step 7: Create Pull Request

Go to GitHub and create a PR.

**PR checklist:**
- [ ] Title is descriptive
- [ ] Description explains changes
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] 119/119 tests pass

## Code Standards

### Python Files

#### Type Hints

Add type hints to all functions:

```python
def get_repo_root() -> str:
	"""Get repository root path."""
	...

def validate_config(config: dict[str, any]) -> bool:
	"""Validate configuration dictionary."""
	...
```

#### Docstrings

Use Google-style docstrings:

```python
def calculate_hash(filepath: str) -> str:
	"""Calculate SHA-256 hash of a file.

	Args:
		filepath: Path to file to hash

	Returns:
		Hex-encoded SHA-256 hash string

	Raises:
		FileNotFoundError: If file does not exist
		IOError: If file cannot be read

	Example:
		>>> hash_val = calculate_hash('/path/to/file.zip')
		>>> assert len(hash_val) == 64
	"""
	...
```

#### Formatting

- **Line length:** 120 characters (enforced by Black)
- **Quotes:** Double quotes (enforced by Black)
- **Indentation:** Tabs (not spaces)
- **Imports:** Alphabetical, grouped (enforced by isort)

#### Exception Handling

```python
# ❌ REJECTED - Bare except
try:
	do_something()
except:
	print("Error occurred")

# ✅ ACCEPTED - Specific exceptions
try:
	do_something()
except FileNotFoundError as e:
	logger.error(f"File not found: {e}")
except ValueError as e:
	logger.error(f"Invalid value: {e}")
```

### Skill Files

#### SKILL.md Format

```markdown
---
name: apex-skill-name
category: "Apex Category"
order: 5
tags: ['tag1', 'tag2']
description: "One-line description"
---

# Skill Title

## Purpose

Clear explanation of what this skill does.

## Workflow

Step-by-step instructions:
1. First step with example
2. Second step with example
3. Third step with verification
```

#### Frontmatter Requirements

Portable minimum: all skills must have name and description. This repository additionally uses:
- `name`: Unique skill identifier (lowercase, kebab-case)
- `category`: "Apex [Category]" format
- `order`: Unique number (0-14)
- `tags`: Array of 3-5 tags
- `description`: One-line description (50-100 chars)

## Testing

### Run All Tests

```bash
pytest tests/ -v
# Output: 119 passed
```

### Run Specific Markers

```bash
pytest tests/ -m unit           # Only unit tests
pytest tests/ -m "not slow"     # Skip slow tests
```

### Generate Coverage Report

```bash
pytest tests/ --cov=scripts --cov-report=html
open htmlcov/index.html
```

## Documentation

### Update CLAUDE.md

If adding features, update `CLAUDE.md`:
- Add new components to Architecture
- Document new configuration options
- Update Project Health if applicable

### Update Skill Catalog

If adding/modifying skills:
- Update `skills/README.md`
- Update `skills/SKILLS-QUICK-REFERENCE.md`
- Verify alphabetical ordering

### Add Changelog Entry

Update `CHANGELOG.md` with your changes:

```markdown
## [Unreleased]

### Added
- New feature description

### Fixed
- Bug fix description
```

## Common Issues

### Pre-commit hook failure

```bash
# Fix formatting issues
black scripts/

# Re-run hook
pre-commit run --all-files

# Commit again
git commit -m "fix: Apply Black formatting"
```

### Test failures

1. Read the failure message carefully
2. Debug the test
3. Fix the code or test
4. Re-run: `pytest tests/ -v`

### Merge conflicts

```bash
git fetch origin
git merge origin/main
# Fix conflicts in affected files
git commit -m "merge: Resolve conflicts with main"
git push origin feature/branch-name
```

## Questions?

- Read `CLAUDE.md` for repository overview
- Read `docs/ARCHITECTURE.md` for system design
- Check recent commits for examples
- Ask in PR discussion

Thank you for contributing! 🎉
