"""An experiment workspace. It does not inherit the vault and cannot promote itself."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path


def open_sandbox(work: Path, goal: str) -> dict:
    run_id = uuid.uuid4().hex[:12]
    folder = Path(work) / 'sandboxes' / run_id
    folder.mkdir(parents=True)
    (folder / 'workspace').mkdir()
    manifest = {
        'run_id': run_id,
        'goal': goal[:160],
        'filesystem': 'workspace only',
        'vault': 'denied',
        'stop': 'denied',
        'credentials': 'denied',
        'promote': 'qualification required',
    }
    (folder / 'manifest.txt').write_text('\n'.join(f'{key}: {value}' for key, value in manifest.items()), encoding='utf-8')
    return {'ok': True, 'tool': 'sandbox', 'run_id': run_id, 'path': str(folder), 'vault': 'denied'}


def run_in_sandbox(work: Path, run_id: str, source: str) -> dict:
    folder = Path(work) / 'sandboxes' / run_id / 'workspace'
    if not folder.is_dir():
        return {'ok': False, 'reason': 'sandbox not found'}
    if any(word in source.lower() for word in ('vault', 'emergency_stop', 'credentials')):
        return {'ok': False, 'reason': 'sandbox cannot touch vault, stop, or credentials'}
    script = folder / 'main.py'
    script.write_text(source, encoding='utf-8')
    try:
        run = subprocess.run(
            [sys.executable, str(script)],
            cwd=folder,
            env={'PATH': os.environ.get('PATH', ''), 'PYTHONDONTWRITEBYTECODE': '1'},
            capture_output=True,
            text=True,
            timeout=8,
        )
    except subprocess.TimeoutExpired:
        return {'ok': False, 'reason': 'timed out'}
    return {'ok': run.returncode == 0, 'stdout': run.stdout[-400:], 'promoted': False}


def qualify(claimed_better: bool, evidence_better: bool) -> dict:
    promoted = bool(evidence_better)
    return {
        'ok': True,
        'claimed_better': claimed_better,
        'evidence_better': evidence_better,
        'promoted': promoted,
        'reason': 'qualification evidence' if promoted else 'a claim is not proof',
    }
