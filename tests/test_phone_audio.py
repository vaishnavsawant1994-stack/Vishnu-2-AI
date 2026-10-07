from pathlib import Path

from evo.phone_screen import capture_audio, start_screen


def test_live_clip_is_stored_on_the_call(tmp_path: Path):
    started = start_screen('Ada', tmp_path)
    clip = b'RIFFdemo-audio'
    saved = capture_audio(started['call_id'], tmp_path, clip, seconds=3)
    assert saved['live'] is True
    assert saved['carrier'] is False
    assert Path(saved['audio_path']).read_bytes() == clip


def test_missing_audio_is_refused(tmp_path: Path):
    started = start_screen('Ada', tmp_path)
    assert capture_audio(started['call_id'], tmp_path, b'')['ok'] is False
