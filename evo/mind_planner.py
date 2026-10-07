"""Run one planner cycle through the goal loop. The planner does not grade itself."""

from __future__ import annotations

from pathlib import Path

from evo.mind import goal_status, mark_blocked, record_step, start_goal


def verify(expected, actual) -> dict:
    if actual is None:
        return {'verified': False, 'state': 'unknown'}
    return {'verified': actual == expected, 'state': 'verified' if actual == expected else 'failed'}


def plan_cycle(work: Path, title: str, criteria: list[str], hypothesis: str, action: str, expected, actual, met: list[str] | None = None, blocked: str = '') -> dict:
    goal = start_goal(work, title, criteria)
    if not goal['ok']:
        return goal
    if blocked:
        state = mark_blocked(work, goal['id'], blocked)
        state['next'] = 'resume when the missing dependency is available'
        return state
    check = verify(expected, actual)
    step = record_step(work, goal['id'], hypothesis, action, str(actual), check['verified'])
    status = goal_status(work, goal['id'], met or [])
    context = {
        'goal': title,
        'missing': status['missing'],
        'lesson': step['lesson'],
        'verified': check['verified'],
    }
    return {
        'ok': True,
        'tool': 'mind_planner',
        'id': goal['id'],
        'verification': check,
        'status': status['status'],
        'context': context,
        'stop_cleared': False,
    }
