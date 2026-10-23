import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")
BASH = shutil.which("bash")


def _ps_literal(path: Path) -> str:
    return str(path).replace("'", "''")


@pytest.mark.skipif(POWERSHELL is None, reason="PowerShell is not installed")
def test_powershell_audit_helper_appends_correlated_json_lines(tmp_path):
    helper = ROOT / "scripts" / "Write-ApexAuditEvent.ps1"
    source = tmp_path / "change.sql"
    audit_path = tmp_path / "control-proyecto" / ".bitacora.json"
    source.write_text("delete from data.example;", encoding="utf-8")
    harness = tmp_path / "audit-harness.ps1"
    harness.write_text(
        f"""
. '{_ps_literal(helper)}'
$identity = Get-ApexAuditFileMetadata -Path '{_ps_literal(source)}' -RepositoryRoot '{_ps_literal(tmp_path)}'
$start = New-ApexAuditEntry -EventId 'event-1' -EventPhase started -Environment 'TEST' `
    -Operation 'oracle_sql_file' -Source $identity.source -SourceSha256 $identity.source_sha256 `
    -Result 'STARTED' -ExitCode $null -TimingsMs ([ordered]@{{}}) -Metadata ([ordered]@{{backup_choice='no'}})
Write-ApexAuditEvent -AuditPath '{_ps_literal(audit_path)}' -Entry $start
$complete = New-ApexAuditEntry -EventId 'event-1' -EventPhase completed -Environment 'TEST' `
    -Operation 'oracle_sql_file' -Source $identity.source -SourceSha256 $identity.source_sha256 `
    -Result 'SUCCESS' -ExitCode 0 -TimingsMs ([ordered]@{{route_total=12}}) -Metadata ([ordered]@{{backup_choice='no'}})
Write-ApexAuditEvent -AuditPath '{_ps_literal(audit_path)}' -Entry $complete
""",
        encoding="utf-8",
    )

    subprocess.run([POWERSHELL, "-NoProfile", "-File", str(harness)], check=True, capture_output=True, text=True)

    entries = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert [entry["event_phase"] for entry in entries] == ["started", "completed"]
    assert {entry["event_id"] for entry in entries} == {"event-1"}
    assert entries[0]["source"] == "change.sql"
    assert entries[1]["result"] == "SUCCESS"
    assert entries[1]["timings_ms"]["route_total"] == 12
    assert "delete from data.example" not in audit_path.read_text(encoding="utf-8")


@pytest.mark.skipif(POWERSHELL is None, reason="PowerShell is not installed")
def test_powershell_audit_helper_surfaces_write_failures(tmp_path):
    helper = ROOT / "scripts" / "Write-ApexAuditEvent.ps1"
    blocked_path = tmp_path / "audit-is-a-directory"
    blocked_path.mkdir()
    harness = tmp_path / "audit-failure-harness.ps1"
    harness.write_text(
        f"""
. '{_ps_literal(helper)}'
$entry = [ordered]@{{event_id='event-fail';event_phase='started';operation='oracle_sql_file'}}
$failed = $false
try {{ Write-ApexAuditEvent -AuditPath '{_ps_literal(blocked_path)}' -Entry $entry }} catch {{ $failed = $true }}
if (-not $failed) {{ exit 1 }}
exit 0
""",
        encoding="utf-8",
    )

    subprocess.run([POWERSHELL, "-NoProfile", "-File", str(harness)], check=True, capture_output=True, text=True)


@pytest.mark.parametrize(
    ("script_name", "operation_marker", "execution_marker"),
    [
        ("Execute-OracleSql.ps1", "oracle_sql_file", "Invoke-SqlclScript -SqlclPath"),
        ("Deploy-ApexPage.ps1", "apex_native_import", "Invoke-SqlclScript -SqlclPath"),
        ("Invoke-OracleApexChange.ps1", "oracle_apex_change_bundle", "Invoke-BundleSqlclPhase -SqlFile $preflightSql"),
    ],
)
def test_powershell_write_routes_persist_start_and_completion_before_return(
    script_name, operation_marker, execution_marker
):
    script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

    assert "Write-ApexAuditEvent.ps1" in script
    assert "New-ApexAuditEntry" in script
    assert "-EventPhase started" in script
    assert "-EventPhase completed" in script
    assert operation_marker in script
    assert script.index("EventPhase started") < script.index(execution_marker)
    assert "Do not retry automatically" in script
    assert "could not be persisted" in script
    assert (
        "no SQL was submitted" in script
        or "no APEX import was submitted" in script
        or "no bundle SQL was submitted" in script
    )


def test_powershell_readonly_route_does_not_gate_query_on_start_audit():
    script = (ROOT / "scripts" / "Execute-OracleSql.ps1").read_text(encoding="utf-8")
    start_event = script.index("$auditStart = New-ApexAuditEntry")
    start_write = script.index("Write-ApexAuditEvent -AuditPath $auditPath -Entry $auditStart")
    sql_execution = script.index("Invoke-SqlclScript -SqlclPath $SqlclPath")
    completion_write = script.index("Write-ApexAuditEvent -AuditPath $auditPath -Entry $auditComplete")

    assert "if (-not $ReadOnly) {" in script[start_write - 100 : start_write]
    assert start_event < start_write < sql_execution < completion_write
    assert "Read-only SQL completed, but its audit result could not be persisted" in script


@pytest.mark.skipif(BASH is None, reason="Bash is required")
def test_precommit_audit_hook_appends_jsonl_without_rewriting_existing_events(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Audit Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "audit@example.invalid"], cwd=tmp_path, check=True)
    staged_file = tmp_path / "tracked.txt"
    staged_file.write_text("change\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_path, check=True)
    audit_path = tmp_path / "control-proyecto" / ".bitacora.json"
    audit_path.parent.mkdir()
    audit_path.write_text('{"operation":"previous"}\n', encoding="utf-8")

    env = os.environ.copy()
    env["PYTHON_BIN"] = "python" if os.name == "nt" else (shutil.which("python3") or "python3")
    completed = subprocess.run(
        [BASH, str(ROOT / ".hooks" / "pre-commit.sh")],
        cwd=tmp_path,
        env=env,
        check=False,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stderr.decode("utf-8", errors="replace")

    entries = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert len(entries) == 2
    assert entries[0] == {"operation": "previous"}
    assert entries[1]["operation"] == "git_staged_changes"
    assert entries[1]["files_changed"] == ["tracked.txt"]
