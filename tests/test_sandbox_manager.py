from evo.sandbox_manager import open_sandbox, qualify, run_in_sandbox


def test_sandbox_runs_without_promoting_or_reading_vault(tmp_path):
    opened = open_sandbox(tmp_path, 'try a fix')
    assert opened['vault'] == 'denied'
    run = run_in_sandbox(tmp_path, opened['run_id'], 'print(1 + 1)')
    assert run['ok'] is True
    assert run['promoted'] is False
    blocked = run_in_sandbox(tmp_path, opened['run_id'], 'import security.vault')
    assert blocked['ok'] is False


def test_claim_does_not_promote():
    assert qualify(True, False)['promoted'] is False
    assert qualify(False, True)['promoted'] is True
