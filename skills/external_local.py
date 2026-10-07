"""Call a program the owner already installed. Never clone or copy it."""

from __future__ import annotations

import os
from pathlib import Path


def external_skill(home: str, repo_root: Path) -> dict:
    if not home:
        return {'available': False, 'reason': 'set BRAHMA_HOME to a local checkout you already installed'}
    target = Path(home).expanduser().resolve()
    root = Path(repo_root).resolve()
    if root == target or root in target.parents or target in root.parents and target != root:
        if target == root or str(target).startswith(str(root) + os.sep):
            return {'available': False, 'reason': 'external code cannot live inside the Vishnu-2 repo'}
    if not target.exists():
        return {'available': False, 'reason': 'local checkout was not found'}
    if not (target / 'main.py').exists():
        return {'available': False, 'reason': 'main.py is not in that folder'}
    return {
        'available': True,
        'stored_in_vishnu': False,
        'cloned': False,
        'path': str(target),
        'run': f'python {target / "main.py"}',
    }
