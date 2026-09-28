---
name: apex-page-range-governance
category: "Apex Page Range Governance"
order: 7
tags: ["governance", "pages", "validation"]
description: "Reserve and validate conflict-free APEX page ranges by project."
---

# APEX Page Range Governance

## Workflow

1. Require application number, project name, and inclusive page range (`desde` / `hasta`). Ask only for any missing value; require `desde <= hasta`.
2. Keep existing `control-proyecto/` unchanged. In addition, create the layout in `references/layout-and-register.md` inside the application folder.
3. Inspect profiles and page ranges in the requested environment using any available route. Record unavailable comparisons accurately.
4. Inspect existing page numbers and names in the requested inclusive range. Compare environments and active reservations when the information is available.
5. Report overlapping reservations, different occupancy, or naming differences. These findings do not veto a directly requested operation; follow the user's target and let APEX determine permission and outcome.
6. Reserve the requested range and update the application register and project `proyecto.md` with environment status, evidence, decision, and timestamp; never store secrets.
7. Set APEX **Page Name** as `<nombre-proyecto>-<nombre-pagina>`. Set APEX **Page Title** as only `<nombre-pagina>`. Verify both properties after page creation/import.
8. Perform a requested copy or deployment in the named environment without a separate skill approval step.
