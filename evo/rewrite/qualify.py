"""Qualify baseline and candidate with pinned checks in a networkless container."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from evo.rewrite import (
    PHASE0_COMMAND, SECURITY_COMMAND, SECURITY_SUITE_VERSION, TEST_COMMAND,
    TEST_SUITE_VERSION, actual_isolation, append_audit, baseline_dir,
    data_root, digest_file, excluded, isolation_satisfied, json_read, now,
    run_dir, tree_hashes,
)


def _container_run(tree: Path, command: list[str], actual: str, *, timeout: int = 900) -> dict:
    if actual != "CONTAINER":
        return {"ok": False, "returncode": 125, "stdout": "", "stderr": "container isolation is unavailable", "duration_seconds": 0.0}
    docker = shutil.which("docker")
    image = os.environ.get("VISHNU_REWRITE_CONTAINER_IMAGE", "").strip()
    if not docker or not image:
        return {"ok": False, "returncode": 125, "stdout": "", "stderr": "container image is not configured", "duration_seconds": 0.0}
    owner_root = Path(__file__).resolve().parents[2]
    mounts = []
    for source, target in (
        (Path(__file__).resolve().parent, "/owner-kernel/rewrite"),
        (owner_root / "security", "/owner-kernel/security"),
        (owner_root / "tools", "/owner-kernel/tools"),
        (owner_root / "core", "/owner-kernel/core"),
        (owner_root / "desktop", "/owner-kernel/desktop"),
    ):
        if source.exists():
            mounts.extend(["-v", f"{source.resolve()}:{target}:ro"])
    args = [
        docker, "run", "--rm", "--network=none", "--read-only",
        "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--pids-limit=128", "--memory=2g", "--cpus=2",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=512m",
        "-e", "TMPDIR=/tmp", "-e", "PYTHONDONTWRITEBYTECODE=1",
        "-e", "PYTHONPATH=/owner-kernel/rewrite:/workspace:/owner-kernel",
        "-v", f"{Path(tree).resolve()}:/workspace:ro", *mounts,
        "-w", "/workspace", image, *command,
    ]
    started = time.monotonic()
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return {
            "ok": result.returncode == 0, "returncode": result.returncode,
            "stdout": result.stdout[-40000:], "stderr": result.stderr[-12000:],
            "duration_seconds": time.monotonic() - started,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "returncode": 124, "stdout": "", "stderr": str(exc), "duration_seconds": time.monotonic() - started}


def _score(test_result: dict) -> float:
    output = str(test_result.get("stdout", "")) + "\n" + str(test_result.get("stderr", ""))
    passed_match = re.search(r"(\d+) passed", output)
    failed_match = re.search(r"(\d+) failed", output)
    passed = int(passed_match.group(1)) if passed_match else 0
    failed = int(failed_match.group(1)) if failed_match else (0 if test_result.get("ok") else 1)
    # Pass count is the primary score; verified runtime is the tie-breaker.
    duration = float(test_result.get("duration_seconds", 0.0))
    return round(float(passed - failed * 1000 - duration / 1000000), 6)


def _secret_findings(before: dict[str, str], candidate_root: Path) -> list[str]:
    findings = []
    patterns = [
        ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
        ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        ("token-assignment", re.compile(r"(?i)(?:api[_-]?key|access[_-]?token|secret)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{24,}")),
    ]
    for relative, new_hash in tree_hashes(candidate_root).items():
        if before.get(relative) == new_hash:
            continue
        path = candidate_root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        for label, pattern in patterns:
            if pattern.search(text):
                findings.append(f"{relative}:{label}")
    return findings


def _path_escape_findings(root: Path) -> list[str]:
    root = Path(root).resolve()
    findings = []
    app = root / "app"
    for path in app.rglob("*"):
        if path.is_symlink():
            findings.append(path.relative_to(app).as_posix())
            continue
        resolved = path.resolve()
        if resolved != app and app not in resolved.parents:
            findings.append(path.relative_to(app).as_posix())
    return findings


def measure_tree(tree: Path, actual: str) -> dict:
    tests = _container_run(tree, TEST_COMMAND, actual)
    phase0 = _container_run(tree, PHASE0_COMMAND, actual)
    security = _container_run(tree, SECURITY_COMMAND, actual)
    security_result = {
        "passed": bool(security.get("ok") and phase0.get("ok")),
        "suite_version": SECURITY_SUITE_VERSION,
        "command_result": security,
        "phase0_result": phase0,
        "checks": {
            "registry_uniqueness": bool(security.get("ok")),
            "stop_blocks_execution": bool(security.get("ok")),
            "permission_denial_does_not_execute": bool(security.get("ok")),
            "recovery_does_not_repeat": bool(security.get("ok")),
            "phase0_executor": bool(phase0.get("ok")),
        },
    }
    return {
        "tests_passed": bool(tests.get("ok")),
        "tests": {"command": TEST_COMMAND, "suite_version": TEST_SUITE_VERSION, **tests},
        "security_passed": security_result["passed"],
        "security": security_result,
        "score": _score(tests),
    }


def qualify_rewrite(baseline_id: str, run_id: str, *, data_dir: Path | None = None) -> dict:
    data_dir = data_root(data_dir)
    baseline_path = baseline_dir(data_dir, baseline_id)
    run_path = run_dir(data_dir, run_id)
    try:
        baseline = json_read(baseline_path / "manifest.json")
        run_manifest = json_read(run_path / "manifest.json")
    except (OSError, ValueError):
        return {"state": "REJECTED", "reason": "baseline or run manifest is missing"}
    if baseline.get("frozen") is not True or run_manifest.get("baseline_id") != baseline_id:
        return {"state": "REJECTED", "reason": "baseline binding is invalid"}
    if run_manifest.get("state") != "OPEN":
        return {"state": "REJECTED", "reason": "rewrite run is not open"}
    required = str(run_manifest.get("required_isolation", "CONTAINER"))
    actual = actual_isolation()
    if not isolation_satisfied(required, actual) or actual != "CONTAINER":
        return {"state": "INSUFFICIENT_ISOLATION", "required_isolation": required, "actual_isolation": actual}

    baseline_app = baseline_path / "app"
    candidate_app = run_path / "app"
    expected_baseline = baseline.get("file_hashes", {})
    baseline_now = tree_hashes(baseline_app)
    if baseline_now != expected_baseline:
        append_audit(data_dir, {"action": "baseline_tamper_detected", "baseline_id": baseline_id})
        return {"state": "SECURITY_FAILURE", "reason": "frozen baseline hash mismatch"}

    before = run_manifest.get("application_hashes", {})
    baseline_result = measure_tree(baseline_app, actual)
    candidate_result = measure_tree(candidate_app, actual)
    secrets = _secret_findings(before, candidate_app)
    escapes = _path_escape_findings(run_path)
    security_passed = bool(candidate_result["security_passed"] and not secrets and not escapes)
    failures = []
    if not candidate_result["tests_passed"]:
        failures.append("unit tests")
    if not candidate_result["security"]["checks"]["phase0_executor"]:
        failures.append("tests/test_phase0_executor.py")
    for check in ("registry_uniqueness", "stop_blocks_execution", "permission_denial_does_not_execute", "recovery_does_not_repeat"):
        if not candidate_result["security"]["checks"][check]:
            failures.append(check)
    if secrets:
        failures.append("secret scan")
    if escapes:
        failures.append("path escape")
    if baseline_result["tests_passed"] and not candidate_result["tests_passed"]:
        failures.append("regression")
    baseline_score = float(baseline.get("score", 0))
    candidate_score = float(candidate_result["score"])
    isolation_ok = isolation_satisfied(required, actual)
    result = {
        "baseline_id": baseline_id,
        "run_id": run_id,
        "baseline_score": baseline_score,
        "candidate_score": candidate_score,
        "security_passed": security_passed,
        "required_isolation": required,
        "actual_isolation": actual,
        "regressions": failures,
        "baseline_tests": baseline_result["tests"],
        "candidate_tests": candidate_result["tests"],
        "security": {
            **candidate_result["security"],
            "secret_findings": secrets,
            "path_escape_findings": escapes,
        },
        "isolation_satisfied": isolation_ok,
        "qualified_at": now(),
    }
    accepted = (
        isolation_ok and security_passed and not failures
        and candidate_result["tests_passed"]
        and candidate_score > baseline_score
        and candidate_result["security"]["checks"]["stop_blocks_execution"]
        and candidate_result["security"]["checks"]["recovery_does_not_repeat"]
    )
    state = "QUALIFIED" if accepted else "REJECTED"
    result["state"] = state
    if accepted:
        run_manifest["state"] = "QUALIFIED"
        run_manifest["qualification"] = result
        from evo.rewrite import json_write
        json_write(run_path / "manifest.json", run_manifest)
        json_write(run_path / "qualification.json", result, exclusive=True)
        append_audit(data_dir, {"action": "rewrite_qualified", "run_id": run_id, "baseline_id": baseline_id})
    else:
        append_audit(data_dir, {"action": "rewrite_rejected", "run_id": run_id, "baseline_id": baseline_id, "failures": failures})
        shutil.rmtree(run_path, ignore_errors=True)
    return result
