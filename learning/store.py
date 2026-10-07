"""SQLite ledger for episodes, lessons, and improvement proposals."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal TEXT NOT NULL,
    plan_json TEXT NOT NULL DEFAULT '[]',
    outcome TEXT NOT NULL,
    tool_name TEXT NOT NULL DEFAULT '',
    detail TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statement TEXT NOT NULL,
    kind TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed',
    source_episode INTEGER,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    change_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed',
    created_at TEXT NOT NULL
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_episode(conn, goal: str, plan: list, outcome: str, tool_name: str = '', detail: str = '') -> int:
    cur = conn.execute(
        "INSERT INTO episodes (goal, plan_json, outcome, tool_name, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (goal.strip()[:1000], json.dumps(plan)[:8000], outcome, tool_name[:120], detail[:1000], now()),
    )
    conn.commit()
    return int(cur.lastrowid)


def add_lesson(conn, statement: str, kind: str, source_episode: int | None, status: str = 'proposed') -> int:
    cur = conn.execute(
        "INSERT INTO lessons (statement, kind, status, source_episode, created_at) VALUES (?, ?, ?, ?, ?)",
        (statement.strip()[:500], kind, status, source_episode, now()),
    )
    conn.commit()
    return int(cur.lastrowid)


def set_lesson_status(conn, lesson_id: int, status: str) -> dict:
    if status not in {'accepted', 'rejected'}:
        raise ValueError('status must be accepted or rejected')
    conn.execute("UPDATE lessons SET status = ? WHERE id = ?", (status, lesson_id))
    conn.commit()
    row = conn.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,)).fetchone()
    if row is None:
        raise KeyError(lesson_id)
    return dict(row)


def accepted_lessons(conn, limit: int = 8) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM lessons WHERE status = 'accepted' ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def add_proposal(conn, title: str, change: dict) -> int:
    cur = conn.execute(
        "INSERT INTO proposals (title, change_json, created_at) VALUES (?, ?, ?)",
        (title[:160], json.dumps(change)[:4000], now()),
    )
    conn.commit()
    return int(cur.lastrowid)
