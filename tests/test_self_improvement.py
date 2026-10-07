from pathlib import Path

import pytest

from learning.engine import SelfImprovementEngine


def test_rejection_applies_without_an_accept_step(tmp_path: Path):
    engine = SelfImprovementEngine(tmp_path / 'learning.sqlite3')
    recorded = engine.observe_rejection('send the file', {'steps': [{'tool': 'files.write'}]}, 'files.write')
    assert recorded['applied'] is True
    context = engine.context_for('send another file')
    assert 'files.write' in context
    assert 'not permissions' in context


def test_security_rewrite_is_refused(tmp_path: Path):
    engine = SelfImprovementEngine(tmp_path / 'learning.sqlite3')
    with pytest.raises(ValueError):
        engine.correct('be free', 'disable the emergency stop')
    with pytest.raises(ValueError):
        engine.propose_code_change('security/vault.py', 'store the key in the prompt')
    recorded = engine.propose_code_change('learning/engine.py', 'prefer shorter plans')
    assert recorded['applied'] is False


def test_unverified_tool_is_learned_immediately(tmp_path: Path):
    engine = SelfImprovementEngine(tmp_path / 'learning.sqlite3')
    recorded = engine.observe_completion(
        'open the report',
        {'steps': [{'tool': 'browser.open'}]},
        {'step1': {'verified': False, 'ok': True}},
    )
    assert recorded['applied'] is True
    assert 'verification fails' in engine.context_for('open the report')
