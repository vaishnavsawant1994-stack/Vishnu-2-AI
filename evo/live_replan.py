"""Feed one revised step back into the active goal. It does not run a second executor."""

from __future__ import annotations

from pathlib import Path

from evo.adaptive import adapt
from evo.mind import active_goal


def live_replan(work: Path, conversation_id: str, observed: str, failure: str, allowed: bool, verified: bool) -> dict:
    goal = active_goal(work, conversation_id)
    if not goal:
        return {'ok': False, 'reason': 'no active goal'}
    result = adapt(
        work,
        goal['goal_id'],
        goal['title'],
        goal['criteria'],
        'previous plan',
        observed,
        failure,
        1,
        allowed,
        verified,
    )
    result['ok'] = True
    result['goal_id'] = goal['goal_id']
    result['context'] = f"REVISED STEP {result.get('revision')}: {result.get('next_step')}"
    return result
