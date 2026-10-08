"""Freeze an immutable, scored application baseline before candidate runs."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from evo.rewrite import (
    APPLICATION_ROOT, append_audit, baseline_dir, copy_application, data_root,
    json_read, json_write, now, required_isolation,
)
from evo.rewrite.qualify import measure_tree


def freeze_baseline(data_dir: Path, git_sha: str) -> dict:
    data_dir = data_root(data_dir)
    baseline_id = uuid.uuid4().hex
    root = baseline_dir(data_dir, baseline_id)
    root.mkdir(parents=True, exist_ok=False)
    app = root / "app"
    try:
        copy_application(APPLICATION_ROOT, app)
        isolation = __import__("evo.rewrite", fromlist=["actual_isolation"]).actual_isolation()
        # Store the score and security result before any candidate is opened.
        measured = measure_tree(app, isolation)
        manifest = {
            "baseline_id": baseline_id,
            "git_sha": str(git_sha),
            "file_hashes": __import__("evo.rewrite", fromlist=["tree_hashes"]).tree_hashes(app),
            "excluded_paths": ["vault", ".env", "secrets", "data"],
            "test_command": __import__("evo.rewrite", fromlist=["TEST_COMMAND"]).TEST_COMMAND,
            "test_suite_version": __import__("evo.rewrite", fromlist=["TEST_SUITE_VERSION"]).TEST_SUITE_VERSION,
            "security_command": __import__("evo.rewrite", fromlist=["SECURITY_COMMAND"]).SECURITY_COMMAND,
            "security_suite_version": __import__("evo.rewrite", fromlist=["SECURITY_SUITE_VERSION"]).SECURITY_SUITE_VERSION,
            "score": measured["score"],
            "security_result": measured["security"],
            "required_isolation": required_isolation(),
            "actual_isolation": isolation,
            "timestamp": now(),
            "frozen": True,
        }
        json_write(root / "manifest.json", manifest, exclusive=True)
        (root / "manifest.json").chmod(0o444)
        append_audit(data_dir, {"action": "baseline_frozen", "baseline_id": baseline_id, "git_sha": str(git_sha)})
        return manifest
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise
