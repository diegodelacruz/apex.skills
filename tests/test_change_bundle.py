import json
from pathlib import Path

import pytest

from scripts.change_bundle import ChangeBundleError, load_bundle, render_execution_sql


def write_bundle(root: Path, **changes: object) -> Path:
    for phase in ("preflight", "apply", "verify", "rollback", "snapshot"):
        (root / f"{phase}.sql").write_text(f"prompt {phase}\n", encoding="utf-8")
    payload = {
        "version": 1,
        "id": "fix-category-join",
        "kind": "oracle_ddl",
        "target": {"type": "view", "name": "data.v_example"},
        "baseline": {"fingerprint": "sha256:observed"},
        "artifacts": {phase: f"{phase}.sql" for phase in ("preflight", "apply", "verify", "rollback", "snapshot")},
    }
    payload.update(changes)
    path = root / "change.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_bundle_requires_baseline_and_all_execution_artifacts(tmp_path):
    bundle_path = write_bundle(tmp_path, baseline={})

    with pytest.raises(ChangeBundleError, match="fingerprint"):
        load_bundle(bundle_path, tmp_path)


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
