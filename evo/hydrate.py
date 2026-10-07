"""Load an active goal for the planner. This does not change the goal."""

from __future__ import annotations

from pathlib import Path

from evo.mind import active_goal


def hydrate(work: Path, conversation_id: str = '') -> str:
    goal = active_goal(work, conversation_id)
    if not goal:
        return ''
    criteria = ', '.join(goal['criteria'])
    return (
        f"ACTIVE GOAL {goal['goal_id']}: {goal['title']}\\n"
        f"completion criteria: {criteria}\\n"
        f"lesson: {goal['lesson'] or 'none'}\\n"
        f"status: {goal['status']}"
    )
