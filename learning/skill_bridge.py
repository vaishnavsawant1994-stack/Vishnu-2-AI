"""Use a qualified skill from learning. This does not promote a rewrite."""
from __future__ import annotations

from pathlib import Path

from learning.engine import SelfImprovementEngine
from skills.qualified_action_items import execute_action_items


def learn_action_items(data_dir: Path, text: str) -> dict:
    """Run the one qualified skill and record that it was reused or forged."""
    result = execute_action_items(Path(data_dir), text)
    engine = SelfImprovementEngine(Path(data_dir) / "learning.sqlite3")
    lesson = engine.correct(
        "extract action items",
        "Use the qualified action-item skill and do not treat an echo as the skill.",
    )
    return {
        "skill_id": result["skill_id"],
        "reused": result["reused"],
        "items": result["result"]["items"],
        "lesson_id": lesson["lesson_id"],
        "rewrite_promoted": False,
    }


def request_rewrite_promotion() -> dict:
    """Fail closed. The learning path cannot promote a candidate."""
    return {"state": "BLOCKED", "reason": "only the owner kernel can promote", "rewrite_promoted": False}
