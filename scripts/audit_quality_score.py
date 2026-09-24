#!/usr/bin/env python3
"""Run a deterministic, agent-neutral quality audit for the repository."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parent.parent
POLICY = "Ningún archivo puede obligar técnicamente a un agente externo arbitrario."
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER = re.compile(r"(?s)^---\s*(.*?)\s*---")
NAME = re.compile(r"^name:\s*[\"']?([^\"'\r\n]+)")


@dataclass(frozen=True)
class Check:
    identifier: str
    title: str
    weight: int
    passed: bool
    evidence: str
    gate: bool = False


def skill_names() -> List[str]:
    return sorted(path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md"))


def markdown_files() -> Iterable[Path]:
    yield from (ROOT / "docs").rglob("*.md")
    yield from (ROOT / "skills").rglob("*.md")
    for path in (ROOT / "README.md", ROOT / "CLAUDE.md", ROOT / "AGENTS.md"):
        if path.is_file():
            yield path


def check_skills(names: List[str]) -> Check:
    errors, metadata_names = [], []
    for name in names:
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        match = FRONTMATTER.match(text)
        if not match:
            errors.append(f"{name}: missing YAML frontmatter")
            continue
        name_match = NAME.search(match.group(1))
        if not name_match or name_match.group(1).strip() != name:
            errors.append(f"{name}: metadata name does not match directory")
        if not re.search(r"^description:\s*.+", match.group(1), re.MULTILINE):
            errors.append(f"{name}: missing description")
        metadata_names.append(name_match.group(1).strip() if name_match else "")
    if len(metadata_names) != len(set(metadata_names)):
        errors.append("duplicate skill metadata names")
    return Check(
        "Q01",
        "Portable skill metadata",
        15,
        not errors,
        "; ".join(errors) or f"{len(names)} SKILL.md files inspected",
        True,
    )


def check_catalogs(names: List[str]) -> Check:
    missing: List[str] = []
    for relative in ("skills/README.md", "skills/SKILLS-QUICK-REFERENCE.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        missing.extend(f"{relative}: {name}" for name in names if name not in text)
    for relative in ("README.md", "CLAUDE.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        if f"{len(names)} skills" not in text and f"{len(names)} specialized skills" not in text:
            missing.append(f"{relative}: missing current count ({len(names)} skills)")
    return Check(
        "Q02",
        "Catalog and documentation synchronization",
        15,
        not missing,
        "; ".join(missing) or "all skills present in four catalogs",
        True,
    )


def check_links() -> Check:
    errors = []
    for path in markdown_files():
        for target in LINK.findall(path.read_text(encoding="utf-8", errors="replace")):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith(("mailto:", "<", "#")):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"{path.relative_to(ROOT)} -> {target}")
    return Check(
        "Q03",
        "Local links and references",
        10,
        not errors,
        "; ".join(errors) or "all local Markdown links resolve",
        True,
    )


def check_required_files() -> Check:
    required = [
        "AGENTS.md",
        "docs/POLITICA-EVOLUCION-ECOSISTEMA.md",
        "docs/ACTUALIZACION-ECOSISTEMA.md",
        "docs/CONTRIBUTING.md",
        "docs/TESTING.md",
        "SECURITY.md",
        ".github/workflows/ci.yml",
        ".pre-commit-config.yaml",
        "requirements.txt",
        "scripts/run_ci_checks.py",
        ".python-version",
        "upstreams.lock.json",
        "tests",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    return Check(
        "Q04",
        "Governance and validation entry points",
        10,
        not missing,
        "; ".join(missing) or "required governance, CI and test entry points exist",
        True,
    )


def check_policy_and_ci() -> Check:
    policy = (ROOT / "docs/POLITICA-EVOLUCION-ECOSISTEMA.md").read_text(encoding="utf-8")
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    runner = (ROOT / "scripts/run_ci_checks.py").read_text(encoding="utf-8")
    ok = (
        POLICY in policy
        and "Python 3.13" in policy
        and "run_ci_checks.py" in ci
        and "audit_skill_ecosystem.py" in runner
        and "pytest" in runner
        and '"diff", "--check"' in runner
        and '"diff", "--cached", "--check"' in runner
        and '"ls-files", "--others", "--exclude-standard", "-z"' in runner
        and 'shutil.which("git")' in runner
    )
    return Check(
        "Q05",
        "Independent enforcement",
        15,
        ok,
        (
            "canonical independence rule and audit/test/whitespace CI controls present"
            if ok
            else "missing canonical independence rule or CI control"
        ),
        True,
    )


def check_upstreams() -> Check:
    try:
        data = json.loads((ROOT / "upstreams.lock.json").read_text(encoding="utf-8"))
        entries = data["repositories"].values()
        fields = {"url", "branch", "expected_commit", "license", "classification", "purpose", "path"}
        errors: List[str] = []
        for item in entries:
            errors.extend(f"{item.get('path')}: missing {field}" for field in fields if not item.get(field))
            if item.get("kind") not in {"managed", "reference"}:
                errors.append(f"{item.get('path')}: invalid classification")
        return Check(
            "Q06",
            "Upstream provenance and classification",
            10,
            not errors,
            "; ".join(errors) or f"{len(entries)} lock entries contain provenance metadata",
            True,
        )
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        return Check("Q06", "Upstream provenance and classification", 10, False, str(error), True)


def check_reproducibility() -> Check:
    files = ["scripts/audit_skill_ecosystem.py", "scripts/audit_quality_score.py", "tests", "pyproject.toml"]
    ok = all((ROOT / item).exists() for item in files)
    return Check(
        "Q07",
        "Reproducible audit and test entry points",
        10,
        ok,
        "audit scripts, tests and tool configuration are versioned",
        True,
    )


def check_traceability() -> Check:
    text = (ROOT / "control-proyecto/pendientes.md").read_text(encoding="utf-8")
    ok = all(term in text for term in ("Objetivo", "Alcance", "Dependencias", "Criterio de cierre"))
    return Check(
        "Q08",
        "Change traceability",
        5,
        ok,
        (
            "project backlog records objective, scope, dependencies and closure"
            if ok
            else "backlog lacks required traceability fields"
        ),
        True,
    )


def check_standards() -> Check:
    files = ["pyproject.toml", ".bandit.yaml", ".pre-commit-config.yaml", "SECURITY.md"]
    ok = all((ROOT / item).is_file() for item in files)
    return Check(
        "Q09",
        "Programming and security standards",
        10,
        ok,
        (
            "formatting, typing, security and hook standards are versioned"
            if ok
            else "one or more standard configurations are missing"
        ),
        True,
    )


def run() -> Dict[str, object]:
    names = skill_names()
    checks = [
        check_skills(names),
        check_catalogs(names),
        check_links(),
        check_required_files(),
        check_policy_and_ci(),
        check_upstreams(),
        check_reproducibility(),
        check_traceability(),
        check_standards(),
    ]
    return {
        "score": sum(check.weight for check in checks if check.passed),
        "maximum": sum(check.weight for check in checks),
        "gates_pass": all(check.passed for check in checks if check.gate),
        "checks": [check.__dict__ for check in checks],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"QUALITY_AUDIT_{'PASS' if result['gates_pass'] else 'FAIL'}: {result['score']}/{result['maximum']}")
        checks = result["checks"]
        assert isinstance(checks, list)
        for check in checks:
            status = "PASS" if check["passed"] else "FAIL"
            line = f"{check['identifier']} {status} ({check['weight']}): {check['title']} — {check['evidence']}"
            print(line)
    return 0 if result["gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
