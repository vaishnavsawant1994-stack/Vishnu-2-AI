from pathlib import Path

from app.council import debate
from app.store import add_idea, connect, decide, save_council


def test_council_names_the_idea():
    result = debate("Market stall ledger", "Track cash without a new app store account.")
    names = [voice.name for voice in result.voices]
    assert names == ["Preserver", "Builder", "Critic", "Operator"]
    assert "Market stall ledger" in result.decision
    assert result.source == "heuristic"


def test_idea_can_be_debated_and_parked(tmp_path: Path):
    conn = connect(tmp_path / "ideas.sqlite3")
    idea = add_idea(conn, "Night market map", "Paper first.")
    saved = save_council(conn, idea["id"], debate(idea["title"], idea["seed"]))
    assert saved["status"] == "debated"
    parked = decide(conn, idea["id"], "parked")
    assert parked["status"] == "parked"
