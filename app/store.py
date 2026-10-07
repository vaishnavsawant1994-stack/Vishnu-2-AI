"""SQLite idea ledger."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    seed TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'seed',
    decision TEXT NOT NULL DEFAULT '',
    dissent TEXT NOT NULL DEFAULT '',
    experiment TEXT NOT NULL DEFAULT '',
    council_source TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def add_idea(conn: sqlite3.Connection, title: str, seed: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO ideas (title, seed, created_at) VALUES (?, ?, ?)",
        (title.strip(), seed.strip(), now),
    )
    conn.commit()
    return get_idea(conn, int(cur.lastrowid))


def list_ideas(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM ideas ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


def get_idea(conn: sqlite3.Connection, idea_id: int) -> dict:
    row = conn.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,)).fetchone()
    if row is None:
        raise KeyError(idea_id)
    return dict(row)


def save_council(conn: sqlite3.Connection, idea_id: int, result) -> dict:
    conn.execute(
        """
        UPDATE ideas
        SET status = 'debated',
            decision = ?,
            dissent = ?,
            experiment = ?,
            council_source = ?
        WHERE id = ?
        """,
        (result.decision, result.dissent, result.experiment, result.source, idea_id),
    )
    conn.commit()
    return get_idea(conn, idea_id)


def decide(conn: sqlite3.Connection, idea_id: int, status: str) -> dict:
    if status not in {"decided", "parked"}:
        raise ValueError("status must be decided or parked")
    conn.execute("UPDATE ideas SET status = ? WHERE id = ?", (status, idea_id))
    conn.commit()
    return get_idea(conn, idea_id)
