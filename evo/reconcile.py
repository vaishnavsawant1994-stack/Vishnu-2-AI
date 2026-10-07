"""Check the outside state of an interrupted step before planning again."""

from __future__ import annotations

import sqlite3
from pathlib import Path

STATES = ('APPLIED', 'NOT_APPLIED', 'PARTIALLY_APPLIED', 'UNKNOWN', 'CONFLICTED')


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
    return provider_status(kind)
