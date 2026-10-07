"""Build a reviewed page, API, and data layer."""

from __future__ import annotations

from evo.coder import write_source


def build_senior_stack(work, name: str) -> dict:
    slug = ''.join(ch.lower() if ch.isalnum() else '-' for ch in name).strip('-') or 'app'
    write_source(work, f'{slug}/index.html', f'''<!doctype html>
<html><head><meta charset="utf-8"><title>{slug}</title></head>
<body><h1>{slug}</h1><form id="f"><input name="text" maxlength="200"><button>Save</button></form>
<p id="error"></p><pre id="out"></pre>
<script>
async function load(){{const r=await fetch('/items');document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2)}}
document.getElementById('f').onsubmit=async(e)=>{{e.preventDefault();const r=await fetch('/items',{{method:'POST',body:new FormData(e.target)}});const body=await r.json();document.getElementById('error').textContent=body.error||'';load()}};
load();
</script></body></html>
''')
    write_source(work, f'{slug}/server.py', f'''from pathlib import Path
import sqlite3
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)
DB = Path(__file__).with_name('{slug}.sqlite3')

class InputError(ValueError):
    pass

def conn():
    c = sqlite3.connect(DB)
    c.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, text TEXT NOT NULL)')
    return c

def clean(value) -> str:
    if not isinstance(value, str):
        raise InputError('text must be a string')
    text = ' '.join(value.split())
    if not text:
        raise InputError('text is required')
    if len(text) > 200:
        raise InputError('text is too long')
    return text

@app.get('/')
def home():
    return send_file(Path(__file__).with_name('index.html'))

@app.get('/items')
def items():
    with conn() as c:
        rows = c.execute('SELECT id, text FROM items ORDER BY id').fetchall()
    return jsonify({{'items': rows}})

@app.post('/items')
def add():
    try:
        text = clean(request.form.get('text', ''))
    except InputError as exc:
        return jsonify({{'ok': False, 'error': str(exc)}}), 400
    with conn() as c:
        c.execute('INSERT INTO items (text) VALUES (?)', (text,))
    return jsonify({{'ok': True}})
''')
    write_source(work, f'{slug}/test_server.py', f'''from importlib.machinery import SourceFileLoader
from pathlib import Path

def _client(tmp_path, monkeypatch):
    server = SourceFileLoader('server', str(Path(__file__).with_name('server.py'))).load_module()
    monkeypatch.setattr(server, 'DB', tmp_path / '{slug}.sqlite3')
    return server.app.test_client()

def test_valid_item_is_stored(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    assert client.post('/items', data={{'text': '  hello  '}}).status_code == 200
    assert client.get('/items').get_json()['items'][0][1] == 'hello'

def test_empty_item_is_rejected(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    response = client.post('/items', data={{'text': '   '}})
    assert response.status_code == 400
    assert response.get_json()['ok'] is False
''')
    write_source(work, f'{slug}/DESIGN.md', f'# {slug}\n\nPage posts to the API. API validates before SQLite. Empty input returns 400.\n')
    return {'ok': True, 'tool': 'owner_senior_fullstack', 'app': slug, 'stack': ['html', 'flask', 'sqlite'], 'checks': ['validation', 'errors', 'failure tests', 'design note']}
