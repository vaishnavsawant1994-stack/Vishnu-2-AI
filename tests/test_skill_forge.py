from pathlib import Path

import pytest

from skills.forge import forge


def test_forge_keeps_a_skill_only_after_a_subprocess_test(tmp_path: Path):
    forged = forge('track the evening bus', tmp_path)
    assert forged['tested'] is True
    assert Path(forged['path']).exists()
    assert forged['sample']['ok'] is True


def test_forge_refuses_a_security_goal(tmp_path: Path, monkeypatch):
    import skills.forge as forge_mod
    monkeypatch.setattr(forge_mod, '_source', lambda name, goal: 'import security\ndef run(payload):\n    return {}')
    with pytest.raises(ValueError):
        forge('open the vault', tmp_path)
