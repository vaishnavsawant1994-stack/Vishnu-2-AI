"""Feed one revised step back into the active goal. It does not run a second executor."""

from __future__ import annotations

from pathlib import Path

from evo.adaptive import adapt
from evo.mind import active_goal


def live_replan(work: Path, conversation_id: str, observed: str, failure: str, allowed: bool, verified: bool) -> dict:
    goal = active_goal(work, conversation_id)
    if not goal:
        return {'ok': False, 'reason': 'no active goal'}
    marker = Path(work) / 'replan-triggers' / f"{goal['goal_id']}-{failure}"
    if marker.exists():
        return {'ok': True, 'goal_id': goal['goal_id'], 'criteria': goal['criteria'], 'context': marker.read_text(encoding='utf-8'), 'duplicate': True, 'goal_changed': False}
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
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(result['context'], encoding='utf-8')
    result['duplicate'] = False
    return result
