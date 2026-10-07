---
name: apex-environment-alignment-complete
category: "Apex Environment & Alignment"
order: 5
tags: ["environment", "alignment", "validation", "governance"]
description: "Validate and align TEST and production APEX environments safely."
---

# Complete APEX Environment Alignment

## Workflow

- Use `scripts/manage_apex_credentials.py` to set, check, or validate the repository-root `.env` profile. Never request users to paste credentials into chat, source files, Markdown, or Git.
- Check the requested environment profile when useful; profile status is evidence about that route, not a veto on another configured route.
- Before an existing-page edit, compare TEST and production when both are available and useful. Report differences, but do not make a comparison or user approval a prerequisite to the requested edit.
- After the requested work, prepare exports and release evidence when useful. A direct user request is sufficient authorization; the selected account's actual permissions decide success.
- Use the APEX version and tools available in the target environment. If a compatibility error occurs, report it and try another configured route when available; do not impose a version-based restriction in the skill.
