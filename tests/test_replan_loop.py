from evo.replan_loop import run_revised_step


def test_revised_step_uses_the_same_path_and_keeps_the_goal():
    result = run_revised_step('Get the fix into main', ['pull request merged'], 'create pull request', 'wrong base', 'CONFLICTED', 1, True, False)
    assert result['executed'] is True
    assert result['verified'] is False
    assert result['failure'] == 'VERIFICATION_FAILURE'
    assert result['criteria'] == ['pull request merged']
    assert result['goal_changed'] is False


def test_permission_and_repeated_credential_block_without_running():
    denied = run_revised_step('Get the fix into main', ['pull request merged'], 'create pull request', 'wrong base', 'CONFLICTED', 1, False, False)
    assert denied['executed'] is False
    assert denied['failure'] == 'PERMISSION_DENIED'
    blocked = run_revised_step('Get the fix into main', ['pull request merged'], 'create pull request', 'token missing', 'MISSING_CREDENTIAL', 3, True, False, same_failure_count=3)
    assert blocked['failure'] == 'MISSING_CREDENTIAL'
    assert blocked['executed'] is False
