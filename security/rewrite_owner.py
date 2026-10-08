"""Owner-kernel-only authority for rewrite release controls.

This module is excluded from candidate copies. Never expose this object through a
tool schema, environment variable, manifest, or candidate workspace.
"""
from __future__ import annotations

from pathlib import Path

from evo.rewrite import append_audit, json_read, json_write, run_dir

_PROMOTION_AUTHORITY = object()


def owner_promote(run_id: str, *, data_dir: Path | None = None) -> dict:
    from evo.rewrite.release import _promote
    return _promote(run_id, authority=_PROMOTION_AUTHORITY, data_dir=data_dir)


def owner_record_canary(run_id: str, *, healthy: bool, error_rate: float, stop_active: bool, data_dir: Path | None = None) -> dict:
    from evo.rewrite.release import _record_canary
    return _record_canary(
        run_id, {"healthy": bool(healthy), "error_rate": float(error_rate), "stop_active": bool(stop_active)},
        authority=_PROMOTION_AUTHORITY, data_dir=data_dir,
    )
