from evo.sandbox_manager import compare_baseline, open_sandbox


def test_candidate_must_beat_a_frozen_baseline(tmp_path):
    opened = open_sandbox(tmp_path, 'planner experiment')
    assert 'network_policy: default deny' in (tmp_path / 'sandboxes' / opened['run_id'] / 'manifest.txt').read_text()
    assert compare_baseline(82, 89, True)['promoted'] is True
    assert compare_baseline(82, 89, False)['promoted'] is False
    assert compare_baseline(82, 80, True)['promoted'] is False
