"""One explicit runtime step. A replan enters the adaptive cycle once."""

from __future__ import annotations

from pathlib import Path

from evo.live_replan import live_replan


def advance(work: Path, conversation_id: str, state: str, observed: str = '', allowed: bool = True, verified: bool = False) -> dict:
    if state == 'STOPPED':
        return {'state': 'STOPPED', 'advanced': False}
    if state != 'REPLAN':
        return {'state': state, 'advanced': False}
    revised = live_replan(work, conversation_id, observed or 'wrong base', 'CONFLICTED', allowed, verified)
    if not revised.get('ok'):
        return {'state': 'BLOCKED', 'reason': revised.get('reason', 'no active goal'), 'advanced': False}
    return {'state': 'PLAN', 'advanced': True, 'context': revised['context'], 'goal_changed': False, 'criteria': revised['criteria']}
