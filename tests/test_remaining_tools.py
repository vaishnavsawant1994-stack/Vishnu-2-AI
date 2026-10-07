from pathlib import Path

from evo.phone_screen import append_audio, start_screen
from evo.workspace_memory import recall, remember


def test_workspace_memory_round_trip(tmp_path: Path):
    remember(tmp_path, 'build', 'created ledger')
    notes = recall(tmp_path)['notes']
    assert notes[0]['text'] == 'created ledger'


def test_call_stream_appends(tmp_path: Path):
    started = start_screen('Ada', tmp_path)
    first = append_audio(started['call_id'], tmp_path, b'one')
    second = append_audio(started['call_id'], tmp_path, b'two')
    assert second['streamed'] is True
    assert second['bytes'] == first['bytes'] + 3
