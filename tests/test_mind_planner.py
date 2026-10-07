from evo.mind_planner import plan_cycle, verify


def test_planner_does_not_accept_its_own_claim(tmp_path):
    result = plan_cycle(tmp_path, 'Store records', ['count is 100'], 'The tool said it stored them', 'insert records', 100, 50, [])
    assert result['verification']['verified'] is False
    assert result['status'] == 'continue'
    assert 'verification fails' in result['context']['lesson']
    assert result['stop_cleared'] is False


def test_blocked_goal_waits_instead_of_completing(tmp_path):
    result = plan_cycle(tmp_path, 'Deploy', ['health is 200'], '', '', None, None, [], blocked='credential unavailable')
    assert result['status'] == 'blocked'
    assert verify(200, 200)['verified'] is True
