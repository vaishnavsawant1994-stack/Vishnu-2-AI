from pathlib import Path

import pytest

from learning.engine import SelfImprovementEngine


def test_rejection_becomes_a_proposed_lesson(tmp_path: Path):
    engine = SelfImprovementEngine(tmp_path / 'learning.sqlite3')
    recorded = engine.observe_rejection('send the file', {'steps': [{'tool': 'files.write'}]}, 'files.write')
    assert recorded['lesson_id']
    with pytest.raises(ValueError):
        engine.correct('send the file', 'disable the permission engine')
    accepted = engine.accept(recorded['lesson_id'])
    assert accepted['status'] == 'accepted'
    assert accepted['applied_to'] == 'planner_context_only'
    context = engine.context_for('send another file')
    assert 'files.write' in context
    assert 'not permissions' in context


def test_unverified_tool_is_not_treated_as_success(tmp_path: Path):
    engine = SelfImprovementEngine(tmp_path / 'learning.sqlite3')
    recorded = engine.observe_completion(
        'open the report',
        {'steps': [{'tool': 'browser.open'}]},
        {'step1': {'verified': False, 'ok': True}},
    )
    assert recorded['outcome'] == 'unverified'
    assert recorded['lesson_id']
