"""Write a small skill, test it in a subprocess, and keep it only if it passes.

This is an original Vishnu-2 mechanism. It does not include or adapt another
assistant's source. A skill cannot import Vishnu security modules.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

BANNED = ('security', 'core.permissions', 'tools.registry', 'learning.engine', 'os.system', 'subprocess')


def _safe_name(goal: str) -> str:
    letters = ''.join(ch.lower() if ch.isalnum() else '_' for ch in goal).strip('_')
    return (letters or 'skill')[:40]


def _source(name: str, goal: str) -> str:
    title = json.dumps(goal[:160])
    return (
        'def run(payload):\n'
        f'    """Skill {name}: {goal[:80]}"""\n'
        '    text = str(payload.get("text") or "")\n'
        f'    return {{"ok": True, "skill": "{name}", "goal": {title}, "echo": text[:200]}}\n'
    )


def _check(source: str) -> None:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ValueError('a forged skill cannot import other modules')
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'exec', 'eval', '__import__'}:
            raise ValueError('a forged skill cannot execute arbitrary code')
    lowered = source.lower()
    if any(word in lowered for word in BANNED):
        raise ValueError('a forged skill cannot reach the stop switch or vault')


def forge(goal: str, root: Path) -> dict:
    name = _safe_name(goal)
    source = _source(name, goal)
    _check(source)
    folder = Path(root) / 'skills' / 'forged'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f'{name}.py'
    path.write_text(source, encoding='utf-8')
    probe = (
        'import importlib.util, json, sys\n'
        f'path = {str(path)!r}\n'
        'spec = importlib.util.spec_from_file_location("forged", path)\n'
        'mod = importlib.util.module_from_spec(spec)\n'
        'spec.loader.exec_module(mod)\n'
        'print(json.dumps(mod.run({"text": "ping"})))\n'
    )
    run = subprocess.run([sys.executable, '-c', probe], capture_output=True, text=True, timeout=8)
    if run.returncode != 0:
        path.unlink(missing_ok=True)
        raise RuntimeError(run.stderr.strip() or 'skill test failed')
    result = json.loads(run.stdout.strip())
    return {'name': name, 'path': str(path), 'tested': True, 'sample': result}
