"""Revise the route. The goal and its criteria stay fixed."""

from __future__ import annotations


def mind_replan(goal: str, criteria: list[str], previous_plan: str, observed: str, failure: str, revision: int, same_failure_count: int = 0) -> dict:
    if same_failure_count >= 3:
        return {
            'ok': False,
            'action': 'block',
            'failure': 'MISSING_CAPABILITY',
            'goal': goal,
            'criteria': list(criteria),
            'revision': revision,
            'reason': 'same failure repeated',
        }
    assumption = 'the current route still matches the outside state'
    if 'wrong base' in observed or failure == 'CONFLICTED':
        assumption = 'no existing pull request targets the wrong base'
        next_step = 'inspect the existing pull request'
    elif failure == 'PARTIALLY_APPLIED':
        assumption = 'the effect was either complete or absent'
        next_step = 'repair the remaining work'
    else:
        next_step = 'choose one narrower step'
    return {
        'ok': True,
        'action': 'replan',
        'goal': goal,
        'criteria': list(criteria),
        'unchanged_goal': True,
        'invalidated_assumption': assumption,
        'previous_plan': previous_plan,
        'new_strategy': next_step,
        'next_step': next_step,
        'revision': revision + 1,
        'mutated': False,
    }
