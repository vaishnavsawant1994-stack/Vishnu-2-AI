from core.permissions import PermissionEngine


def test_free_mode_allows_a_critical_action_until_stop():
    decision = PermissionEngine('free').decide(4)
    assert decision.allowed is True
    assert decision.requires_confirmation is False


def test_ask_mode_still_blocks_side_effects():
    decision = PermissionEngine('ask').decide(2)
    assert decision.allowed is False
