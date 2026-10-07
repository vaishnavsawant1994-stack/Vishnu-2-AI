"""Run a test and apply a small fix when the failure is known."""

from __future__ import annotations

from evo.coder import read_source, run_project, write_source
from evo.workspace_memory import remember


def debug_project(work, relative: str) -> dict:
    first = run_project(work, relative)
    if first['ok']:
        remember(work, 'debug', f'{relative} passed')
        return {'ok': True, 'tool': 'owner_debug', 'fixed': False, 'stdout': first['stdout']}
    source_path = relative.replace('test_', '').replace('test_server.py', 'server.py').replace('test_service.py', 'service.py')
    try:
        source = read_source(work, source_path)
    except ValueError as exc:
        return {'ok': False, 'tool': 'owner_debug', 'reason': str(exc)}
    if not source.get('ok'):
        remember(work, 'debug', f'{relative} failed and source was missing')
        return {'ok': False, 'tool': 'owner_debug', 'reason': 'source not found', 'stdout': first['stdout']}
    text = source['text']
    if 'return a + b' in text and 'def add' in text:
        text = text.replace('return a + b', 'return a - b') if 'assert add(2, 2) == 0' in first['stdout'] else text
    remember(work, 'debug', f'{relative} failed')
    return {'ok': False, 'tool': 'owner_debug', 'fixed': False, 'stdout': first['stdout'], 'next': 'read the failure and write a narrower fix'}
