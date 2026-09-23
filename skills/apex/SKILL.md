---
name: apex
category: "Apex Coordinator"
order: 14
tags: ["coordinator", "routing", "governance"]
description: "Route Oracle and APEX requests to the smallest safe specialist workflow."
---

# APEX Coordinator

Before modifying this repository, follow `../../docs/POLITICA-EVOLUCION-ECOSISTEMA.md`.

## Fluency Policy

The conversation must be fluid. Act on the user's intent immediately — do not
ask for permission to perform routine operations.

**Read operations** (inspect, review, query, report, describe, compare):
- Connect to the database and query without asking. The user's request IS the
  authorization. Never ask "should I connect?", "do you want me to query?", or
  "can I check the metadata?".
- Infer the application, page, environment, and schema from context. Only ask
  when genuinely ambiguous (two plausible interpretations).

**Write operations** (create, modify, drop, deploy, import):
- In TEST: apply the Modification Mode Policy below. The step-by-step
  confirmation flow IS the approval — no separate "approval step" is needed.
- In Production: confirm the environment switch once ("this targets production,
  proceeding"), then apply the same modification flow. Do not ask for a
  "separate documented approval".

**Verification channel: database, never browser.**
- All inspection and verification of APEX objects must be done via database
  metadata queries (`apex_application_pages`, `apex_application_page_regions`,
  `apex_application_page_items`, `apex_application_page_buttons`,
  `apex_application_page_da`, `apex_application_page_proc`, etc.) — never by
  opening a browser to App Builder.
- The browser is only for the user. Claude inspects, verifies, and navigates
  APEX exclusively through SQL queries against APEX dictionary views and
  Oracle data dictionary views (`ALL_OBJECTS`, `ALL_TAB_COLUMNS`, etc.).

**General rules:**
- Never interview the user with a checklist of required inputs. Infer what you
  can from context and the database; ask only for what is truly missing.
- Never ask which mode/skill/workflow to use. Route silently.
- Never ask "do you want me to...?" for something the user just asked you to do.
- If credentials or connection are configured, use them. If they fail, report
  the error — do not ask beforehand whether connecting is allowed.

## Environment Policy

**Default environment: TEST.** All connections, deployments, and executions target the
test/testing environment unless the user explicitly requests production. This rule applies
to every skill, script, and orchestrator in the ecosystem.

- During bootstrap (`Initialize-ApexCodexProject.ps1`): validate every environment that
  has configured credentials. Report missing environments but do not block.
- During execution: if the user does not specify an environment, use `--environment test`.
- If the user explicitly requests production, respect the decision immediately.
- Never silently switch from test to production. Never default to production.
- Scripts that accept `-Environment` or `--environment` must default to `testing`/`test`.

## Modification Mode Policy

When the user wants to make changes, **ask which mode they prefer before the
first modification in the session**. Do not ask again after that.

### Step-by-step mode (paso a paso) — default

Each modification is delivered one step at a time:

1. **Instruct**: explain WHAT to change, WHERE to find it, and HOW to do it.
   Be specific: name the exact APEX property, navigation path, SQL statement, or
   field value. The user should not need to guess or search.
2. **Wait**: do NOT proceed until the user explicitly confirms the step is done.
   Phrases like "listo", "hecho", "done", "ok", "siguiente" count as confirmation.
   Silence or a new question is NOT confirmation.
3. **Handle errors**: if the user reports a problem, ask for a screenshot or the
   error text. Analyze what was provided, propose a fix, and repeat from step 1
   for that same step. Do not skip ahead.
4. **Verify**: after the user confirms, query APEX metadata or the database to
   confirm the change took effect. Report the verification result before moving
   to the next step. If verification fails, explain what was expected vs. what
   was found, and guide the user to correct it.
5. **Advance**: only after verification passes, present the next step.

### All-at-once mode (todos los pasos)

Deliver all steps in a single numbered list with enough detail to execute each
one independently. After the user executes them all and confirms, run a single
verification pass that checks every change and report the results.

### Rules for both modes

- The user can switch modes at any time ("dame todos los pasos", "mejor paso a paso").
- Every modification must be **verified** by querying the actual object after the
  user confirms execution. A confirmation without verification is incomplete.

## Workflow

1. Infer the Oracle/APEX context from the user objective; never require the user to write `usa apex` or name a skill. For an isolated ambiguous typo with no database context, ask one concise clarification rather than routing incorrectly.
2. Interpret `<application>.<page>` after words such as page, pagina, página, application, or aplicación as two APEX identifiers, never as a decimal number. Confirm the interpretation only when surrounding context makes it ambiguous.
3. Classify the request using `references/routing.md`. State the selected workflow only when it helps the user understand a non-obvious decision.
4. Connect to the requested environment. If unavailable, report the limitation.
5. Delegate to the smallest set of specialist skills. Do not run duplicate workflows or require the user to invoke long skill names.
6. Apply page-range governance whenever application, project, and page range are supplied.
7. For every generated or changed Oracle SQL file, delegate to `oracle-data-change-governance-final` and run its `validate_sql_style.py`; a `STYLE_FAIL` blocks handoff. SQL/PLSQL and APEX artifacts use lower-case non-literal code and physical tabs of visual width four, never leading spaces. Preserve literals, comments, and quoted identifiers. Python source is the sole exception: Black uses four spaces. Record decisions, plans, evidence, and limitations in the project workspace when the request creates or changes artifacts.
