"""Screen a call, store the transcript, and return a summary."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS calls (
            id TEXT PRIMARY KEY,
            caller TEXT NOT NULL,
            status TEXT NOT NULL,
            transcript TEXT NOT NULL DEFAULT '[]',
            summary TEXT NOT NULL DEFAULT '',
            audio_path TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def start_screen(caller: str, work: Path) -> dict:
    name = ' '.join(caller.split())[:80] or 'unknown'
    call_id = uuid.uuid4().hex[:12]
    with _connect(Path(work) / 'calls.sqlite3') as conn:
        conn.execute(
            "INSERT INTO calls (id, caller, status, created_at) VALUES (?, ?, 'screening', ?)",
            (call_id, name, _now()),
        )
        conn.commit()
    return {
        'ok': True,
        'tool': 'owner_phone',
        'call_id': call_id,
        'caller': name,
        'status': 'screening',
        'answered': True,
        'carrier': False,
    }


def add_line(call_id: str, speaker: str, text: str, work: Path) -> dict:
    if speaker not in {'caller', 'vishnu'}:
        return {'ok': False, 'reason': 'speaker must be caller or vishnu'}
    line = {'speaker': speaker, 'text': ' '.join(text.split())[:400], 'at': _now()}
    with _connect(Path(work) / 'calls.sqlite3') as conn:
        row = conn.execute("SELECT transcript FROM calls WHERE id = ?", (call_id,)).fetchone()
        if row is None:
            return {'ok': False, 'reason': 'call not found'}
        lines = json.loads(row['transcript'])
        lines.append(line)
        conn.execute("UPDATE calls SET transcript = ? WHERE id = ?", (json.dumps(lines), call_id))
        conn.commit()
    return {'ok': True, 'tool': 'owner_phone', 'call_id': call_id, 'lines': len(lines)}


def finish_screen(call_id: str, work: Path) -> dict:
    with _connect(Path(work) / 'calls.sqlite3') as conn:
        row = conn.execute("SELECT * FROM calls WHERE id = ?", (call_id,)).fetchone()
        if row is None:
            return {'ok': False, 'reason': 'call not found'}
        lines = json.loads(row['transcript'])
        summary = _summary(row['caller'], lines)
        conn.execute("UPDATE calls SET status = 'finished', summary = ? WHERE id = ?", (summary, call_id))
        conn.commit()
    return {
        'ok': True,
        'tool': 'owner_phone',
        'call_id': call_id,
        'caller': row['caller'],
        'status': 'finished',
        'transcript': lines,
        'summary': summary,
    }


def _summary(caller: str, lines: list[dict]) -> str:
    if not lines:
        return f'Screened a call from {caller}. No speech was captured.'
    spoken = '; '.join(f"{item['speaker']}: {item['text']}" for item in lines[-4:])
    return f'Screened a call from {caller}. {spoken}'


def capture_audio(call_id: str, work: Path, audio: bytes, seconds: int = 5) -> dict:
    """Store a live audio clip for a screened call. Carrier delivery is separate."""
    if not audio:
        return {'ok': False, 'tool': 'owner_phone', 'reason': 'no audio captured'}
    if len(audio) > 8_000_000:
        return {'ok': False, 'tool': 'owner_phone', 'reason': 'audio clip is too large'}
    folder = Path(work) / 'call-audio'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f'{call_id}.wav'
    path.write_bytes(audio)
    with _connect(Path(work) / 'calls.sqlite3') as conn:
        row = conn.execute("SELECT id FROM calls WHERE id = ?", (call_id,)).fetchone()
        if row is None:
            path.unlink(missing_ok=True)
            return {'ok': False, 'reason': 'call not found'}
        try:
            conn.execute("UPDATE calls SET audio_path = ? WHERE id = ?", (str(path), call_id))
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE calls ADD COLUMN audio_path TEXT NOT NULL DEFAULT ''")
            conn.execute("UPDATE calls SET audio_path = ? WHERE id = ?", (str(path), call_id))
        conn.commit()
    return {
        'ok': True,
        'tool': 'owner_phone',
        'call_id': call_id,
        'audio_path': str(path),
        'bytes': len(audio),
        'seconds': seconds,
        'live': True,
        'carrier': False,
    }


def append_audio(call_id: str, work: Path, chunk: bytes) -> dict:
    """Append a live carrier chunk to the call clip."""
    if not chunk:
        return {'ok': False, 'reason': 'empty audio chunk'}
    if len(chunk) > 1_000_000:
        return {'ok': False, 'reason': 'chunk is too large'}
    folder = Path(work) / 'call-audio'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f'{call_id}.wav'
    with path.open('ab') as handle:
        handle.write(chunk)
    return {'ok': True, 'tool': 'owner_phone', 'call_id': call_id, 'bytes': path.stat().st_size, 'streamed': True}
