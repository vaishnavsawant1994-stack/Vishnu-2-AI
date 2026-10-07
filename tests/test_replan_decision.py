from evo.reconcile import deployment, next_decision


def test_wrong_deployment_replans_and_unknown_blocks():
    conflict = deployment('abc123', {'id': 'D92', 'sha': 'def456', 'status': 'healthy'})
    assert conflict['state'] == 'CONFLICTED'
    assert next_decision(conflict['state'])['action'] == 'replan'
    building = deployment('abc123', {'id': 'D92', 'sha': 'abc123', 'status': 'building'})
    assert building['state'] == 'IN_PROGRESS'
    assert next_decision('UNKNOWN') == {'action': 'block', 'repeat': False}
