"""Run a Python file in the scratch workspace and record the result."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from evo.coder import write_source


def run_sandbox(work: Path, relative: str, source: str) -> dict:
    path = write_source(work, relative, source)
    if not path['ok']:
        return path
    folder = Path(work) / 'coding-workspace'
    try:
        run = subprocess.run([sys.executable, relative], cwd=folder, capture_output=True, text=True, timeout=8)
    except subprocess.TimeoutExpired:
        return {'ok': False, 'tool': 'sandbox_run', 'reason': 'timed out'}
    return {'ok': run.returncode == 0, 'tool': 'sandbox_run', 'stdout': run.stdout[-400:], 'stderr': run.stderr[-200:]}
