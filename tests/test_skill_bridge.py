from learning.skill_bridge import learn_action_items, request_rewrite_promotion


def test_skill_is_reused_after_restart(tmp_path):
    text = "- [ ] Send report\n- [x] Done"
    first = learn_action_items(tmp_path, text)
    second = learn_action_items(tmp_path, text)
    assert first["items"] == ["Send report"]
    assert first["reused"] is False
    assert second["reused"] is True
    assert second["items"] == ["Send report"]
    assert second["rewrite_promoted"] is False


def test_learning_cannot_promote_a_rewrite():
    assert request_rewrite_promotion()["state"] == "BLOCKED"
