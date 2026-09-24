#!/usr/bin/env python3
"""Run the repository's CI checks locally with the active Python interpreter."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path


def main() -> int:
    """Run all checks required by GitHub Actions and stop on the first failure."""
    if sys.version_info[:2] != (3, 13):
        print(
            f"CI requires Python 3.13; active interpreter is {sys.version_info.major}.{sys.version_info.minor}.",
            file=sys.stderr,
        )
        return 2

    commands: Sequence[Sequence[str]] = [
        [sys.executable, "-m", "pip", "check"],
        [sys.executable, "scripts/audit_skill_ecosystem.py"],
        [sys.executable, "scripts/audit_quality_score.py"],
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-v",
            "--cov=scripts",
            "--cov-report=xml",
            "--cov-report=term",
        ],
        [sys.executable, "-m", "black", "--check", "scripts", "tests"],
        [sys.executable, "-m", "isort", "--check-only", "scripts", "tests"],
        [sys.executable, "-m", "flake8", "scripts", "tests", "--max-line-length=120"],
        [
            sys.executable,
            "-m",
            "mypy",
            "--ignore-missing-imports",
            "--explicit-package-bases",
            "scripts",
            "tests",
        ],
        [sys.executable, "-m", "bandit", "-c", ".bandit.yaml", "-r", "scripts", "tests"],
    ]

    for command in commands:
        print(f"\n$ {' '.join(command)}", flush=True)
        result = subprocess.run(command, check=False)
        if result.returncode:
            print(f"CI check failed with exit code {result.returncode}.", file=sys.stderr)
            return result.returncode

    if run_secret_scan():
        return 1

    if run_whitespace_check():
        return 1

    print("\nAll local CI checks passed.")
    return 0


def run_secret_scan() -> int:
    """Compare a fresh detect-secrets scan to the checked-in baseline safely."""
    root = Path(__file__).resolve().parent.parent
    baseline_path = root / ".secrets.baseline"
    original = json.loads(baseline_path.read_text(encoding="utf-8"))
    temp_path: Path | None = None
    exclude_files = (
        r"(^|[\\/])(\.env|\.mypy_cache|\.pytest_cache|\.venv|\.upstreams|\.upstream-backups|"
        r"htmlcov|\.secrets\.baseline(\.scan\.[^\\/]+)?|"
        r"control-proyecto[\\/]\.bitacora\.json|runtime[\\/]sqlcl-runtime\.json)([\\/]|$)|"
        r"(^|[\\/])vendor[\\/]upstreams[\\/][^\\/]+\.zip$"
    )
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=".secrets.baseline.scan.",
            dir=root,
            delete=False,
        ) as temp_file:
            temp_file.write(json.dumps(original))
            temp_path = Path(temp_file.name)

        command = [
            sys.executable,
            "-m",
            "detect_secrets",
            "scan",
            "--baseline",
            str(temp_path),
            "--all-files",
            "--force-use-all-plugins",
            "--exclude-files",
            exclude_files,
        ]
        print(f"\n$ {' '.join(command)}", flush=True)
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode:
            print(result.stderr or result.stdout, file=sys.stderr)
            print("detect-secrets scan failed.", file=sys.stderr)
            return result.returncode

        scanned = json.loads(temp_path.read_text(encoding="utf-8"))
        known = {
            (name, item.get("hashed_secret")) for name, items in original.get("results", {}).items() for item in items
        }
        new = {
            (name, item.get("hashed_secret")) for name, items in scanned.get("results", {}).items() for item in items
        } - known
        if new:
            print("New possible secrets detected; review before updating the baseline:", file=sys.stderr)
            for name, line, secret_type in sorted(
                (name, item.get("line_number", "?"), item.get("type", "unknown"))
                for name, items in scanned.get("results", {}).items()
                for item in items
                if (name, item.get("hashed_secret")) in new
            ):
                print(f"{name}:{line}: {secret_type}", file=sys.stderr)
            return 1
        print("No unapproved secrets detected.")
        return 0
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def run_whitespace_check(root: Path | None = None) -> int:
    """Check tracked and untracked text files for trailing whitespace."""
    root = root or Path(__file__).resolve().parent.parent
    git_executable = shutil.which("git")
    if not git_executable:
        print("Git executable was not found on PATH.", file=sys.stderr)
        return 1

    commands = ([git_executable, "diff", "--check"], [git_executable, "diff", "--cached", "--check"])
    for command in commands:
        print(f"\n$ {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            print(f"Whitespace check failed with exit code {result.returncode}.", file=sys.stderr)
            return result.returncode

    result = subprocess.run(
        [git_executable, "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = root / Path(raw_path.decode("utf-8", errors="surrogateescape"))
        try:
            contents = path.read_bytes()
            contents.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(contents.splitlines(), start=1):
            if line.endswith((b" ", b"\t")):
                print(f"{path.relative_to(root)}:{line_number}: trailing whitespace", file=sys.stderr)
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
