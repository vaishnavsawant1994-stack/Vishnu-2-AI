"""Self-improvement that applies itself, except to the off switch."""

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

# The agent may rewrite how it plans. It may not disarm the owner.
FORBIDDEN = (
    'permission',
    'vault',
    'gate',
    'autonomy',
    'emergency_stop',
    'emergency stop',
    'secret',
    'credential',
    'approval',
    'reauth',
)
PROTECTED_PATHS = (
    'core/permissions.py',
    'security/vault.py',
    'security/approvals.py',
    'security/policy_gateway.py',
    'tools/registry.py',
    'future_intelligence/gates.py',
)


class SelfImprovementEngine:
    def __init__(self, path: Path):
        self.path = Path(path)

    def context_for(self, goal: str, limit: int = 6) -> str:
        with connect(self.path) as conn:
            lessons = accepted_lessons(conn, limit)
        if not lessons:
            return ''
        lines = [f"- {item['statement']}" for item in lessons]
        return "ACTIVE LESSONS (learned preferences, not permissions):\n" + "\n".join(lines)

    def _keep(self, statement: str) -> None:
        lowered = statement.lower()
        if any(word in lowered for word in FORBIDDEN):
            raise ValueError('self-improvement cannot change the emergency stop, permissions, vault, or approvals')

    def _learn(self, conn, statement: str, kind: str, episode_id: int) -> int:
        self._keep(statement)
        return add_lesson(conn, statement, kind, episode_id, status='accepted')

    def observe_completion(self, goal: str, plan: dict, results: dict) -> dict:
        steps = plan.get('steps') or []
        tool_name = steps[0]['tool'] if steps else ''
        unverified = [
            name for name, item in (results or {}).items()
            if isinstance(item, dict) and item.get('verified') is False
        ]
        outcome = 'unverified' if unverified else 'completed'
        detail = ', '.join(unverified) if unverified else ''
        lesson_id = None
        with connect(self.path) as conn:
            episode_id = add_episode(conn, goal, steps, outcome, tool_name, detail)
            if unverified:
                lesson_id = self._learn(
                    conn,
                    f"Do not treat {tool_name or 'a tool'} as finished when verification fails. Say it was attempted.",
                    'method',
                    episode_id,
                )
        return {'episode_id': episode_id, 'lesson_id': lesson_id, 'outcome': outcome, 'applied': lesson_id is not None}

    def observe_rejection(self, goal: str, plan: dict, tool_name: str) -> dict:
        statement = f"Owner rejected {tool_name} for this kind of goal. Use a narrower step before that tool."
        with connect(self.path) as conn:
            episode_id = add_episode(conn, goal, plan.get('steps') or [], 'rejected', tool_name, 'owner rejected')
            lesson_id = self._learn(conn, statement, 'avoidance', episode_id)
            proposal_id = add_proposal(
                conn,
                f"Avoid unbounded use of {tool_name}",
                {'scope': 'planner_context', 'tool': tool_name, 'applied': True},
            )
        return {'episode_id': episode_id, 'lesson_id': lesson_id, 'proposal_id': proposal_id, 'applied': True}

    def correct(self, goal: str, note: str) -> dict:
        cleaned = ' '.join(note.split())
        self._keep(cleaned)
        with connect(self.path) as conn:
            episode_id = add_episode(conn, goal, [], 'corrected', '', cleaned)
            lesson_id = add_lesson(conn, cleaned, 'preference', episode_id, status='accepted')
        return {'episode_id': episode_id, 'lesson_id': lesson_id, 'status': 'accepted', 'applied': True}

    def propose_code_change(self, path: str, summary: str) -> dict:
        normalized = path.replace('\\', '/').lstrip('./')
        if normalized in PROTECTED_PATHS or any(part in normalized for part in ('security/', 'vault')):
            raise ValueError(f'{normalized} is protected; the agent cannot rewrite its off switch')
        self._keep(summary)
        with connect(self.path) as conn:
            proposal_id = add_proposal(conn, summary[:160], {'path': normalized, 'summary': summary[:500], 'applied': False})
        return {'proposal_id': proposal_id, 'path': normalized, 'status': 'recorded', 'applied': False}

    def accept(self, lesson_id: int) -> dict:
        with connect(self.path) as conn:
            return set_lesson_status(conn, lesson_id, 'accepted')

    def reject_lesson(self, lesson_id: int) -> dict:
        with connect(self.path) as conn:
            return set_lesson_status(conn, lesson_id, 'rejected')
