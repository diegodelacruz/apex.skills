---
name: apex-user-manual
description: Generate a validated Word user manual for a completed Oracle APEX project or change. Use after approved QA evidence exists to capture the real APEX workflow with Playwright or Browser, build a DOCX from reviewed content, audit embedded images, render the document to PNG for visual QA, and deliver the final manual under control-proyecto/manuales.
---

# APEX User Manual

## Preconditions

- Require an approved coverage inventory: one row per screen, dialog, action, tab, accordion, or flow step documented.
- Require TEST access and safe authentication handling. Never record credentials, tokens, storage state, or sensitive data in the manual/evidence repository.
- Require QA evidence for the same candidate/version. Do not document guessed routes or screenshots from historical builds.

## Workflow

1. Use Browser when available; otherwise use the reusable Playwright runner from `.upstreams/zaimella-skill/skill/qa-apex/scripts/ensure-playwright-env.ps1`. It installs the official `@playwright/test` package and browser runtime. Do not vendor the full Microsoft Playwright source repository.
2. Capture desktop-viewport screenshots through the real authorized navigation path. Wait for report data and spinners to finish. Save image, trace, and coverage evidence in `control-proyecto/qa/<id-cambio>/`.
3. Create editable manual source in `control-proyecto/manuales/fuentes/`. Use the upstream `documentacion-proyecto-sistemas` manual builder where available; otherwise create a DOCX with the active `documents` skill.
4. Generate `control-proyecto/manuales/manual_usuario_<version>.docx`.
5. Audit images with upstream `audit_docx_images.py`, then render the DOCX to PNG with the active `documents` skill and inspect every page. Fix and re-render until clean.
6. Record generated manual, source, evidence version, audit result, render result, and final status in the project plan.

## Boundaries

Playwright automates browser navigation and captures evidence; it does not author the Word file. Word generation and visual DOCX verification are separate mandatory stages.
