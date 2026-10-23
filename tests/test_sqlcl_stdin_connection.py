"""Regression tests: PowerShell SQLcl routes never pass the connection string on argv."""

import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
# Windows PowerShell 5.1 and PowerShell 7 build the SQLcl stdin writer differently; test both.
SHELLS = [shell for shell in (shutil.which("pwsh"), shutil.which("powershell")) if shell]
CONNECTION = "apex_test_user/NotARealSecret#42@db.example.invalid:1521/TESTPDB"
SQLCL_ROUTES = ("Deploy-ApexPage.ps1", "Execute-OracleSql.ps1", "Invoke-OracleApexChange.ps1")
FAKE_SQLCL = """
import json
import os
import sys

with open(os.environ["FAKE_SQLCL_LOG"], "w", encoding="utf-8") as log:
    json.dump({"argv": sys.argv[1:], "stdin": sys.stdin.buffer.read().decode("latin-1")}, log)
print("FAKE_SQLCL_OUTPUT")
sys.exit(int(os.environ.get("FAKE_SQLCL_EXIT", "0")))
"""


def _ps_literal(value: object) -> str:
    return str(value).replace("'", "''")


def _fake_sqlcl(tmp_path: Path) -> Path:
    """Create a SQLcl stand-in that records its argv and stdin."""
    program = tmp_path / "fake_sqlcl.py"
    program.write_text(FAKE_SQLCL, encoding="utf-8")
    if os.name == "nt":
        launcher = tmp_path / "sql.cmd"
        launcher.write_text(f'@"{sys.executable}" "{program}" %*\r\n', encoding="utf-8")
    else:
        launcher = tmp_path / "sql"
        launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{program}" "$@"\n', encoding="utf-8")
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)
    return launcher


def _run_powershell(shell: str, script: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )


@pytest.mark.parametrize("script_name", SQLCL_ROUTES)
def test_sqlcl_routes_send_connection_through_stdin_helper(script_name):
    script = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")

    assert '. (Join-Path $PSScriptRoot "Invoke-SqlclScript.ps1")' in script
    assert "Invoke-SqlclScript -SqlclPath" in script
    assert "-Connection $env:APEX_SQLCL_CONN" in script
    assert "Start-Process" not in script
    for line in script.splitlines():
        if "APEX_SQLCL_CONN" in line:
            assert not re.search(r"ArgumentList|\"-S\"|&\s*\$", line), line


@pytest.mark.skipif(not SHELLS, reason="PowerShell is not installed")
@pytest.mark.parametrize("shell", SHELLS)
def test_invoke_sqlcl_script_keeps_connection_out_of_argv(tmp_path, shell):
    sqlcl = _fake_sqlcl(tmp_path)
    log = tmp_path / "sqlcl.json"
    sql_script = tmp_path / "phase script.sql"
    sql_script.write_text("select 1 from dual;\nexit\n", encoding="utf-8")
    harness = tmp_path / "harness.ps1"
    harness.write_text(
        f"""
. '{_ps_literal(ROOT / "scripts" / "Invoke-SqlclScript.ps1")}'
# Interactive hosts often run with a UTF-8 console, whose encoder emits a byte-order mark.
try {{ [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($true) }} catch {{ }}
$consoleBefore = [Console]::InputEncoding.WebName
$result = Invoke-SqlclScript -SqlclPath '{_ps_literal(sqlcl)}' -Connection '{_ps_literal(CONNECTION)}' `
    -ScriptPath '{_ps_literal(sql_script)}'
Write-Output "EXIT=$($result.ExitCode)"
Write-Output "OUT=$($result.StdOut.Trim())"
Write-Output "CONSOLE_RESTORED=$([Console]::InputEncoding.WebName -eq $consoleBefore)"
""",
        encoding="utf-8",
    )
    env = {**os.environ, "FAKE_SQLCL_LOG": str(log), "FAKE_SQLCL_EXIT": "7"}

    completed = _run_powershell(shell, harness, env=env)

    assert completed.returncode == 0, completed.stderr
    assert "EXIT=7" in completed.stdout
    assert "OUT=FAKE_SQLCL_OUTPUT" in completed.stdout
    assert "CONSOLE_RESTORED=True" in completed.stdout
    recorded = json.loads(log.read_text(encoding="utf-8"))
    assert recorded["argv"] == ["-S", "/nolog"]
    assert not any(CONNECTION in argument or "NotARealSecret" in argument for argument in recorded["argv"])
    lines = recorded["stdin"].splitlines()
    # A byte-order mark would make SQLcl reject the WHENEVER guard and ignore a failed connect.
    assert lines[0] == "WHENEVER SQLERROR EXIT FAILURE"
    assert lines[1] == f"connect {CONNECTION}"
    assert lines[2] == f'@"{sql_script}"'
    assert lines[3] == "EXIT"


@pytest.mark.skipif(not SHELLS, reason="PowerShell is not installed")
@pytest.mark.parametrize("shell", SHELLS)
def test_execute_oracle_sql_readonly_route_keeps_connection_out_of_argv_and_audit(tmp_path, shell):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    for helper in ("Execute-OracleSql.ps1", "Write-ApexAuditEvent.ps1", "Invoke-SqlclScript.ps1"):
        shutil.copy2(ROOT / "scripts" / helper, scripts_dir / helper)
    sqlcl = _fake_sqlcl(tmp_path)
    log = tmp_path / "sqlcl.json"
    env = {
        **os.environ,
        "APEX_SQLCL_CONN": CONNECTION,
        "APEX_SQLCL_PATH": str(sqlcl),
        "APEX_ENVIRONMENT": "testing",
        "FAKE_SQLCL_LOG": str(log),
    }

    completed = _run_powershell(
        shell, scripts_dir / "Execute-OracleSql.ps1", "-Sql", "select 1 from dual", "-ReadOnly", env=env
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "FAKE_SQLCL_OUTPUT" in completed.stdout
    assert "NotARealSecret" not in completed.stdout + completed.stderr
    recorded = json.loads(log.read_text(encoding="utf-8"))
    assert recorded["argv"] == ["-S", "/nolog"]
    assert f"connect {CONNECTION}" in recorded["stdin"].splitlines()
    audit = (tmp_path / "control-proyecto" / ".bitacora.json").read_text(encoding="utf-8")
    entries = [json.loads(line) for line in audit.splitlines()]
    assert entries[-1]["result"] == "SUCCESS"
    assert entries[-1]["exit_code"] == 0
    assert "NotARealSecret" not in audit
