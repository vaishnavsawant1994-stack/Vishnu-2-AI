"""Remember what the coding workspace built and what failed."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _connect(work: Path) -> sqlite3.Connection:
    path = Path(work) / 'coding-workspace' / 'memory.sqlite3'
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, kind TEXT, text TEXT, created_at TEXT)')
    conn.commit()
    return conn


def remember(work: Path, kind: str, text: str) -> dict:
    with _connect(work) as conn:
        conn.execute(
            'INSERT INTO notes (kind, text, created_at) VALUES (?, ?, ?)',
            (kind[:40], text[:500], datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return {'ok': True, 'tool': 'workspace_memory'}


def recall(work: Path, limit: int = 8) -> dict:
    with _connect(work) as conn:
        rows = conn.execute('SELECT kind, text, created_at FROM notes ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    return {'ok': True, 'tool': 'workspace_memory', 'notes': [dict(row) for row in rows]}
