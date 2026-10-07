"""Run owner Python in a scratch folder. Timeout and no inherited secrets."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path


def run_python(source: str, work: Path, timeout: int = 8) -> dict:
    cleaned = source.strip()
    if not cleaned:
        return {'ok': False, 'tool': 'owner_python', 'reason': 'empty'}
    if len(cleaned) > 4000:
        return {'ok': False, 'tool': 'owner_python', 'reason': 'code is too long'}
    if any(word in cleaned.lower() for word in ('security.vault', 'core.permissions', 'emergency_stop')):
        return {'ok': False, 'tool': 'owner_python', 'reason': 'vault and stop code are blocked'}
    folder = Path(work) / 'python-runs' / uuid.uuid4().hex
    folder.mkdir(parents=True, exist_ok=True)
    script = folder / 'main.py'
    script.write_text(cleaned, encoding='utf-8')
    env = {'PATH': os.environ.get('PATH', ''), 'PYTHONDONTWRITEBYTECODE': '1'}
    try:
        run = subprocess.run(
            [sys.executable, str(script)],
            cwd=folder,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {'ok': False, 'tool': 'owner_python', 'reason': 'timed out', 'folder': str(folder)}
    return {
        'ok': run.returncode == 0,
        'tool': 'owner_python',
        'owner': 'vaishnav',
        'returncode': run.returncode,
        'stdout': run.stdout[-800:],
        'stderr': run.stderr[-400:],
        'folder': str(folder),
    }
