"""A goal loop. It records the next step. It cannot clear Stop."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _connect(work: Path) -> sqlite3.Connection:
    path = Path(work) / 'mind.sqlite3'
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        '''CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            title TEXT,
            criteria TEXT,
            status TEXT,
            steps TEXT,
            lesson TEXT,
            conversation_id TEXT DEFAULT '',
            created_at TEXT
        )'''
    )
    conn.commit()
    return conn


def start_goal(work: Path, title: str, criteria: list[str], conversation_id: str = '') -> dict:
    checks = [item.strip() for item in criteria if item.strip()]
    if not checks:
        return {'ok': False, 'reason': 'a goal needs completion criteria'}
    with _connect(work) as conn:
        cur = conn.execute(
            'INSERT INTO goals (title, criteria, status, steps, lesson, conversation_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title[:160], json.dumps(checks), 'open', '[]', '', conversation_id[:80], datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return {'ok': True, 'tool': 'mind', 'id': cur.lastrowid, 'status': 'open', 'criteria': checks}


def record_step(work: Path, goal_id: int, hypothesis: str, action: str, result: str, verified: bool) -> dict:
    with _connect(work) as conn:
        row = conn.execute('SELECT steps, criteria FROM goals WHERE id = ?', (goal_id,)).fetchone()
        if row is None:
            return {'ok': False, 'reason': 'goal not found'}
        steps = json.loads(row['steps'])
        steps.append({
            'hypothesis': hypothesis[:240],
            'action': action[:240],
            'result': result[:240],
            'verified': verified,
            'at': datetime.now(timezone.utc).isoformat(),
        })
        lesson = ''
        status = 'open'
        if not verified:
            lesson = f'Do not treat {action[:80]} as complete when verification fails.'
            status = 'learning'
        conn.execute('UPDATE goals SET steps = ?, lesson = ?, status = ? WHERE id = ?', (json.dumps(steps), lesson, status, goal_id))
        conn.commit()
    return {'ok': True, 'tool': 'mind', 'id': goal_id, 'status': status, 'lesson': lesson, 'stop_cleared': False}


def goal_status(work: Path, goal_id: int, met: list[str]) -> dict:
    with _connect(work) as conn:
        row = conn.execute('SELECT title, criteria, lesson FROM goals WHERE id = ?', (goal_id,)).fetchone()
    if row is None:
        return {'ok': False, 'reason': 'goal not found'}
    criteria = json.loads(row['criteria'])
    done = [item for item in criteria if item in met]
    missing = [item for item in criteria if item not in met]
    status = 'complete' if not missing else 'continue'
    return {
        'ok': True,
        'title': row['title'],
        'status': status,
        'met': done,
        'missing': missing,
        'lesson': row['lesson'],
        'complete': status == 'complete',
    }


def mark_blocked(work: Path, goal_id: int, reason: str) -> dict:
    with _connect(work) as conn:
        row = conn.execute('SELECT id FROM goals WHERE id = ?', (goal_id,)).fetchone()
        if row is None:
            return {'ok': False, 'reason': 'goal not found'}
        conn.execute("UPDATE goals SET status = 'blocked', lesson = ? WHERE id = ?", (reason[:240], goal_id))
        conn.commit()
    return {'ok': True, 'tool': 'mind', 'id': goal_id, 'status': 'blocked', 'reason': reason[:240], 'stop_cleared': False}


def active_goal(work: Path, conversation_id: str = '') -> dict | None:
    with _connect(work) as conn:
        try:
            row = conn.execute(
                "SELECT id, title, criteria, lesson, status FROM goals WHERE status IN ('open', 'learning', 'blocked') AND (? = '' OR conversation_id = ?) ORDER BY id DESC LIMIT 1",
                (conversation_id, conversation_id),
            ).fetchone()
        except sqlite3.OperationalError:
            return None
    if row is None:
        return None
    return {'goal_id': row['id'], 'title': row['title'], 'criteria': json.loads(row['criteria']), 'lesson': row['lesson'], 'status': row['status']}
