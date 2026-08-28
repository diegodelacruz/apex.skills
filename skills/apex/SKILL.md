---
name: apex
category: "Apex Coordinator"
order: 14
tags: ['coordinator', 'routing', 'gateway']
description: "Coordinate all Oracle Database and Oracle APEX work through canonical specialist skills. Activate implicitly for requests to inspect, diagnose, develop, optimize, troubleshoot, compare, copy, release, migrate, or document an APEX application, page, region, item, workspace, export, or an Oracle object/query/code: table, view, package, function, procedure, trigger, sequence, index, constraint, schema, SQL, PL/SQL, ORA error, execution plan, or slow performance. Recognize Spanish and English forms, Oracle Application Express/App Express, and likely typos including orcle, oracel, orcale, oracl, oralce, apx, apxe, apexx, a-pex, and apek. Classify the request, select the smallest workflow, and enforce access validation, approvals, decisions, plans, SQL style validation, and audit."
---

# APEX Coordinator

Before modifying this repository, follow `docs/POLITICA-EVOLUCION-ECOSISTEMA.md`.

1. Infer the Oracle/APEX context from the user objective; never require the user to write `usa apex` or name a skill. For an isolated ambiguous typo with no database context, ask one concise clarification rather than routing incorrectly.
2. Interpret `<application>.<page>` after words such as page, pagina, página, application, or aplicación as two APEX identifiers, never as a decimal number. Confirm the interpretation only when surrounding context makes it ambiguous.
3. Classify the request using `references/routing.md`. State the selected workflow only when it helps the user understand a non-obvious decision.
4. For any requested environment, validate the requested profile in read-only mode first. If unavailable or unauthorized, report the limitation and stop that environment flow.
5. Delegate to the smallest set of specialist skills. Do not run duplicate workflows or require the user to invoke long skill names.
6. Preserve environment rules: TEST changes require scope/approval; production changes require separate explicit approval after explaining target, impact, and risk.
7. Apply page-range governance whenever application, project, and page range are supplied.
8. For every generated or changed Oracle SQL file, delegate to `oracle-data-change-governance-final` and run its `validate_sql_style.py`; a `STYLE_FAIL` blocks handoff. Before handoff, run the remaining applicable validation and mandatory ecosystem audit. Record decisions, plans, evidence, and limitations in the project workspace when the request creates or changes artifacts.
