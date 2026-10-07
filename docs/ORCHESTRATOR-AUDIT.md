# Orchestrator roles and current verification

## Canonical role rule

Classify from the primary user-facing function in each `SKILL.md`: the entry
coordinator routes any Oracle/APEX request; workflow orchestrators coordinate
multiple skills for a defined lifecycle/application outcome; focused
orchestrators coordinate a bounded workflow; specialists perform one domain
function. The L0-L3 labels describe routing breadth, not authorization or
execution order.

## Current inventory

The source of truth is the 31 directories under `skills/*/SKILL.md`.

| Level | Role | Skills | Count |
|---|---|---|---:|
| L0 | Entry coordinator | `apex` | 1 |
| L1 | Broad lifecycle/application orchestrators | `apex-delivery-lifecycle-complete`, `apex-delivery-lifecycle-safe`, `apex-delivery-lifecycle-zaimella`, `apex-application-generator-complete` | 4 |
| L2 | Focused workflow orchestrators | `apex-data-orchestrator-safe`, `apex-qa-orchestrator-safe`, `apex-design-review-orchestrator` | 3 |
| L3 | Active domain specialists | Specialist directories excluding the retired API compatibility entry | 22 |

The 31-entry total also includes the retired `apex-api-client-safe` compatibility
entry. Role counts classify primary purpose; `status` separately records
operational state. `apex-delivery-lifecycle-zaimella`,
`apex-application-generator-complete`, and `apex-data-orchestrator-safe` are
development-status entries. The application generator is an end-to-end
development prototype; the data orchestrator is an outline. Their role labels
do not claim operational execution.

These roles classify function; they do not assert a dependency tree. A direct
edge is valid only when the caller and callee both describe that capability in
their current `SKILL.md` and the callee is operational.

## Compatibility and unresolved dependency findings

`apex-api-client-safe` has `status: retired` and explicitly says its simulated
REST deployment adapter is non-operational. Its directory and invocation name
remain in place. The historical body and changelog still describe its former
intent, but current dependent-skill integration sections and active cross-skill
maps no longer present it as a deploy, sync, or test-setup prerequisite. The
`.claude` command remains an invocation-compatible entry and opens the retired
notice. This static correction does not prove host-side discovery or runtime
compatibility.

- `skills/apex-application-generator-complete/SKILL.md` (prototype status and separate native import)
- `skills/apex-data-orchestrator-safe/SKILL.md` (ETL/import separation)
- `skills/apex-data-migration-safe/SKILL.md` (no API connectivity dependency)
- `skills/apex-code-generation-safe/SKILL.md` (generated specification is not deployment)
- `skills/apex-automated-testing-safe/SKILL.md` (configured target; no API setup/teardown)
- `docs/CROSS-SKILL-INTEGRATION.md` and `docs/SKILL-DEPENDENCY-MATRIX.md` (active edges corrected; graph-wide cycle proof pending)

The available documented replacement for APEX component deployment is native
APEX export/import or the configured App Builder/MCP route, including
`apex-page-automation-safe`; see
`docs/CAPACIDADES-CONTROLADAS-ORACLE-APEX.md`. Regression tests verify the
corrected direct edges and preserved compatibility name/command; end-to-end
orchestration remains uncertified because these prototype workflows are not
runtime executors.

Two skills currently declare `order: 3.5`:
`apex-delivery-lifecycle-zaimella` and `apex-external-context-learn`. An
in-repository search did not find an executable order consumer. External
skill-discovery/UI behavior is unverified, so changing either value would not
be a justified compatibility-preserving edit yet. No uniqueness claim is made.

## Audit status

This classification corrects the role counts and hierarchy descriptions in
navigation docs. Full dependency direction/cycle validation, order-consumer
compatibility, complete routing coverage, agent/adapter compatibility, and
functional regression remain pending. This document does not claim a complete
repository audit or `AUDIT_PASS`.
