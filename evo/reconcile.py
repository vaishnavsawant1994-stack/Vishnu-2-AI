"""Check the outside state of an interrupted step before planning again."""

from __future__ import annotations

import sqlite3
from pathlib import Path

STATES = ('APPLIED', 'NOT_APPLIED', 'PARTIALLY_APPLIED', 'IN_PROGRESS', 'CONFLICTED', 'UNKNOWN')


def file_write(path: Path, expected_text: str = '') -> dict:
    if not path.exists():
        return {'state': 'NOT_APPLIED', 'provider': 'filesystem'}
    if expected_text and expected_text not in path.read_text(encoding='utf-8', errors='replace'):
        return {'state': 'CONFLICTED', 'provider': 'filesystem'}
    return {'state': 'APPLIED', 'provider': 'filesystem'}


def database_write(database: Path, table: str, expected: int) -> dict:
    if not database.exists() or not table.isidentifier():
        return {'state': 'NOT_APPLIED', 'provider': 'sqlite'}
    with sqlite3.connect(database) as conn:
        actual = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    if actual >= expected:
        return {'state': 'APPLIED', 'provider': 'sqlite', 'actual': actual}
    if actual == 0:
        return {'state': 'NOT_APPLIED', 'provider': 'sqlite', 'actual': actual}
    return {'state': 'PARTIALLY_APPLIED', 'provider': 'sqlite', 'actual': actual}


def provider_status(name: str) -> dict:
    return {'state': 'UNKNOWN', 'provider': name, 'reason': 'no live provider query is configured'}


def reconcile(kind: str, target: str, expected: str = '') -> dict:
    if kind == 'file_write':
        return file_write(Path(target), expected)
    if kind == 'database_write':
        table, count = expected.split(':', 1)
        return database_write(Path(target), table, int(count))
    if kind == 'github_pr':
        owner, repo, head = (expected.split(':', 2) + ['', '', ''])[:3]
        return github_pr(owner, repo, head, target)
    return provider_status(kind)


def github_pr(owner: str, repo: str, head: str, token: str = '', base: str = '', sha: str = '') -> dict:
    """Ask GitHub whether a matching pull request exists. No token means unknown."""
    if not token:
        return {'state': 'UNKNOWN', 'provider': 'github', 'reason': 'no token', 'retry_safe': False}
    import json
    import urllib.request
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls?state=open&per_page=20'
    request = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json', 'User-Agent': 'vishnu-2'})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            pulls = json.loads(response.read().decode('utf-8'))
    except Exception as exc:
        return {'state': 'UNKNOWN', 'provider': 'github', 'reason': str(exc)[:120], 'retry_safe': False}
    for pull in pulls:
        ref = str(pull.get('head', {}).get('ref', ''))
        if ref != head:
            continue
        observed_base = str(pull.get('base', {}).get('ref', ''))
        observed_sha = str(pull.get('head', {}).get('sha', ''))
        if (base and observed_base != base) or (sha and observed_sha != sha):
            return {'state': 'CONFLICTED', 'provider': 'github', 'external_id': pull.get('number'), 'retry_safe': False}
        return {'state': 'APPLIED', 'provider': 'github', 'external_id': pull.get('number'), 'retry_safe': False}
    return {'state': 'NOT_APPLIED', 'provider': 'github', 'retry_safe': True}


def deployment(expected_sha: str, observed: dict | None) -> dict:
    """Classify a deployment observation. A missing query stays unknown."""
    if not observed:
        return {'state': 'UNKNOWN', 'provider': 'deployment', 'retry_safe': False}
    if observed.get('sha') != expected_sha:
        return {'state': 'CONFLICTED', 'provider': 'deployment', 'external_id': observed.get('id'), 'retry_safe': False}
    status = str(observed.get('status', '')).lower()
    if status in {'building', 'queued'}:
        return {'state': 'IN_PROGRESS', 'provider': 'deployment', 'external_id': observed.get('id'), 'retry_safe': False}
    if status in {'healthy', 'success'}:
        return {'state': 'APPLIED', 'provider': 'deployment', 'external_id': observed.get('id'), 'retry_safe': False}
    return {'state': 'UNKNOWN', 'provider': 'deployment', 'retry_safe': False}


def next_decision(state: str) -> dict:
    if state == 'APPLIED':
        return {'action': 'continue', 'repeat': False}
    if state == 'NOT_APPLIED':
        return {'action': 'retry', 'repeat': True}
    if state in {'CONFLICTED', 'PARTIALLY_APPLIED'}:
        return {'action': 'replan', 'repeat': False}
    return {'action': 'block', 'repeat': False}
