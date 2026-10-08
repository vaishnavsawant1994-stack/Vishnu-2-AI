"""Apply owner-audited candidate edits inside a run's app directory only."""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path

from evo.rewrite import (
    PROTECTED_FILES, PROTECTED_SEGMENTS, append_audit, digest_file,
    excluded, json_read, now, run_dir,
)


def _safe_target(app_root: Path, relative: str) -> Path:
    text = str(relative)
    parts = text.replace("\\", "/").split("/")
    candidate = Path(text)
    if not text or candidate.is_absolute() or any(p in {"", ".", ".."} for p in parts):
        raise PermissionError("candidate path must be a safe relative path")
    normalized = Path(*parts).as_posix()
    if normalized in PROTECTED_FILES or excluded(Path(normalized)) or any(p.lower() in PROTECTED_SEGMENTS for p in parts):
        raise PermissionError("candidate path is protected")
    root = app_root.resolve()
    target = (root / Path(*parts)).resolve()
    if root not in target.parents:
        raise PermissionError("candidate path escapes the rewrite workspace")
    probe = root
    for part in parts:
        probe = probe / part
        if probe.is_symlink():
            raise PermissionError("candidate path crosses a symlink")
    return target


def apply_candidate(run_id: str, changes, *, data_dir: Path | None = None) -> dict:
    root = run_dir(data_dir, run_id).resolve()
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        return {"state": "BLOCKED", "reason": "rewrite run not found"}
    manifest = json_read(manifest_path)
    if manifest.get("state") != "OPEN":
        return {"state": "BLOCKED", "reason": "candidate workspace is not open"}
    if isinstance(changes, dict) and any(k in changes for k in ("promoted", "promotion", "state")):
        return {"state": "SECURITY_FAILURE", "reason": "candidate cannot set owner state"}
    items = list(changes.items()) if isinstance(changes, dict) else [
        (item.get("path"), item) for item in changes
    ]
    prepared = []
    app_root = root / "app"
    for relative, value in items:
        content = value.get("content") if isinstance(value, dict) else value
        reason = str(value.get("reason") or "").strip() if isinstance(value, dict) else ""
        if not reason or not isinstance(content, str):
            return {"state": "BLOCKED", "reason": "each UTF-8 write needs a reason"}
        try:
            target = _safe_target(app_root, str(relative))
        except (ValueError, PermissionError) as exc:
            append_audit(data_dir, {"action": "candidate_write_refused", "run_id": run_id, "path": str(relative), "reason": str(exc)})
            return {"state": "SECURITY_FAILURE", "reason": str(exc), "path": str(relative)}
        prepared.append((str(relative), target, content, reason))
    # Validate every path before the first mutation, so a refused vault path
    # cannot leave earlier writes partially applied.
    records = []
    for relative, target, content, reason in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        old_hash = digest_file(target) if target.is_file() else None
        temporary = target.with_name(f".{target.name}.{uuid.uuid4().hex}.tmp")
        with temporary.open("x", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        new_hash = digest_file(target)
        record = {"path": Path(relative).as_posix(), "old_hash": old_hash, "new_hash": new_hash, "reason": reason, "at": now()}
        records.append(record)
        with (root / "write-log.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    append_audit(data_dir, {"action": "candidate_changed", "run_id": run_id, "writes": records})
    return {"state": "OPEN", "writes": records, "promoted": False}
