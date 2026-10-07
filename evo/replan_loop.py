"""Run one revised step through the normal path. It cannot change the goal."""

from __future__ import annotations

from evo.replan import mind_replan


def run_revised_step(goal: str, criteria: list[str], previous_plan: str, observed: str, failure: str, revision: int, allowed: bool, verified: bool, same_failure_count: int = 0) -> dict:
    plan = mind_replan(goal, criteria, previous_plan, observed, failure, revision, same_failure_count)
    if plan['action'] == 'block':
        plan['executed'] = False
        return plan
    if not allowed:
        return {**plan, 'executed': False, 'verified': False, 'failure': 'PERMISSION_DENIED', 'criteria': list(criteria)}
    return {
        **plan,
        'executed': True,
        'verified': verified,
        'failure': None if verified else 'VERIFICATION_FAILURE',
        'criteria': list(criteria),
        'goal_changed': False,
    }
