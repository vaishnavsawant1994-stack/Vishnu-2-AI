from evo.live_replan import live_replan
from evo.mind import start_goal


def test_live_replan_uses_the_active_goal(tmp_path):
    start_goal(tmp_path, 'Get the fix into main', ['pull request merged'], conversation_id='chat-1')
    result = live_replan(tmp_path, 'chat-1', 'wrong base', 'CONFLICTED', True, False)
    assert result['goal_id']
    assert result['criteria'] == ['pull request merged']
    assert result['context'].startswith('REVISED STEP 2')
    assert result['goal_changed'] is False
