"""Run a short Python snippet in a subprocess. It cannot change the stop switch."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

BLOCKED = ('security.vault', 'core.permissions', 'set_emergency_stop', 'tools.registry')


def run_python(source: str, timeout: int = 8) -> dict:
    cleaned = source.strip()[:4000]
    if not cleaned:
        return {'ok': False, 'reason': 'empty'}
    lowered = cleaned.lower()
    if any(word in lowered for word in BLOCKED):
        return {'ok': False, 'reason': 'code cannot reach the stop switch or vault'}
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'snippet.py'
        path.write_text(cleaned, encoding='utf-8')
        try:
            run = subprocess.run(
                [sys.executable, str(path)],
                cwd=folder,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return {'ok': False, 'reason': 'timed out'}
    return {
        'ok': run.returncode == 0,
        'stdout': run.stdout[-1000:],
        'stderr': run.stderr[-500:],
        'tool': 'owner_python',
    }
