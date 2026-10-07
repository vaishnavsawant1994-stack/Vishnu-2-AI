"""One adaptive cycle: conflict, revise, one checked step, record. The goal stays fixed."""

from __future__ import annotations

from evo.mind import record_step
from evo.replan_loop import run_revised_step


def adapt(work, goal_id: int, goal: str, criteria: list[str], previous_plan: str, observed: str, failure: str, revision: int, allowed: bool, verified: bool, same_failure_count: int = 0) -> dict:
    result = run_revised_step(goal, criteria, previous_plan, observed, failure, revision, allowed, verified, same_failure_count)
    record_step(work, goal_id, result.get('invalidated_assumption', ''), result.get('next_step', 'blocked'), str(result.get('failure') or 'verified'), bool(result.get('verified')))
    result['goal_changed'] = False
    result['criteria'] = list(criteria)
    return result
