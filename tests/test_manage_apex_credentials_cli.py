import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "manage_apex_credentials.py"


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


def test_direct_script_apex_status_uses_package_imports():
    result = run(str(SCRIPT), "apex-status", "--environment", "test")
    assert result.returncode in (0, 1)
    assert "APEX_PROFILE_" in result.stdout
    assert "ModuleNotFoundError" not in result.stderr


def test_module_apex_status_uses_package_imports():
    result = run("-m", "scripts.manage_apex_credentials", "apex-status", "--environment", "test")
    assert result.returncode in (0, 1)
    assert "APEX_PROFILE_" in result.stdout
    assert "ModuleNotFoundError" not in result.stderr


def test_initializer_calls_the_documented_direct_script_path():
    initializer = (ROOT / "scripts" / "Initialize-ApexCodexProject.ps1").read_text(encoding="utf-8")
    assert "& $python $credentials status --environment $Environment" in initializer


def test_initializer_is_best_effort_for_remote_profiles():
    initializer = (ROOT / "scripts" / "Initialize-ApexCodexProject.ps1").read_text(encoding="utf-8")
    assert "$SkipRemoteProbe" in initializer
    assert "$ValidateOracleTest" not in initializer
    assert "$credentials apex-status --environment production" in initializer
    assert "Get-OracleEnvironmentState -Environment test" in initializer
    assert "Get-OracleEnvironmentState -Environment production" in initializer
    assert "probe --environment $Environment" in initializer
    assert "NOT_PROBED" in initializer
    assert "$RegisterProductionMcp" not in initializer
    assert "MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE" in initializer
    assert "MCP_REGISTRATION_NOT_SUPPORTED_IN_THIS_BOOTSTRAP" not in initializer


def test_initializer_does_not_invoke_mutating_upstream_patches():
    initializer = (ROOT / "scripts" / "Initialize-ApexCodexProject.ps1").read_text(encoding="utf-8")
    assert "Apply-ApexMcpDirectConnectionPatch.py" not in initializer
    assert "Apply-ApexMcpApex241CompatibilityPatch.py" not in initializer
    assert "validate_apex_mcp_adapter.py" in initializer
    assert "codex mcp add apex-mcp-test" not in initializer
    assert "codex mcp remove" not in initializer
    assert "validate_apex_mcp_handshake.py" not in initializer


def test_initializer_skip_remote_probe_keeps_profile_checks_only():
    initializer = (ROOT / "scripts" / "Initialize-ApexCodexProject.ps1").read_text(encoding="utf-8")
    assert "if ($SkipRemoteProbe)" in initializer
    assert "Oracle probe skipped by -SkipRemoteProbe" in initializer


def test_initializer_production_mcp_uses_same_labels_as_test():
    initializer = (ROOT / "scripts" / "Initialize-ApexCodexProject.ps1").read_text(encoding="utf-8")
    assert "apex-mcp-production" in initializer
    assert initializer.count("MCP_REGISTRATION_PREEXISTING_UNVERIFIED") == 2
    assert initializer.count("MCP_REGISTRATION_SKIPPED_UNSAFE_SURFACE") >= 4


def test_initializer_does_not_reuse_profile_exit_code_for_skill_installer():
    initializer = (ROOT / "scripts" / "Initialize-ApexCodexProject.ps1").read_text(encoding="utf-8")
    assert "$skillInstallerSucceeded = $?" in initializer
