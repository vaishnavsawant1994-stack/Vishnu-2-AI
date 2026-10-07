"""Original Vishnu-2 surfaces for the studied GitHub board. No upstream source."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _db(work: Path) -> sqlite3.Connection:
    path = Path(work) / 'board.sqlite3'
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        '''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT, created_at TEXT);
           CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY, name TEXT, role TEXT);
           CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY, text TEXT, created_at TEXT);'''
    )
    conn.commit()
    return conn


def add_task(work: Path, title: str) -> dict:
    with _db(work) as conn:
        cur = conn.execute(
            'INSERT INTO tasks (title, status, created_at) VALUES (?, ?, ?)',
            (title[:160], 'open', datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return {'ok': True, 'tool': 'task_board', 'id': cur.lastrowid, 'title': title[:160]}


def list_tasks(work: Path) -> dict:
    with _db(work) as conn:
        rows = conn.execute('SELECT id, title, status FROM tasks ORDER BY id DESC').fetchall()
    return {'ok': True, 'tasks': [dict(row) for row in rows]}


def add_agent(work: Path, name: str, role: str) -> dict:
    with _db(work) as conn:
        conn.execute('INSERT INTO agents (name, role) VALUES (?, ?)', (name[:80], role[:80]))
        conn.commit()
    return {'ok': True, 'tool': 'agent_roster', 'name': name[:80], 'role': role[:80]}


def retain(work: Path, text: str) -> dict:
    with _db(work) as conn:
        conn.execute(
            'INSERT INTO memory (text, created_at) VALUES (?, ?)',
            (text[:500], datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return {'ok': True, 'tool': 'learned_memory'}


def recall(work: Path, query: str) -> dict:
    with _db(work) as conn:
        rows = conn.execute('SELECT text FROM memory ORDER BY id DESC').fetchall()
    words = set(query.lower().split())
    hits = [row['text'] for row in rows if words & set(row['text'].lower().split())]
    return {'ok': True, 'hits': hits[:5]}


def design_check(text: str) -> dict:
    rules = {
        'has_heading': text.lstrip().startswith('#'),
        'names_the_user_action': 'user' in text.lower() or 'click' in text.lower(),
        'states_the_failure': 'error' in text.lower() or 'fail' in text.lower(),
    }
    return {'ok': all(rules.values()), 'rules': rules}


def storyboard(title: str) -> dict:
    page = f'<!doctype html><html><body><h1>{title[:80]}</h1><p>Storyboard only. No video is rendered.</p></body></html>'
    return {'ok': True, 'tool': 'storyboard', 'html': page, 'rendered_video': False}


def topic_script(topic: str) -> dict:
    return {
        'ok': True,
        'tool': 'topic_script',
        'script': f'A short narration about {topic[:120]}. State the fact, then the next step.',
        'video': False,
    }
