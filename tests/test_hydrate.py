import sqlite3
from pathlib import Path

from evo.hydrate import hydrate
from evo.mind import start_goal
from evo.verifiers import classify, db_count


def test_active_goal_is_loaded_for_its_conversation(tmp_path: Path):
    start_goal(tmp_path, 'Store the records', ['count is 100'], conversation_id='chat-1')
    loaded = hydrate(tmp_path, 'chat-1')
    assert loaded.startswith('ACTIVE GOAL')
    assert 'count is 100' in loaded
    assert hydrate(tmp_path, 'other-chat') == ''


def test_count_verifier_uses_the_database(tmp_path: Path):
    db = tmp_path / 'research.sqlite3'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE people (id INTEGER PRIMARY KEY, text TEXT)')
        conn.executemany('INSERT INTO people (text) VALUES (?)', [('a',), ('b',)])
    proof = db_count(db, 'people', 100)
    assert proof['actual'] == 2
    assert proof['verified'] is False
    assert proof['failure'] == 'VERIFICATION_FAILURE'
    assert classify('credential unavailable') == 'MISSING_CREDENTIAL'
