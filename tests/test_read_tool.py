from pathlib import Path

from evo.read_tool import read_anything


def test_reads_a_text_file_and_refuses_secrets(tmp_path: Path):
    note = tmp_path / 'note.txt'
    note.write_text('hello reader', encoding='utf-8')
    found = read_anything(str(note), tmp_path)
    assert found['ok'] is True
    assert found['text'] == 'hello reader'
    secret = tmp_path / '.env'
    secret.write_text('TOKEN=1', encoding='utf-8')
    assert read_anything(str(secret), tmp_path)['ok'] is False


def test_http_site_is_refused(tmp_path: Path):
    assert read_anything('http://example.com', tmp_path)['ok'] is False
