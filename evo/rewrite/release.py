"""Non-production staging, canary gates, owner promotion, and verified rollback."""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

from evo.rewrite import (
    append_audit, baseline_dir, data_root, digest_file, json_read, json_write,
    run_dir, tree_hashes,
)
from security.rewrite_owner import _PROMOTION_AUTHORITY


def _release_path(root: Path) -> Path:
    return root / "release.json"


def _read_release(root: Path) -> dict:
    path = _release_path(root)
    return json_read(path) if path.exists() else {"state": "QUALIFIED"}


def _write_release(root: Path, value: dict) -> None:
    json_write(_release_path(root), value)


def stage(run_id: str, *, data_dir: Path | None = None) -> dict:
    data_dir = data_root(data_dir)
    root = run_dir(data_dir, run_id)
    manifest = json_read(root / "manifest.json")
    if manifest.get("state") != "QUALIFIED":
        return {"state": "REJECTED", "reason": "only qualified runs can be staged"}
    target_env = os.environ.get("VISHNU_REWRITE_STAGING_ROOT", "").strip()
    if not target_env:
        return {"state": "BLOCKED", "reason": "non-production staging host is not configured"}
    target_root = Path(target_env).resolve()
    app_target = target_root / str(run_id)
    if target_root == data_dir.resolve() or data_dir.resolve() in target_root.parents:
        return {"state": "SECURITY_FAILURE", "reason": "staging host overlaps private data"}
    shutil.rmtree(app_target, ignore_errors=True)
    shutil.copytree(root / "app", app_target)
    release = {
        "state": "STAGING",
        "run_id": run_id,
        "baseline_id": manifest["baseline_id"],
        "baseline_sha": json_read(baseline_dir(data_dir, manifest["baseline_id"]) / "manifest.json")["git_sha"],
        "candidate_hashes": tree_hashes(app_target),
        "staging_path": str(app_target),
        "canary_started_at": None,
        "canary_window_seconds": int(os.environ.get("VISHNU_REWRITE_CANARY_SECONDS", "1800")),
        "canary_metrics": None,
        "running_sha": None,
    }
    _write_release(root, release)
    append_audit(data_dir, {"action": "rewrite_staged", "run_id": run_id, "path": str(app_target)})
    return release


def canary(run_id: str, *, data_dir: Path | None = None) -> dict:
    data_dir = data_root(data_dir)
    root = run_dir(data_dir, run_id)
    release = _read_release(root)
    if release.get("state") != "STAGING":
        return {"state": "REJECTED", "reason": "run is not staged"}
    if not Path(release["staging_path"]).is_dir():
        return {"state": "REJECTED", "reason": "staging tree is missing"}
    release["state"] = "CANARY"
    release["canary_started_at"] = time.time()
    release["canary_metrics"] = None
    _write_release(root, release)
    append_audit(data_dir, {"action": "rewrite_canary_started", "run_id": run_id})
    return release


def _record_canary(run_id: str, metrics: dict, *, authority, data_dir: Path | None = None) -> dict:
    if authority is not _PROMOTION_AUTHORITY:
        return {"state": "BLOCKED", "reason": "owner-kernel authority required"}
    data_dir = data_root(data_dir)
    root = run_dir(data_dir, run_id)
    release = _read_release(root)
    if release.get("state") != "CANARY":
        return {"state": "REJECTED", "reason": "canary is not active"}
    release["canary_metrics"] = metrics
    _write_release(root, release)
    append_audit(data_dir, {"action": "canary_metrics", "run_id": run_id, "metrics": metrics})
    return {"state": "CANARY", "metrics": metrics}


def _promote(run_id: str, *, authority, data_dir: Path | None = None) -> dict:
    if authority is not _PROMOTION_AUTHORITY:
        return {"state": "BLOCKED", "reason": "only the owner kernel can promote"}
    data_dir = data_root(data_dir)
    root = run_dir(data_dir, run_id)
    release = _read_release(root)
    if release.get("state") != "CANARY":
        return {"state": "REJECTED", "reason": "run has not completed the canary stage"}
    metrics = release.get("canary_metrics") or {}
    elapsed = time.time() - float(release.get("canary_started_at") or 0)
    if elapsed < int(release.get("canary_window_seconds") or 1800):
        return {"state": "BLOCKED", "reason": "canary window is still running"}
    if not metrics.get("healthy") or metrics.get("stop_active") or float(metrics.get("error_rate", 1)) > 0.01:
        return {"state": "REJECTED", "reason": "canary health or Stop gate failed"}
    release["state"] = "PRODUCTION"
    release["running_sha"] = "candidate:" + str(run_id)
    release["promoted_at"] = time.time()
    _write_release(root, release)
    append_audit(data_dir, {"action": "rewrite_promoted", "run_id": run_id})
    return release


def promote(run_id: str, *, data_dir: Path | None = None) -> dict:
    """Candidate-facing entrypoint. Deliberately has no owner authority."""
    return _promote(run_id, authority=None, data_dir=data_dir)


def rollback(run_id: str, *, data_dir: Path | None = None) -> dict:
    data_dir = data_root(data_dir)
    root = run_dir(data_dir, run_id)
    release = _read_release(root)
    if release.get("state") not in {"STAGING", "CANARY", "PRODUCTION"}:
        return {"state": "REJECTED", "reason": "no staged release to roll back"}
    baseline_id = release["baseline_id"]
    baseline_manifest = json_read(baseline_dir(data_dir, baseline_id) / "manifest.json")
    staging_path = Path(release["staging_path"]).resolve()
    source = baseline_dir(data_dir, baseline_id) / "app"
    shutil.rmtree(staging_path, ignore_errors=True)
    shutil.copytree(source, staging_path)
    restored_hashes = tree_hashes(staging_path)
    expected_hashes = baseline_manifest["file_hashes"]
    verified = restored_hashes == expected_hashes and release["baseline_sha"] == baseline_manifest["git_sha"]
    release["state"] = "STAGING"
    release["active_tree"] = "baseline"
    release["running_sha"] = baseline_manifest["git_sha"] if verified else None
    release["rollback_verified"] = bool(verified)
    release["rollback_at"] = time.time()
    _write_release(root, release)
    append_audit(data_dir, {"action": "rewrite_rollback", "run_id": run_id, "verified": bool(verified), "running_sha": release["running_sha"]})
    if not verified:
        return {"state": "SECURITY_FAILURE", "reason": "frozen baseline SHA or tree hash did not verify"}
    return {"state": "STAGING", "rollback_verified": True, "running_sha": release["running_sha"], "tree_hashes_match": True}
