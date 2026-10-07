from evo.mind import interrupt_step, start_goal
from evo.recover import recover


def test_restart_does_not_repeat_a_finished_side_effect(tmp_path):
    goal = start_goal(tmp_path, 'Deploy', ['release exists'], conversation_id='chat-1')
    interrupt_step(tmp_path, goal['id'], 'create deployment', 'g1-deploy')
    resumed = recover(tmp_path, 'chat-1', {'g1-deploy': True})
    assert resumed['resumed'] is True
    assert resumed['repeated'] is False
    assert resumed['state'] == 'VERIFIED'


def test_missing_evidence_does_not_retry_blindly(tmp_path):
    goal = start_goal(tmp_path, 'Deploy', ['release exists'], conversation_id='chat-1')
    interrupt_step(tmp_path, goal['id'], 'create deployment', 'g1-deploy')
    resumed = recover(tmp_path, 'chat-1', {})
    assert resumed['repeated'] is False
    assert resumed['next'] == 'inspect before retry'
