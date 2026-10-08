"""Acceptance tests for a real persistent skill, not an echo."""
import json
from pathlib import Path

import pytest

from learning.engine import SelfImprovementEngine
from skills.qualified_action_items import SOURCE, _qualify


def test_qualify_real_skill_and_reuse_after_restart(tmp_path: Path):
    db = tmp_path / "learning.sqlite3"
    first = SelfImprovementEngine(db).perform_action_items("- [ ] Write tests\n- [x] Done\n- [ ] Ship fix")
    assert first["forged"] is True
    assert first["result"] == {"items": ["Write tests", "Ship fix"]}
    saved = tmp_path / "skills" / "qualified" / "extract_action_items_v1.json"
    before = saved.read_bytes()
    second = SelfImprovementEngine(db).perform_action_items("- [ ] Review logs")
    assert second["forged"] is False
    assert second["reused"] is True
    assert second["result"] == {"items": ["Review logs"]}
    assert saved.read_bytes() == before


def test_reject_bad_candidate():
    assert not _qualify('import security\ndef run(payload):\n    return {}\n')
    assert not _qualify('def run(payload):\n    return {"echo": payload}\n')


def test_reject_tampered_persistent_skill(tmp_path: Path):
    engine = SelfImprovementEngine(tmp_path / "learning.sqlite3")
    engine.perform_action_items("- [ ] First")
    saved = tmp_path / "skills" / "qualified" / "extract_action_items_v1.json"
    record = json.loads(saved.read_text())
    record["source"] = "import os"
    saved.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="integrity"):
        SelfImprovementEngine(tmp_path / "learning.sqlite3").perform_action_items("- [ ] Second")


def test_invalid_input_fails_closed(tmp_path: Path):
    with pytest.raises(ValueError):
        SelfImprovementEngine(tmp_path / "learning.sqlite3").perform_action_items("x" * 100001)
