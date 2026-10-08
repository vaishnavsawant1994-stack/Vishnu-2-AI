"""Private Postgres persistence for vetted skill artifacts.

This store is server-side only. Never expose DATABASE_URL to a browser.
"""
from __future__ import annotations

import hashlib
import os


def configured() -> bool:
    return bool(os.environ.get("PERSONAL_AI_SKILL_DATABASE_URL", "").strip())


def get_or_qualify(skill_id: str, source: str, qualify) -> bool:
    """Return True only if this process inserted the vetted skill.

    An existing row must match the audited source exactly; failures never
    silently fall back to an ephemeral local copy.
    """
    url = os.environ.get("PERSONAL_AI_SKILL_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("private skill database is not configured")
    import psycopg

    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    with psycopg.connect(url, connect_timeout=8, sslmode="require") as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT source, sha256 FROM vishnu_private.qualified_skills "
                    "WHERE skill_id = %s FOR UPDATE",
                    (skill_id,),
                )
                existing = cur.fetchone()
                if existing is not None:
                    if existing[0] != source or existing[1] != digest:
                        raise ValueError("stored skill failed integrity verification")
                    return False
                if not qualify(source):
                    raise RuntimeError("candidate failed independent qualification")
                cur.execute(
                    "INSERT INTO vishnu_private.qualified_skills "
                    "(skill_id, source, sha256) VALUES (%s, %s, %s) "
                    "ON CONFLICT (skill_id) DO NOTHING RETURNING skill_id",
                    (skill_id, source, digest),
                )
                inserted = cur.fetchone() is not None
                if not inserted:
                    cur.execute(
                        "SELECT source, sha256 FROM vishnu_private.qualified_skills WHERE skill_id = %s",
                        (skill_id,),
                    )
                    winner = cur.fetchone()
                    if winner != (source, digest):
                        raise ValueError("concurrent stored skill failed integrity verification")
                return inserted
