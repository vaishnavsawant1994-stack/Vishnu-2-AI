"""Call a separately installed local app. Never copy it into this repo."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def external_status(home: str | None, repo_root: Path) -> dict:
    if not home:
        return {'available': False, 'reason': 'set BRAHMA_HOME to a checkout outside this repo'}
    path = Path(home).expanduser().resolve()
    repo = repo_root.resolve()
    if path == repo or repo in path.parents or path in repo.parents:
        return {'available': False, 'reason': 'external app must stay outside this repository'}
    if not path.exists():
        return {'available': False, 'reason': 'path does not exist'}
    return {'available': True, 'path': str(path), 'copied': False}


def run_external(home: str | None, repo_root: Path, args: list[str]) -> dict:
    status = external_status(home, repo_root)
    if not status['available']:
        return status
    if any(arg.startswith('-c') or 'git' == Path(arg).name for arg in args):
        return {'available': True, 'ran': False, 'reason': 'clone and copy commands are refused'}
    try:
        run = subprocess.run(args, cwd=status['path'], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'available': True, 'ran': False, 'error': str(exc)}
    return {'available': True, 'ran': run.returncode == 0, 'output': run.stdout[-500:], 'copied': False}
