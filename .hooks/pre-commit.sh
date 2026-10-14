#!/bin/bash
# Append staged Git metadata to the local JSON Lines audit log.

set -euo pipefail

python_bin="${PYTHON_BIN:-python3}"
"$python_bin" <<'PYTHON_EOF'
import json
import os
import subprocess
import uuid
from datetime import datetime, timezone


def git(*args: str) -> str:
    completed = subprocess.run(["git", *args], check=True, capture_output=True)
    return completed.stdout.decode("utf-8", errors="replace").strip()


def git_config(name: str) -> str:
    completed = subprocess.run(["git", "config", name], capture_output=True)
    return completed.stdout.decode("utf-8", errors="replace").strip() if completed.returncode == 0 else ""


branch_result = subprocess.run(["git", "symbolic-ref", "--short", "-q", "HEAD"], capture_output=True)
branch = branch_result.stdout.decode("utf-8", errors="replace").strip() if branch_result.returncode == 0 else "detached"
files = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "-z"], check=True, capture_output=True
).stdout.split(b"\0")
files_changed = [path.decode("utf-8", errors="replace") for path in files if path]
timestamp = datetime.now(timezone.utc).isoformat()
entry = {
    "timestamp_utc": timestamp,
    "event_id": str(uuid.uuid4()),
    "event_phase": "completed",
    "operation": "git_staged_changes",
    "source": "git_index",
    "result": "STAGED",
    "exit_code": 0,
    "branch": branch,
    "author": git_config("user.name"),
    "email": git_config("user.email"),
    "files_count": len(files_changed),
    "files_changed": files_changed,
}

audit_path = os.path.join("control-proyecto", ".bitacora.json")
os.makedirs(os.path.dirname(audit_path), exist_ok=True)
with open(audit_path, "a", encoding="utf-8", newline="\n") as audit_file:
    audit_file.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
    audit_file.flush()
    os.fsync(audit_file.fileno())

print(f"Audit logged: {len(files_changed)} staged files at {timestamp}")
PYTHON_EOF
