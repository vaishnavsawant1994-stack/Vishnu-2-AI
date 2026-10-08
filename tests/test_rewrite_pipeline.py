"""End-to-end owner-kernel checks for isolated rewrite lifecycle."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

# This is a host-side test. Candidate copies intentionally exclude evo/rewrite.
if not (Path(__file__).resolve().parents[1] / "evo" / "rewrite" / "__init__.py").is_file():
    pytest.skip("owner kernel is not part of candidate application", allow_module_level=True)

import evo.rewrite as rewrite
import evo.rewrite.baseline as baseline_module
import evo.rewrite.candidate as candidate_module
import evo.rewrite.qualify as qualify_module
import evo.rewrite.release as release_module
import evo.rewrite.workspace as workspace_module


def _result(score=10.0, security=True):
    checks = {
        "registry_uniqueness": security,
        "stop_blocks_execution": security,
        "permission_denial_does_not_execute": security,
        "recovery_does_not_repeat": security,
        "phase0_executor": True,
    }
    return {
        "tests_passed": True,
        "tests": {"command": [], "suite_version": "fixture", "ok": True, "stdout": "10 passed", "stderr": "", "duration_seconds": 1},
        "security_passed": security,
        "security": {"passed": security, "suite_version": "fixture", "command_result": {"ok": security}, "phase0_result": {"ok": True}, "checks": checks},
        "score": score,
    }


def test_rewrite_acceptance_isolated_qualification_and_rollback(tmp_path, monkeypatch):
    data_dir = tmp_path / "private-data"
    data_dir.mkdir()
    monkeypatch.setattr(baseline_module, "measure_tree", lambda tree, actual: _result(10.0, True))
    monkeypatch.setattr(rewrite, "actual_isolation", lambda: "CONTAINER")
    monkeypatch.setattr(workspace_module, "actual_isolation", lambda: "CONTAINER")
    monkeypatch.setattr(workspace_module, "_stop_active", lambda data: False)
    monkeypatch.setenv("VISHNU_REWRITE_REQUIRED_ISOLATION", "CONTAINER")

    baseline = baseline_module.freeze_baseline(data_dir, "frozen-git-sha")
    assert baseline["frozen"] is True
    baseline_path = rewrite.baseline_dir(data_dir, baseline["baseline_id"])
    original_manifest = rewrite.json_read(baseline_path / "manifest.json")

    run = workspace_module.open_rewrite(data_dir, baseline["baseline_id"])
    assert run["state"] == "OPEN"
    run_id = run["run_id"]
    app_file = rewrite.run_dir(data_dir, run_id) / "app" / "README.md"
    if not app_file.exists():
        app_file = rewrite.run_dir(data_dir, run_id) / "app" / "pyproject.toml"
    original_source = (rewrite.APPLICATION_ROOT / app_file.relative_to(rewrite.run_dir(data_dir, run_id) / "app")).read_bytes()
    changed = candidate_module.apply_candidate(
        run_id, {app_file.relative_to(rewrite.run_dir(data_dir, run_id) / "app").as_posix(): {"content": "candidate edit\n", "reason": "acceptance fixture"}},
        data_dir=data_dir,
    )
    assert changed["state"] == "OPEN"
    assert app_file.read_text() == "candidate edit\n"
    assert (rewrite.APPLICATION_ROOT / app_file.relative_to(rewrite.run_dir(data_dir, run_id) / "app")).read_bytes() == original_source

    vault_refusal = candidate_module.apply_candidate(
        run_id, {"vault/credentials.json": {"content": "secret", "reason": "must be refused"}}, data_dir=data_dir,
    )
    assert vault_refusal["state"] == "SECURITY_FAILURE"
    assert app_file.read_text() == "candidate edit\n"

    # Lower score rejects and removes the run.
    sequence = {"n": 0}
    def lower_measure(tree, actual):
        sequence["n"] += 1
        return _result(10.0 if sequence["n"] % 2 else 9.0, True)
    monkeypatch.setattr(qualify_module, "measure_tree", lower_measure)
    lower = qualify_module.qualify_rewrite(baseline["baseline_id"], run_id, data_dir=data_dir)
    assert lower["state"] == "REJECTED"
    assert not rewrite.run_dir(data_dir, run_id).exists()

    # A security failure rejects even when the test score is higher.
    run2 = workspace_module.open_rewrite(data_dir, baseline["baseline_id"])
    assert run2["state"] == "OPEN"
    candidate_module.apply_candidate(run2["run_id"], {"README.md": {"content": "better\n", "reason": "fixture"}}, data_dir=data_dir)
    sequence["n"] = 0
    def insecure_measure(tree, actual):
        sequence["n"] += 1
        return _result(10.0 if sequence["n"] % 2 else 11.0, sequence["n"] % 2 == 1)
    monkeypatch.setattr(qualify_module, "measure_tree", insecure_measure)
    insecure = qualify_module.qualify_rewrite(baseline["baseline_id"], run2["run_id"], data_dir=data_dir)
    assert insecure["state"] == "REJECTED"
    assert not rewrite.run_dir(data_dir, run2["run_id"]).exists()

    # A passing candidate is qualified only; no candidate-facing production path exists.
    run3 = workspace_module.open_rewrite(data_dir, baseline["baseline_id"])
    assert run3["state"] == "OPEN"
    candidate_module.apply_candidate(run3["run_id"], {"README.md": {"content": "better\n", "reason": "fixture"}}, data_dir=data_dir)
    sequence["n"] = 0
    def passing_measure(tree, actual):
        sequence["n"] += 1
        return _result(10.0 if sequence["n"] % 2 else 11.0, True)
    monkeypatch.setattr(qualify_module, "measure_tree", passing_measure)
    qualified = qualify_module.qualify_rewrite(baseline["baseline_id"], run3["run_id"], data_dir=data_dir)
    assert qualified["state"] == "QUALIFIED"
    assert rewrite.json_read(rewrite.run_dir(data_dir, run3["run_id"]) / "manifest.json")["state"] == "QUALIFIED"
    assert release_module.promote(run3["run_id"], data_dir=data_dir)["state"] == "BLOCKED"

    # Stage is explicitly non-production; rollback verifies frozen hashes and SHA.
    staging = tmp_path / "staging-host"
    monkeypatch.setenv("VISHNU_REWRITE_STAGING_ROOT", str(staging))
    monkeypatch.setenv("VISHNU_REWRITE_STAGING_ROLE", "non-production")
    staged = release_module.stage(run3["run_id"], data_dir=data_dir)
    assert staged["state"] == "STAGING"
    restored = release_module.rollback(run3["run_id"], data_dir=data_dir)
    assert restored["rollback_verified"] is True
    assert restored["running_sha"] == "frozen-git-sha"
    assert restored["tree_hashes_match"] is True
    assert rewrite.json_read(baseline_path / "manifest.json") == original_manifest

    # Candidate cannot edit Stop controls, and active Stop blocks opening a run.
    run4 = workspace_module.open_rewrite(data_dir, baseline["baseline_id"])
    assert run4["state"] == "OPEN"
    blocked = candidate_module.apply_candidate(run4["run_id"], {"security/stop.py": {"content": "pass", "reason": "attack"}}, data_dir=data_dir)
    assert blocked["state"] == "SECURITY_FAILURE"
    monkeypatch.setattr(workspace_module, "_stop_active", lambda data: True)
    assert workspace_module.open_rewrite(data_dir, baseline["baseline_id"])["state"] == "STOPPED"
