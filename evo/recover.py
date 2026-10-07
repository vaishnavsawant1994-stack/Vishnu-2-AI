"""Resume an interrupted goal from outside evidence. Do not repeat a finished side effect."""

from __future__ import annotations

import json
from pathlib import Path

from evo.mind import _connect


def recover(work: Path, conversation_id: str, evidence: dict) -> dict:
    with _connect(work) as conn:
        try:
            row = conn.execute(
                "SELECT id, title, steps, criteria FROM goals WHERE conversation_id = ? AND status IN ('open', 'learning', 'blocked', 'interrupted') ORDER BY id DESC LIMIT 1",
                (conversation_id,),
            ).fetchone()
        except Exception:
            return {'ok': False, 'reason': 'no recoverable goal'}
    if row is None:
        return {'ok': False, 'reason': 'no recoverable goal'}
    steps = json.loads(row['steps'])
    last = steps[-1] if steps else {}
    key = last.get('operation_key', '')
    already = bool(key and evidence.get(key) is True)
    if already:
        last['state'] = 'VERIFIED'
        last['verified'] = True
        with _connect(work) as conn:
            conn.execute("UPDATE goals SET steps = ?, status = 'open' WHERE id = ?", (json.dumps(steps), row['id']))
            conn.commit()
        return {'ok': True, 'goal_id': row['id'], 'resumed': True, 'repeated': False, 'state': 'VERIFIED'}
    return {'ok': True, 'goal_id': row['id'], 'resumed': True, 'repeated': False, 'state': last.get('state', 'open'), 'next': 'inspect before retry'}
