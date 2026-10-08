"""Create a data-free candidate workspace from a frozen baseline."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from evo.rewrite import (
    actual_isolation, append_audit, baseline_dir, copy_application,
    data_root, isolation_satisfied, json_read, json_write, make_read_only,
    now, required_isolation, run_dir,
)


def _stop_active(data_dir: Path) -> bool:
    """Read the same durable emergency-stop flag used by ToolRegistry."""
    import sqlite3
    db = Path(data_dir) / "runtime-controls.sqlite3"
    if not db.is_file():
        return False
    try:
        with sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=1) as conn:
            row = conn.execute(
                "SELECT value FROM runtime_controls WHERE key='emergency_stop'"
            ).fetchone()
        return bool(row and str(row[0]) == "1")
    except (OSError, sqlite3.Error):
        # If the stop state cannot be read, fail closed.
        return True

def open_rewrite(data_dir: Path, baseline_id: str) -> dict:
    data_dir = data_root(data_dir)
    baseline = baseline_dir(data_dir, baseline_id)
    manifest_path = baseline / "manifest.json"
    if not manifest_path.is_file():
        return {"state": "BLOCKED", "reason": "frozen baseline does not exist"}
    manifest = json_read(manifest_path)
    if manifest.get("frozen") is not True:
        return {"state": "BLOCKED", "reason": "baseline is not frozen"}
    if _stop_active(data_dir):
        return {"state": "STOPPED", "reason": "Stop is active"}
    required, actual = required_isolation(), actual_isolation()
    if not isolation_satisfied(required, actual):
        return {"state": "INSUFFICIENT_ISOLATION", "required_isolation": required, "actual_isolation": actual}
    run_id = uuid.uuid4().hex
    root = run_dir(data_dir, run_id)
    root.mkdir(parents=True, exist_ok=False)
    try:
        copy_application(baseline / "app", root / "app")
        # Stop, owner identity, permissions, vault, and qualification state live
        # outside app. Candidate tools can only address the app subtree.
        owner_state = root / "owner-state.json"
        json_write(owner_state, {"stop_active": False, "baseline_id": baseline_id}, exclusive=True)
        owner_state.chmod(0o444)
        run_manifest = {
            "run_id": run_id, "baseline_id": baseline_id, "state": "OPEN",
            "required_isolation": required, "actual_isolation": actual,
            "application_hashes": manifest["file_hashes"], "created_at": now(),
            "promoted": False,
        }
        json_write(root / "manifest.json", run_manifest, exclusive=True)
        append_audit(data_dir, {"action": "rewrite_opened", "run_id": run_id, "baseline_id": baseline_id, "required_isolation": required, "actual_isolation": actual})
        return {"state": "OPEN", **run_manifest}
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise
