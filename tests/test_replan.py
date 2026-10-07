from evo.replan import mind_replan


def test_conflict_revises_the_plan_and_keeps_the_goal():
    result = mind_replan('Get the fix into main', ['pull request merged'], 'create pull request', 'wrong base', 'CONFLICTED', 1)
    assert result['unchanged_goal'] is True
    assert result['criteria'] == ['pull request merged']
    assert result['revision'] == 2
    assert result['next_step'] == 'inspect the existing pull request'
    assert result['mutated'] is False


def test_repeated_failure_blocks_instead_of_looping():
    result = mind_replan('Get the fix into main', ['pull request merged'], 'create pull request', 'wrong base', 'CONFLICTED', 4, same_failure_count=3)
    assert result['action'] == 'block'
    assert result['failure'] == 'MISSING_CAPABILITY'
