#!/usr/bin/env python3
"""Audit required canonical resources and complete repository Markdown links.

Pre-commit hook that verifies all required governance files exist and all
local Markdown links resolve to existing targets.

Status: ACTIVE (pre-commit hook)
Tests: Covered indirectly by test_quality_audit.py (Q03 link checks)
Dependencies: none (stdlib only)
"""

import subprocess
from pathlib import Path

from audit_markdown_links import audit as audit_markdown

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


def main() -> int:
    """Audit required resources and validate Markdown links.

    Returns:
        0 if audit passes, exits with code 1 if audit fails
    """
    errors = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required resource: {rel}")
    try:
        link_result = audit_markdown()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        errors.append(f"Markdown audit incomplete: {error}")
        link_result = None
    if errors:
        print("AUDIT_FAIL:")
        print("\n".join(errors))
        raise SystemExit(1)
    assert link_result is not None
    if not link_result["passed"]:
        print(
            "SUBAUDIT_INCOMPLETE: required resources exist; whole-repository Markdown coverage or links are unresolved"
        )
        print(
            f"Markdown expected={link_result['expected']} "
            f"covered={link_result['covered']} tracked={link_result['tracked']}"
        )
        for key in ("broken", "coverage_gaps", "external_broken", "external_unverifiable"):
            for item in link_result[key]:
                print(f"{key}: {item}")
        raise SystemExit(2)
    audit_status = "PASS_WITH_NA" if link_result["external_na"] else "PASS"
    print(
        f"RESOURCE_AND_MARKDOWN_SUBAUDIT_{audit_status}: required resources and whole-repository Markdown "
        f"coverage/local links are valid (expected={link_result['expected']} covered={link_result['covered']} "
        f"tracked={link_result['tracked']} tracked_excluded={link_result['tracked_excluded']} "
        f"untracked_included={link_result['untracked_included']} "
        f"excluded_markdown={link_result['excluded_markdown']} links={link_result['links']} "
        f"external={len(link_result['external_links'])} "
        f"external_unverifiable={len(link_result['external_unverifiable'])} "
        f"external_na={len(link_result['external_na'])})"
    )
    for item in link_result["external_na"]:
        print(f"external_na: {item}")
    return 0


if __name__ == "__main__":
    main()
