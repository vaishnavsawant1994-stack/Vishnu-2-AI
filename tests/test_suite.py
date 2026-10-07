from evo.similar.suite import run_suite


def test_suite_runs_the_safe_jobs(tmp_path):
    result = run_suite(tmp_path, 'Ledger')
    assert result['ok'] is True
    assert result['video'] is False
    assert result['voice_clone'] is False
    assert result['download'] is False
