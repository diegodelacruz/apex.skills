---
name: apex-qa-orchestrator-safe
category: "Apex QA"
order: 6.5
tags: ["qa", "validation", "orchestration"]
description: "Coordinate APEX QA evidence and report results without approval gates."
---

# APEX QA Orchestrator

Coordinate the existing export, automated-testing, and environment-alignment skills for the QA
scope requested. QA findings inform the user and help locate defects; they do not create an
approval gate for an operation the user directly requested. Keep testing distinct from design,
implementation, and release authorization.

## Workflow

### Phase 1: Static export review

Delegate to `apex-export-qa-safe` to inspect ZIP integrity and required files,
component references, page and region consistency, static SQL/PLSQL issues, and
export identity. Record findings with severity and distinguish static checks
from checks requiring a live environment. Continue to the next requested QA
activity while reporting unresolved findings; findings inform the user but do
not impose an unrequested gate.

### Phase 2: Automated and regression testing

Delegate to `apex-automated-testing-safe` for the requested UI, API, regression,
or performance checks. Reuse available baselines and test data; capture which
checks actually ran, results, failures, and timings. Do not claim coverage or
performance results without observed evidence.

### Phase 3: Environment comparison

Delegate to `apex-environment-alignment-complete` to compare the requested TEST
and production metadata, database objects, connectivity, and credential
contexts. Use the configured credentials and verify the actual targets. Report
missing access or incompatible tools as technical findings; do not silently
switch environments or stop unrelated requested checks.

Aggregate the evidence from all applicable phases into one QA report. A phase
may be marked unavailable or not requested; that status is reported rather
than converted into an approval requirement.

1. Identify the target app/pages, selected environment, available export/version, and requested
   validation scope. Reuse the coordinator's current read-only evidence for connected account and
   environment; obtain it at the start if missing, and refresh it only when the target changes.
   Effective grants belong to the configured credential.
2. Treat acceptance criteria and test plans from design/blueprint as inputs. QA executes and
   reports those checks; it does not repeat solution design or rewrite the blueprint.
3. For an export review, coordinate `apex-export-qa-safe` to check archive structure, required
   files, component consistency, declared settings, static SQL/PLSQL concerns, and export identity.
   Separate static findings from checks that need a live runtime.
4. For functional or regression coverage, coordinate `apex-automated-testing-safe` to select
   relevant UI, API, regression, or performance checks. Reuse existing baselines and test data
   setup where available; do not claim a test ran unless its result was observed.
5. For environment comparison, coordinate `apex-environment-alignment-complete` to compare
   relevant app metadata, database objects, connectivity, and credential contexts. Use the
   configured credential for each requested environment; do not infer identity from MCP labels.
6. When runtime evidence is required, use the configured read/inspection route for the target.
   Keep QA activities read-only unless the user also requested test-data changes or implementation;
   then perform those requested operations through the appropriate specialist.
7. Report each check as passed, failed, unavailable, or not requested, with evidence and impact.
   A finding does not silently expand or cancel the user's requested implementation scope.

## Output

Summarize requested scope; export, runtime, regression, and environment checks performed; findings
and impact; known limitations; the observed operation result; and recommended next checks.
Distinguish a failed check from a database/APEX permission denial. Do not claim that an unrun
check passed. Do not duplicate design decisions, generate implementation artifacts, or require a
separate release approval unless that work was directly requested.
