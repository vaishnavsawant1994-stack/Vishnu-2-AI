from evo.mind import goal_status, record_step, start_goal


def test_goal_continues_until_criteria_are_met(tmp_path):
    goal = start_goal(tmp_path, 'Research the site', ['pages found', 'records stored'])
    step = record_step(tmp_path, goal['id'], 'Coverage is partial', 'extract pages', '50 records', False)
    assert step['stop_cleared'] is False
    assert 'verification fails' in step['lesson']
    status = goal_status(tmp_path, goal['id'], ['pages found'])
    assert status['status'] == 'continue'
    assert status['missing'] == ['records stored']


def test_goal_requires_criteria(tmp_path):
    assert start_goal(tmp_path, 'Loose goal', [])['ok'] is False
