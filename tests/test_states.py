from evo.states import allow


def test_replan_returns_to_plan_and_cannot_replan_again():
    assert allow('REPLAN', 'PLAN')['ok'] is True
    assert allow('REPLAN', 'REPLAN')['ok'] is False
    assert allow('STOPPED', 'REPLAN')['ok'] is False
