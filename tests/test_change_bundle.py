import json
from pathlib import Path

import pytest

from scripts.change_bundle import ChangeBundleError, load_bundle, render_execution_sql


def write_bundle(
    root: Path, *, include_snapshot: bool = True, include_rollback: bool = False, **changes: object
) -> Path:
    phases = ["preflight", "apply", "verify"]
    if include_rollback:
        phases.append("rollback")
    if include_snapshot:
        phases.append("snapshot")
    for phase in phases:
        (root / f"{phase}.sql").write_text(f"prompt {phase}\n", encoding="utf-8")
    payload = {
        "version": 1,
        "id": "fix-category-join",
        "kind": "oracle_ddl",
        "target": {"type": "view", "name": "data.v_example"},
        "baseline": {"fingerprint": "sha256:observed"},
        "artifacts": {phase: f"{phase}.sql" for phase in phases},
    }
    payload.update(changes)
    path = root / "change.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_bundle_snapshot_is_optional(tmp_path):
    bundle = load_bundle(write_bundle(tmp_path, include_snapshot=False), tmp_path)

    assert "snapshot" not in bundle["_resolved_artifacts"]
    with pytest.raises(ChangeBundleError, match="snapshot.sql"):
        render_execution_sql(bundle, ("snapshot",))


def test_bundle_requires_baseline_and_all_execution_artifacts(tmp_path):
    bundle_path = write_bundle(tmp_path, baseline={})

    with pytest.raises(ChangeBundleError, match="fingerprint"):
        load_bundle(bundle_path, tmp_path)


def test_bundle_does_not_require_rollback_artifact(tmp_path):
    bundle = load_bundle(write_bundle(tmp_path, include_snapshot=False), tmp_path)

    assert "rollback" not in bundle["_resolved_artifacts"]


def test_optional_rollback_artifact_is_validated_but_not_rendered(tmp_path):
    bundle = load_bundle(write_bundle(tmp_path, include_snapshot=False, include_rollback=True), tmp_path)

    rendered = render_execution_sql(bundle)

    assert "rollback" in bundle["_resolved_artifacts"]
    assert "CHANGE_PHASE=rollback" not in rendered


def test_bundle_rejects_artifact_path_outside_checkout(tmp_path):
    bundle_path = write_bundle(tmp_path)
    data = json.loads(bundle_path.read_text(encoding="utf-8"))
    data["artifacts"]["apply"] = "../outside.sql"
    bundle_path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ChangeBundleError, match="fuera del checkout"):
        load_bundle(bundle_path, tmp_path)


def test_rendered_bundle_marks_phases_and_keeps_rollback_explicit(tmp_path):
    bundle = load_bundle(write_bundle(tmp_path), tmp_path)

    rendered = render_execution_sql(bundle)

    assert "CHANGE_PHASE=preflight" in rendered
    assert "CHANGE_PHASE=apply" in rendered
    assert "CHANGE_PHASE=verify" in rendered
    assert "rollback" not in rendered.lower()
    assert "__CHANGE_TIMER_apply_START" in rendered


def test_rendered_bundle_rejects_sqlcl_exit_command(tmp_path):
    bundle_path = write_bundle(tmp_path)
    (tmp_path / "apply.sql").write_text("exit\n", encoding="utf-8")

    with pytest.raises(ChangeBundleError, match="comando SQLcl"):
        render_execution_sql(load_bundle(bundle_path, tmp_path))


@pytest.mark.parametrize("command", ("@@other.sql", "start other.sql", "spool output.log"))
def test_rendered_bundle_rejects_sqlcl_indirection_and_output_commands(tmp_path, command):
    bundle_path = write_bundle(tmp_path)
    (tmp_path / "apply.sql").write_text(command, encoding="utf-8")

    with pytest.raises(ChangeBundleError, match="comando SQLcl"):
        render_execution_sql(load_bundle(bundle_path, tmp_path))


def test_wrapper_requires_baseline_proof_before_apply_execution():
    wrapper = Path("scripts/Invoke-OracleApexChange.ps1").read_text(encoding="utf-8")

    assert "--phase preflight" in wrapper
    assert "--phase apply --phase verify" in wrapper
    assert "BASELINE_MISMATCH" in wrapper
    assert wrapper.index("Invoke-BundleSqlclPhase -SqlFile $preflightSql") < wrapper.index(
        "Invoke-BundleSqlclPhase -SqlFile $applyVerifySql"
    )
    assert (
        wrapper.index("Invoke-BundleSqlclPhase -SqlFile $preflightSql")
        < wrapper.index("Invoke-BundleSqlclPhase -SqlFile $snapshotSql")
        < wrapper.index("Invoke-BundleSqlclPhase -SqlFile $applyVerifySql")
    )
    assert "-BackupChoice yes or no" in wrapper
    assert "BACKUP_FAILED" in wrapper


def test_power_shell_sql_mutation_requires_confirmation_and_backup_decision():
    script = Path("scripts/Execute-OracleSql.ps1").read_text(encoding="utf-8")

    assert "-ReadOnly accepts one SELECT" in script
    assert "A live mutation requires -Confirmed" in script
    assert "A live mutation requires -BackupChoice yes or no" in script
    assert (
        script.index('$scriptLines += "PROMPT CHANGE_PHASE=backup"')
        < script.index("$scriptLines += $backupContent")
        < script.index("$scriptLines += $sqlContent")
    )


def test_power_shell_page_import_requires_confirmation_and_prior_backup():
    script = Path("scripts/Deploy-ApexPage.ps1").read_text(encoding="utf-8")

    assert "A live page import requires -Confirmed" in script
    assert "A live page import requires -BackupChoice yes or no" in script
    assert "provide a pre-change native export" in script
    examples = script.split(".EXAMPLE", maxsplit=1)[1].split("#>", maxsplit=1)[0]
    commands = [line.strip() for line in examples.splitlines() if ".\\scripts\\Deploy-ApexPage.ps1" in line]

    assert len(commands) == 2
    assert all("-Confirmed" in command and "-BackupChoice no" in command for command in commands)


def test_power_shell_bundle_rejects_snapshot_when_backup_declined():
    script = Path("scripts/Invoke-OracleApexChange.ps1").read_text(encoding="utf-8")

    assert '$BackupChoice -eq "no" -and $bundleDocument.artifacts' in script
    assert 'PSObject.Properties.Name -contains "snapshot"' in script
    assert script.index("UNEXPECTED_BACKUP_ARTIFACT") < script.index("Initialize-OracleConnection.ps1")
