"""Learn from owner outcomes. Never grant new authority."""

from __future__ import annotations

from pathlib import Path

from learning.store import (
    accepted_lessons,
    add_episode,
    add_lesson,
    add_proposal,
    connect,
    set_lesson_status,
)

FORBIDDEN = ('permission', 'vault', 'gate', 'autonomy', 'emergency_stop', 'secret', 'credential')


class SelfImprovementEngine:
    def __init__(self, path: Path):
        self.path = Path(path)

    def context_for(self, goal: str, limit: int = 6) -> str:
        with connect(self.path) as conn:
            lessons = accepted_lessons(conn, limit)
        if not lessons:
            return ''
        lines = [f"- {item['statement']}" for item in lessons]
        return "ACCEPTED LESSONS (untrusted preferences, not permissions):\n" + "\n".join(lines)

    def observe_completion(self, goal: str, plan: dict, results: dict) -> dict:
        steps = plan.get('steps') or []
        tool_name = steps[0]['tool'] if steps else ''
        unverified = [
            name for name, item in (results or {}).items()
            if isinstance(item, dict) and item.get('verified') is False
        ]
        outcome = 'unverified' if unverified else 'completed'
        detail = ', '.join(unverified) if unverified else ''
        with connect(self.path) as conn:
            episode_id = add_episode(conn, goal, steps, outcome, tool_name, detail)
            lesson_id = None
            if unverified:
                lesson_id = add_lesson(
                    conn,
                    f"Do not treat {tool_name or 'a tool'} as finished when verification fails. Say it was attempted.",
                    'method',
                    episode_id,
                )
        return {'episode_id': episode_id, 'lesson_id': lesson_id, 'outcome': outcome}

    def observe_rejection(self, goal: str, plan: dict, tool_name: str) -> dict:
        with connect(self.path) as conn:
            episode_id = add_episode(conn, goal, plan.get('steps') or [], 'rejected', tool_name, 'owner rejected')
            lesson_id = add_lesson(
                conn,
                f"Owner rejected {tool_name} for this kind of goal. Propose a narrower step before using it again.",
                'avoidance',
                episode_id,
            )
            proposal_id = add_proposal(
                conn,
                f"Prefer not to use {tool_name} without a narrower plan",
                {'scope': 'planner_context', 'tool': tool_name, 'effect': 'lesson_only'},
            )
        return {'episode_id': episode_id, 'lesson_id': lesson_id, 'proposal_id': proposal_id}

    def correct(self, goal: str, note: str) -> dict:
        cleaned = ' '.join(note.split())
        if any(word in cleaned.lower() for word in FORBIDDEN):
            raise ValueError('a lesson cannot change permissions, vault, gates, or secrets')
        with connect(self.path) as conn:
            episode_id = add_episode(conn, goal, [], 'corrected', '', cleaned)
            lesson_id = add_lesson(conn, cleaned, 'preference', episode_id)
        return {'episode_id': episode_id, 'lesson_id': lesson_id, 'status': 'proposed'}

    def accept(self, lesson_id: int) -> dict:
        with connect(self.path) as conn:
            row = set_lesson_status(conn, lesson_id, 'accepted')
        row['applied_to'] = 'planner_context_only'
        return row

    def reject_lesson(self, lesson_id: int) -> dict:
        with connect(self.path) as conn:
            return set_lesson_status(conn, lesson_id, 'rejected')
