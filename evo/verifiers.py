"""Proof from outside the tool claim."""

from __future__ import annotations

import sqlite3
from pathlib import Path

FAILURES = {
    'MISSING_CREDENTIAL',
    'PERMISSION_DENIED',
    'TOOL_FAILURE',
    'VERIFICATION_FAILURE',
    'BAD_ASSUMPTION',
    'MISSING_CAPABILITY',
    'EXTERNAL_DEPENDENCY',
    'ENVIRONMENT_FAILURE',
    'PLANNING_FAILURE',
    'UNKNOWN',
}


def db_count(database: Path, table: str, expected: int) -> dict:
    if not table.isidentifier():
        return {'verified': False, 'failure': 'PLANNING_FAILURE', 'reason': 'bad table name'}
    with sqlite3.connect(database) as conn:
        conn.execute(f'CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY, text TEXT)')
        actual = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    verified = actual >= expected
    return {
        'verified': verified,
        'actual': actual,
        'expected': expected,
        'failure': None if verified else 'VERIFICATION_FAILURE',
    }


def classify(reason: str) -> str:
    text = reason.lower()
    if 'credential' in text:
        return 'MISSING_CREDENTIAL'
    if 'permission' in text or 'denied' in text:
        return 'PERMISSION_DENIED'
    if 'count' in text or 'verif' in text:
        return 'VERIFICATION_FAILURE'
    return 'UNKNOWN' if reason else 'UNKNOWN'
