"""The hosted skill path must not silently use ephemeral local storage."""
from skills import postgres_skill_store
from skills.qualified_action_items import execute_action_items


def test_postgres_backend_reuses_without_writing_local_skill(monkeypatch, tmp_path):
    monkeypatch.setenv("PERSONAL_AI_SKILL_DATABASE_URL", "postgresql://example.invalid/db")
    calls = []

    def fake_get_or_qualify(skill_id, source, qualify):
        calls.append(skill_id)
        assert qualify(source)
        return len(calls) == 1

    monkeypatch.setattr(postgres_skill_store, "get_or_qualify", fake_get_or_qualify)
    first = execute_action_items(tmp_path, "- [ ] Ship")
    second = execute_action_items(tmp_path, "- [ ] Ship")
    assert first["forged"] and not first["reused"]
    assert second["reused"] and not second["forged"]
    assert first["result"]["items"] == ["Ship"]
    assert len(calls) == 2
    assert not (tmp_path / "skills").exists()


def test_postgres_failure_never_falls_back_to_local(monkeypatch, tmp_path):
    monkeypatch.setenv("PERSONAL_AI_SKILL_DATABASE_URL", "postgresql://example.invalid/db")

    def failed(*args):
        raise ConnectionError("database unavailable")

    monkeypatch.setattr(postgres_skill_store, "get_or_qualify", failed)
    try:
        execute_action_items(tmp_path, "- [ ] Ship")
    except ConnectionError:
        pass
    else:
        raise AssertionError("database failure must fail closed")
    assert not (tmp_path / "skills").exists()
