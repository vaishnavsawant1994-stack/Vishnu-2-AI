from evo.coder import read_source
from evo.fullstack import build_app


def test_fullstack_creates_page_api_and_test(tmp_path):
    built = build_app(tmp_path, 'Notes')
    assert built['stack'] == ['html', 'flask', 'sqlite']
    page = read_source(tmp_path, 'notes/index.html')
    server = read_source(tmp_path, 'notes/server.py')
    assert '<form' in page['text']
    assert 'sqlite3' in server['text']
    assert '@app.post' in server['text']
