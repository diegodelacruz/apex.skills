---
name: apex-export-qa-safe
category: "Apex Export & QA"
order: 6
tags: ['qa', 'validation', 'export', 'read-only']
description: "Static QA validation for APEX export ZIP files. Check structure, integrity, and readiness before changes."
---

# Safe Oracle APEX Export QA

- Run `scripts/validate_export.py <zip>` and report its SHA-256 evidence.
- A `STATIC_PASS` covers only export structure and declared settings. Require runtime/browser evidence for authentication, authorization, navigation, integrations, and business results.
- Do not import, deploy, execute DDL/DML, create users, or invoke mutating MCP tools as QA.
- Return `STATIC_PASS`, `STATIC_FAIL`, or `RUNTIME_EVIDENCE_REQUIRED`, with application identity, page counts, and limitations.

- Check blueprint metadata, REST catalog provenance, Universal Theme usage, accessibility, and responsive declarations when present.
- QA evidence never authorizes CSS/JavaScript, REST configuration, import, deployment, or production changes.
