# Git Hooks

Pre-commit hooks that run automatically on every commit to ensure code quality, security, and audit trail capture.

## Available Hooks

### `pre-commit.sh`

**Purpose:** Capture audit trail of all changes

**When it runs:** Before each commit (automatic)

**What it does:**
- Records timestamp (ISO 8601)
- Captures author name and email
- Records branch name
- Tracks changed files (count + list)
- Stores in `control-proyecto/.bitacora.json`

**Output:**
```
✓ Audit logged: 3 files staged at 2026-08-21T22:30:45Z
```

**Configuration:**
- Path: `.hooks/pre-commit.sh`
- Configured in: `.pre-commit-config.yaml`
- Settings: `.claude/settings.json`

## Installation

The hook is automatically installed when you run:

```bash
pre-commit install
```

This is usually done as part of repository setup.

## Manual Verification

To manually run the hook:

```bash
bash .hooks/pre-commit.sh
```

## Audit Trail Output

The hook creates/updates `control-proyecto/.bitacora.json`:

```json
{
  "2026-08-21T22:30:45Z": [
    {
      "type": "git_staged_changes",
      "branch": "main",
      "author": "Diego de la Cruz",
      "email": "ddelacruz@example.com",
      "files_count": 3,
      "files_changed": ["CLAUDE.md", "requirements.txt", ".gitignore"],
      "status": "staged"
    }
  ]
}
```

## Viewing Audit Trail

Use the audit trail viewer skill:

```bash
/apex-audit-decisions-log
```

This provides visualization, filtering, and export capabilities.

## Troubleshooting

### Hook doesn't run

1. Verify it's executable:
   ```bash
   ls -l .hooks/pre-commit.sh
   chmod +x .hooks/pre-commit.sh
   ```

2. Verify pre-commit framework is installed:
   ```bash
   which pre-commit
   ```

3. Verify hooks are installed:
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

### Python errors in hook

The hook uses Python for JSON handling. Ensure Python 3 is available:

```bash
python3 --version
which python3
```

### Missing .bitacora.json

The hook creates this file automatically on first commit. If missing:

1. Verify `control-proyecto/` directory exists
2. Run hook manually: `bash .hooks/pre-commit.sh`
3. Check permissions: `ls -la control-proyecto/`

---

**Note:** This audit trail is automatically maintained. Do not edit `.bitacora.json` manually.
