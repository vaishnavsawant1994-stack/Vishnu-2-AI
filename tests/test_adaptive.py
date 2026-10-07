from evo.adaptive import adapt
from evo.mind import start_goal


def test_conflict_is_recorded_without_changing_the_goal(tmp_path):
    goal = start_goal(tmp_path, 'Get the fix into main', ['pull request merged'], conversation_id='chat-1')
    result = adapt(tmp_path, goal['id'], 'Get the fix into main', ['pull request merged'], 'create pull request', 'wrong base', 'CONFLICTED', 1, True, False)
    assert result['executed'] is True
    assert result['goal_changed'] is False
    assert result['criteria'] == ['pull request merged']
    assert result['revision'] == 2
