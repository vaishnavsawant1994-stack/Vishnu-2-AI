from evo.reconcile import github_pr


def test_github_without_a_token_is_unknown():
    result = github_pr('vaishnavsawant1994-stack', 'Vishnu-2-AI', 'feature/x', '')
    assert result['state'] == 'UNKNOWN'
    assert result['retry_safe'] is False
