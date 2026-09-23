#!/usr/bin/env python3
"""Audit controlled local Markdown links and required canonical resources.

Pre-commit hook that verifies all required governance files exist and all
local Markdown links resolve to existing targets.

Status: ACTIVE (pre-commit hook)
Tests: Covered indirectly by test_quality_audit.py (Q03 link checks)
Dependencies: none (stdlib only)
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = (
    "AGENTS.md",
    "docs/POLITICA-EVOLUCION-ECOSISTEMA.md",
    "skills/apex-project-bootstrap-final/SKILL.md",
    "skills/apex-delivery-lifecycle-safe/SKILL.md",
    "skills/oracle-data-change-governance-final/SKILL.md",
    "skills/apex-user-manual/SKILL.md",
    "scripts/Initialize-ApexSkillUpstreams-V2.ps1",
    "scripts/Sync-ApexSkillUpstreams.ps1",
    "scripts/Export-ApexSkillUpstreamSnapshots.ps1",
    "scripts/Restore-ApexSkillUpstreamBackup.ps1",
    "scripts/Setup-ApexSkills.ps1",
    "scripts/Update-ApexSkillUpstreams-V2.ps1",
    "requirements.txt",
    "docs/decisiones-canonicas-finales.md",
    "upstreams.lock.json",
)
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    """Audit required resources and validate Markdown links.

    Returns:
        0 if audit passes, exits with code 1 if audit fails
    """
    errors = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required resource: {rel}")
    for base in (ROOT / "docs", ROOT / "skills"):
        for file in base.rglob("*.md"):
            text = file.read_text(encoding="utf-8", errors="replace")
            for target in LINK.findall(text):
                target = target.split("#", 1)[0].strip()
                if not target or "://" in target or target.startswith("mailto:") or target.startswith("<"):
                    continue
                if not (file.parent / target).resolve().exists():
                    errors.append(f"broken local link: {file.relative_to(ROOT)} -> {target}")
    if errors:
        print("AUDIT_FAIL:")
        print("\n".join(errors))
        raise SystemExit(1)
    print("AUDIT_PASS: required resources and local Markdown links are valid")
    return 0


if __name__ == "__main__":
    main()
