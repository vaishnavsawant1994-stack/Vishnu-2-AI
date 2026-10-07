from evo.mind import start_goal
from evo.runtime_loop import advance


def test_replan_state_enters_the_cycle_once(tmp_path):
    start_goal(tmp_path, 'Get the fix into main', ['pull request merged'], conversation_id='chat-1')
    result = advance(tmp_path, 'chat-1', 'REPLAN', 'wrong base')
    assert result['advanced'] is True
    assert result['state'] == 'PLAN'
    assert result['goal_changed'] is False
    assert result['criteria'] == ['pull request merged']


def test_stop_does_not_enter_the_cycle(tmp_path):
    assert advance(tmp_path, 'chat-1', 'STOPPED')['advanced'] is False
