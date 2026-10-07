"""Project coding tools: read, write, and test inside one workspace."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROTECTED = ('security/', 'core/permissions.py', 'tools/registry.py', '.env', 'vault')


def _root(work: Path) -> Path:
    root = Path(work) / 'coding-workspace'
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def _inside(work: Path, relative: str) -> Path:
    path = (_root(work) / relative).resolve()
    if _root(work) not in path.parents and path != _root(work):
        raise ValueError('path is outside the coding workspace')
    lowered = relative.replace('\\', '/').lower()
    if any(part in lowered for part in PROTECTED):
        raise ValueError('coding agent cannot edit Stop, vault, or secret files')
    return path


def list_project(work: Path) -> dict:
    root = _root(work)
    files = [str(path.relative_to(root)) for path in root.rglob('*') if path.is_file()][:100]
    return {'ok': True, 'tool': 'owner_coder', 'workspace': str(root), 'files': files}


def read_source(work: Path, relative: str) -> dict:
    path = _inside(work, relative)
    if not path.is_file():
        return {'ok': False, 'reason': 'file not found'}
    return {'ok': True, 'tool': 'owner_coder', 'path': relative, 'text': path.read_text(encoding='utf-8', errors='replace')[:8000]}


def write_source(work: Path, relative: str, text: str) -> dict:
    path = _inside(work, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    return {'ok': True, 'tool': 'owner_coder', 'path': relative, 'bytes': len(text.encode('utf-8'))}


def run_project(work: Path, relative: str = '') -> dict:
    root = _root(work)
    target = _inside(work, relative) if relative else root
    try:
        run = subprocess.run([sys.executable, '-m', 'pytest', '-q', str(target)], cwd=root, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {'ok': False, 'tool': 'owner_coder', 'reason': 'tests timed out'}
    return {'ok': run.returncode == 0, 'tool': 'owner_coder', 'stdout': run.stdout[-800:], 'stderr': run.stderr[-400:]}
