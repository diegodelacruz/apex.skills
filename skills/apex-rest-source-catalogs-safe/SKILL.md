---
name: apex-rest-source-catalogs-safe
category: "Apex Integration"
order: 16
tags: ["rest", "fusion", "integration", "catalog", "read-only"]
description: "Assess Fusion REST catalogs for safe APEX integration design."
---

# Safe APEX REST Source Catalog Assessment

Use this workflow to assess Fusion Apps REST Source Catalogs from Oracle's official APEX upstream.
It can assess or implement the integration requested by the user, including catalog import,
production endpoints, and APEX REST Data Sources, through the available authenticated route.

## Required inputs

Require the target APEX environment and version, Fusion service scope, intended business actions,
data classification, authentication model, network route, rate limits, error-handling expectations,
and the exact upstream branch/commit. The official `rest-source-catalogs` branch is independent of
the versioned application branches.

## Workflow

1. Inventory endpoints, operations, request/response shapes, pagination, filtering, and declared
   authentication requirements from the selected catalog.
2. Classify operations and report their behavior; follow the user's requested operation and scope.
3. Design an APEX-facing contract: page/process owner, authorization boundary, input validation,
   least-privilege scope, timeout/retry behavior, observability, and user-safe error messages.
4. Verify that credentials remain in the approved secret store and are never embedded in exports,
   catalog files, prompts, logs, or sample applications.
5. Produce a test matrix using a non-production endpoint or mock. Include authentication failure,
   authorization denial, malformed response, throttling, timeout, pagination, and data masking.
6. Perform requested catalog import or endpoint configuration and report the service result.

## Output

Deliver: catalog provenance; endpoint inventory; data classification; operation risk matrix;
authentication and authorization design; mapping contract; test plan; monitoring needs; rollback or
disable procedure; and validation evidence.
