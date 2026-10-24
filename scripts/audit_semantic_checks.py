#!/usr/bin/env python3
"""Report orphan files and stale key documentation without changing anything.

Read-only diagnostic salvaged from PR #15 (checks SM08 and SM09). It only
reports findings; policy section 7 reserves the decision to repair for review
with the user. It is not a CI gate: see
docs/decisiones/20261023-rescate-pr15-auditoria-semantica.md.

Status: ACTIVE (on-demand diagnostic)
Tests: tests/test_audit_semantic_checks.py
Dependencies: none (stdlib and git)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess  # nosec B404
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
MAX_AGE_DAYS = 180
CORPUS_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".ps1", ".toml", ".sh", ".txt", ".cfg", ".ini"}
KEY_DOCS = ("CLAUDE.md", "README.md", "AGENTS.md", "skills/README.md")
DATE_LABEL = re.compile(
    r"^\W*(?:last\s+updated|[uú]ltima\s+actualizaci[oó]n|actualizado|fecha)\W*:\W*(\d{4}-\d{2}-\d{2})",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class SemanticResult:
    identifier: str
    title: str
    findings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.findings


def tracked_files(root: Path) -> List[str]:
    """Return repository-relative paths tracked by Git, using forward slashes."""
    result = subprocess.run(  # nosec B603 B607
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return sorted(item for item in result.stdout.decode("utf-8").split("\0") if item)


def _corpus(root: Path, files: Sequence[str]) -> Dict[str, str]:
    corpus = {}
    for relative in files:
        if Path(relative).suffix.lower() not in CORPUS_SUFFIXES:
            continue
        try:
            corpus[relative] = (root / relative).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return corpus


def check_orphan_files(root: Path, files: Sequence[str]) -> SemanticResult:
    """SM08: report scripts/*.py and docs/*.md that no other tracked file mentions."""
    result = SemanticResult("SM08", "Orphan scripts and top-level docs")
    corpus = _corpus(root, files)
    candidates = [
        item
        for item in files
        if (
            item.startswith("scripts/")
            and item.count("/") == 1
            and item.endswith(".py")
            and item != "scripts/__init__.py"
        )
        or (item.startswith("docs/") and item.count("/") == 1 and item.endswith(".md"))
    ]
    for candidate in candidates:
        path = Path(candidate)
        referenced = False
        for other, content in corpus.items():
            if other == candidate:
                continue
            if path.name in content or (path.suffix == ".py" and other.endswith(".py") and path.stem in content):
                referenced = True
                break
        if not referenced:
            result.findings.append(f"{candidate}: no other tracked file mentions it")
    result.notes.append(f"{len(candidates)} candidates checked against {len(corpus)} tracked text files")
    return result


def check_doc_freshness(
    root: Path, files: Sequence[str], today: Optional[date] = None, max_age_days: int = MAX_AGE_DAYS
) -> SemanticResult:
    """SM09: report key docs whose latest labelled update date is older than the limit."""
    result = SemanticResult("SM09", f"Key documentation updated within {max_age_days} days")
    today = today or date.today()
    tracked = set(files)
    key_docs = [item for item in KEY_DOCS if item in tracked]
    key_docs += [item for item in files if item.startswith("docs/") and item.count("/") == 1 and item.endswith(".md")]
    dated = 0
    for relative in key_docs:
        text = (root / relative).read_text(encoding="utf-8", errors="replace")
        dates = []
        for value in DATE_LABEL.findall(text):
            try:
                dates.append(date.fromisoformat(value))
            except ValueError:
                result.findings.append(f"{relative}: invalid update date {value}")
        if not dates:
            continue
        dated += 1
        age = (today - max(dates)).days
        if age > max_age_days:
            result.findings.append(f"{relative}: last labelled update {max(dates)} is {age} days old")
    result.notes.append(f"{dated} of {len(key_docs)} key docs declare a labelled update date")
    return result


def run(root: Path = ROOT, today: Optional[date] = None, max_age_days: int = MAX_AGE_DAYS) -> List[SemanticResult]:
    """Run every semantic check against the tracked files under root."""
    files = tracked_files(root)
    return [check_orphan_files(root, files), check_doc_freshness(root, files, today, max_age_days)]


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Print the report; exit 0 without findings, 1 with findings, 2 if incomplete."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    parser.add_argument("--max-age-days", type=int, default=MAX_AGE_DAYS)
    args = parser.parse_args(argv)
    try:
        results = run(ROOT, max_age_days=args.max_age_days)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"SEMANTIC_INCOMPLETE: could not list tracked files: {error}")
        return 2
    status = "SEMANTIC_PASS" if all(item.passed for item in results) else "SEMANTIC_FINDINGS"
    if args.json:
        payload = {
            "status": status,
            "checks": [
                {"id": item.identifier, "title": item.title, "findings": item.findings, "notes": item.notes}
                for item in results
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for item in results:
            print(f"[{'OK' if item.passed else 'FINDINGS'}] {item.identifier} {item.title}")
            for note in item.notes:
                print(f"  note: {note}")
            for finding in item.findings:
                print(f"  finding: {finding}")
        print(f"{status}: read-only report; nothing was changed")
    return 0 if status == "SEMANTIC_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
