from evo.sandbox_manager import discover_capabilities, isolation_evidence, respond_to_isolation


def test_missing_container_blocks_without_installing_docker():
    found = discover_capabilities()
    decision = respond_to_isolation('CONTAINER', found)
    assert decision['action'] == 'block'
    assert decision['failure'] == 'INSUFFICIENT_ISOLATION'
    assert decision['install_docker'] is False
    evidence = isolation_evidence('CONTAINER', found, 82, 99, True)
    assert evidence['promoted'] is False
    assert evidence['actual_isolation'] == 'WORKSPACE'
