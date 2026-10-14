---
name: apex-audit-decisions-log
category: "Apex Audit & Decisions"
order: 0
tags: ["audit", "documentation", "decisions", "governance", "read-only"]
description: "Review and export project decisions, controlled-operation events, and Git history."
---

# Apex Audit & Decisions Log

Read-only skill that visualizes and exports events available from controlled executors and the repository's Git history.

## Purpose

Controlled Oracle/APEX write execution through the repository's MCP and PowerShell adapters appends correlated start/result events, hashes, environment, operation and backup choice to `.bitacora.json`. MCP and PowerShell read-only queries append one hashed result event after execution and are not blocked by a write-ahead audit step; an audit append failure does not suppress the query result. Git separately records committed files and their author/timestamp. External tools and manual database changes are not captured by these adapters.

This skill lets you:
- View locally persisted events from supported controlled routes and Git history separately
- Export as Markdown or PDF
- Filter by date, environment, operation, or result when those fields are present
- Generate compliance/audit reports

## How It Works

**Automatic (zero tokens):**
- Git records all commits naturally
- The optional `.hooks/pre-commit.sh` appends staged-file metadata to the same JSON Lines file when invoked.
- `.bitacora.json` is ignored by Git and stays local unless a user explicitly changes that policy.
- No AI processing required

**On-demand (tokens only when you use it):**
```
/apex-audit-decisions-log
  ↓
Reads Git history + JSON Lines from .bitacora.json
AI analyzes context and relationships
Presents decisions in readable format
  ↓
Offers options:
  - View timeline
  - Export to Markdown
  - Export to PDF
  - Filter results
  - Report of available evidence and known capture gaps
```

## Configuration

The controlled adapters write the local log. `.claude/settings.json` does not
enable or disable that logging. The optional `.hooks/pre-commit.sh` is a manual
script and is not installed by `pre-commit install`.

## Usage Examples

**View audit trail:**
```
/apex-audit-decisions-log
Show me the decisions for this project
```

**Export report:**
```
/apex-audit-decisions-log
Generate a PDF audit report for compliance
```

**Filter by skill:**
```
/apex-audit-decisions-log
Show all changes made by apex-engineering-safe skill
```

**Compliance:**
```
/apex-audit-decisions-log
Create an audit trail for TEST→Production release
```

## Security & Compliance

✅ Read-only access only
✅ No modifications allowed
✅ Structured evidence for supported controlled routes
✅ Git commit history shown separately
⚠️ The local `.bitacora.json` can be edited or deleted; it is not tamper-proof
✅ Exportable for compliance
✅ Timestamp every event
