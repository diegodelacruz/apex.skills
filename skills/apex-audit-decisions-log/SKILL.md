---
name: apex-audit-decisions-log
category: "Apex Audit & Decisions"
order: 0
tags: ["audit", "documentation", "decisions", "governance", "read-only"]
description: "View, analyze, and export the complete audit trail and decision log for this project. All changes are automatically captured by git. Use this skill to review decisions, generate audit reports, export to Markdown/PDF, or filter by date/skill/type."
---

# Apex Audit & Decisions Log

Read-only skill that visualizes and exports the automatic decision and audit trail captured by git and the audit hook.

## Purpose

Every change to your APEX project is automatically recorded:
- Git commits (messages, author, timestamp, files changed)
- Decisions made (extracted from commit context)
- Skills invoked (tracked via hook)
- Configuration changes

This skill lets you:
- View the complete audit trail
- Export as Markdown or PDF
- Filter by date, skill, or type
- Generate compliance/audit reports

## How It Works

**Automatic (zero tokens):**
- Git records all commits naturally
- Pre-commit hook captures changes to `.bitacora.json`
- No AI processing required

**On-demand (tokens only when you use it):**
```
/apex-audit-decisions-log
  ↓
Reads git history + .bitacora.json
AI analyzes context and relationships
Presents decisions in readable format
  ↓
Offers options:
  - View timeline
  - Export to Markdown
  - Export to PDF
  - Filter results
  - Compliance report
```

## Configuration

Enable/disable in `.claude/settings.json`:

```json
{
  "apex": {
    "audit": {
      "enabled": true,
      "auto_capture": true,
      "smart_analysis": true,
      "storage": "control-proyecto/.bitacora.json"
    }
  }
}
```

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
✅ Complete audit trail
✅ Tamper-proof (git-backed)
✅ Exportable for compliance
✅ Timestamp every event
