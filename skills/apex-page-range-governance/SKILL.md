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
3. Validate TEST and production profiles in read-only mode. If a profile is unavailable, record the limitation; do not claim a two-environment conflict check passed.
4. In each authorized environment, inspect existing page numbers and page names in the requested inclusive range. Compare both results and active reservations in `registro-rangos-paginas.md`.
5. Treat an overlapping active reservation, a page with another project prefix, or different TEST/production occupancy as a conflict. Create `environment-diff.md`; do not reserve, create, or edit pages until the user resolves an actual conflict explicitly.
6. Reserve the range only after the conflict check. Update the application register and project `proyecto.md` with environment status, evidence, decision, and timestamp; never store secrets.
7. Set APEX **Page Name** as `<nombre-proyecto>-<nombre-pagina>`. Set APEX **Page Title** as only `<nombre-pagina>`. Verify both properties after page creation/import.
8. Any copy or deployment still follows environment approval rules: explicit approval for TEST changes and separate explicit approval for production changes.
