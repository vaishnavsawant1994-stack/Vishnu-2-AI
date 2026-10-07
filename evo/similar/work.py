"""Task board with comments and an agent roster."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _connect(work: Path) -> sqlite3.Connection:
    path = Path(work) / 'similar.sqlite3'
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        '''CREATE TABLE IF NOT EXISTS tasks (
             id INTEGER PRIMARY KEY, title TEXT, status TEXT, owner TEXT, comments TEXT, created_at TEXT);
           CREATE TABLE IF NOT EXISTS agents (
             id INTEGER PRIMARY KEY, name TEXT, role TEXT, task_id INTEGER);'''
    )
    conn.commit()
    return conn


def create_task(work: Path, title: str, owner: str = 'vishnu') -> dict:
    with _connect(work) as conn:
        cur = conn.execute(
            'INSERT INTO tasks (title, status, owner, comments, created_at) VALUES (?, ?, ?, ?, ?)',
            (title[:160], 'open', owner[:40], '[]', datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return {'ok': True, 'id': cur.lastrowid, 'status': 'open'}


def comment(work: Path, task_id: int, text: str) -> dict:
    with _connect(work) as conn:
        row = conn.execute('SELECT comments FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if row is None:
            return {'ok': False, 'reason': 'task not found'}
        notes = json.loads(row['comments'])
        notes.append({'text': text[:300], 'at': datetime.now(timezone.utc).isoformat()})
        conn.execute('UPDATE tasks SET comments = ? WHERE id = ?', (json.dumps(notes), task_id))
        conn.commit()
    return {'ok': True, 'comments': len(notes)}


def assign(work: Path, name: str, role: str, task_id: int) -> dict:
    with _connect(work) as conn:
        conn.execute('INSERT INTO agents (name, role, task_id) VALUES (?, ?, ?)', (name[:80], role[:80], task_id))
        conn.execute("UPDATE tasks SET status = 'doing' WHERE id = ?", (task_id,))
        conn.commit()
    return {'ok': True, 'name': name, 'task_id': task_id, 'status': 'doing'}
