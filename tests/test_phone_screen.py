from pathlib import Path

from evo.phone_screen import add_line, finish_screen, start_screen


def test_screen_records_a_transcript_and_summary(tmp_path: Path):
    started = start_screen('Ada', tmp_path)
    assert started['answered'] is True
    assert started['carrier'] is False
    add_line(started['call_id'], 'vishnu', 'Who is calling?', tmp_path)
    add_line(started['call_id'], 'caller', 'Ada, asking for a meeting tomorrow.', tmp_path)
    finished = finish_screen(started['call_id'], tmp_path)
    assert finished['status'] == 'finished'
    assert len(finished['transcript']) == 2
    assert 'Ada' in finished['summary']
    assert 'meeting tomorrow' in finished['summary']
