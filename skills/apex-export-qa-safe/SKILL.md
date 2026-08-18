---
name: apex-export-qa-safe
description: Perform static, read-only QA for Oracle APEX 24.1.3 split-export ZIP files before an MCP-driven change. Validates basic source structure and declared security settings without deployment, database writes, or application imports.
---

# Safe Oracle APEX Export QA

- Run `scripts/validate_export.py <zip>` and report its SHA-256 evidence.
- A `STATIC_PASS` covers only export structure and declared settings. Require runtime/browser evidence for authentication, authorization, navigation, integrations, and business results.
- Do not import, deploy, execute DDL/DML, create users, or invoke mutating MCP tools as QA.
- Return `STATIC_PASS`, `STATIC_FAIL`, or `RUNTIME_EVIDENCE_REQUIRED`, with application identity, page counts, and limitations.
