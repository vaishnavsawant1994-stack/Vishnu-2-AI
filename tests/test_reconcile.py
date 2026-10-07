from evo.mind import interrupt_step, start_goal
from evo.reconcile import database_write, file_write, provider_status
from evo.recover import recover_external


def test_file_and_database_are_checked_directly(tmp_path):
    note = tmp_path / 'out.txt'
    note.write_text('release abc', encoding='utf-8')
    assert file_write(note, 'abc')['state'] == 'APPLIED'
    assert file_write(tmp_path / 'missing.txt')['state'] == 'NOT_APPLIED'
    assert provider_status('railway')['state'] == 'UNKNOWN'


def test_unknown_provider_blocks_the_next_plan(tmp_path):
    goal = start_goal(tmp_path, 'Deploy', ['release exists'], conversation_id='chat-1')
    interrupt_step(tmp_path, goal['id'], 'deploy', 'g1-deploy')
    result = recover_external(tmp_path, 'chat-1', 'railway', 'service', '')
    assert result['observed']['state'] == 'UNKNOWN'
    assert result['plan_allowed'] is False
    assert result['repeated'] is False
