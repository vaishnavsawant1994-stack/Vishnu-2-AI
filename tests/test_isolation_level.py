from evo.sandbox_manager import open_sandbox, require_isolation


def test_manifest_does_not_pretend_network_is_enforced(tmp_path):
    opened = open_sandbox(tmp_path, 'planner experiment')
    text = (tmp_path / 'sandboxes' / opened['run_id'] / 'manifest.txt').read_text()
    assert 'network_enforced: false' in text
    assert 'isolation: WORKSPACE' in text


def test_container_experiment_is_refused_on_a_workspace_machine():
    assert require_isolation('CONTAINER')['ok'] is False
    assert require_isolation('WORKSPACE')['ok'] is True
