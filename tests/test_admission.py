from evo.sandbox_manager import admit, discover_capabilities, qualify_experiment


def test_weaker_machine_does_not_downgrade_or_promote():
    found = discover_capabilities()
    assert found['available_isolation'] == 'WORKSPACE'
    decision = admit('CONTAINER', found)
    assert decision['ok'] is False
    assert decision['failure'] == 'INSUFFICIENT_ISOLATION'
    assert decision['downgraded'] is False
    assert qualify_experiment(82, 99, True, False)['promoted'] is False
