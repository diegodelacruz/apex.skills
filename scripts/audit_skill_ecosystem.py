#!/usr/bin/env python3
"""Audit controlled local Markdown links and required canonical resources."""
import re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REQUIRED=(
    'skills/apex-project-bootstrap-final/SKILL.md',
    'skills/apex-delivery-lifecycle-safe/SKILL.md',
    'skills/oracle-data-change-governance-final/SKILL.md',
    'skills/apex-user-manual/SKILL.md',
    'scripts/Initialize-ApexSkillUpstreams-V2.ps1',
    'scripts/Update-ApexSkillUpstreams-V2.ps1',
    'requirements.txt',
    'docs/decisiones-canonicas-finales.md',
)
LINK=re.compile(r'\[[^\]]+\]\(([^)]+)\)')

def main():
    errors=[]
    for rel in REQUIRED:
        if not (ROOT/rel).is_file(): errors.append(f'missing required resource: {rel}')
    for base in (ROOT/'docs', ROOT/'skills'):
        for file in base.rglob('*.md'):
            text=file.read_text(encoding='utf-8',errors='replace')
            for target in LINK.findall(text):
                target=target.split('#',1)[0].strip()
                if not target or '://' in target or target.startswith('mailto:') or target.startswith('<'): continue
                if not (file.parent/target).resolve().exists(): errors.append(f'broken local link: {file.relative_to(ROOT)} -> {target}')
    if errors:
        print('AUDIT_FAIL:'); print('\n'.join(errors)); raise SystemExit(1)
    print('AUDIT_PASS: required resources and local Markdown links are valid')
if __name__=='__main__': main()
