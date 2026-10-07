"""Build a small full-stack app in the coding workspace."""

from __future__ import annotations

from evo.coder import write_source


def build_app(work, name: str) -> dict:
    slug = ''.join(ch.lower() if ch.isalnum() else '-' for ch in name).strip('-') or 'app'
    page = f'''<!doctype html>
<html><head><meta charset="utf-8"><title>{slug}</title></head>
<body><h1>{slug}</h1><form id="f"><input name="text"><button>Save</button></form>
<pre id="out"></pre>
<script>
async function load(){{const r=await fetch('/items');document.getElementById('out').textContent=await r.text()}}
document.getElementById('f').onsubmit=async (e)=>{{e.preventDefault();await fetch('/items',{{method:'POST',body:new FormData(e.target)}});load()}};
load();
</script></body></html>
'''
    server = f'''from pathlib import Path
import sqlite3
from flask import Flask, request, send_file

app = Flask(__name__)
DB = Path(__file__).with_name('{slug}.sqlite3')

def conn():
    c = sqlite3.connect(DB)
    c.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, text TEXT)')
    return c

@app.get('/')
def home():
    return send_file(Path(__file__).with_name('index.html'))

@app.get('/items')
def items():
    with conn() as c:
        rows = c.execute('SELECT id, text FROM items').fetchall()
    return {{'items': rows}}

@app.post('/items')
def add():
    text = request.form.get('text', '').strip()[:200]
    with conn() as c:
        c.execute('INSERT INTO items (text) VALUES (?)', (text,))
    return {{'ok': True}}
'''
    test = f'''from importlib.machinery import SourceFileLoader
from pathlib import Path

def test_items_round_trip(tmp_path, monkeypatch):
    server = SourceFileLoader('server', str(Path(__file__).with_name('server.py'))).load_module()
    monkeypatch.setattr(server, 'DB', tmp_path / '{slug}.sqlite3')
    client = server.app.test_client()
    assert client.post('/items', data={{'text': 'hello'}}).status_code == 200
    assert client.get('/items').get_json()['items'][0][1] == 'hello'
'''
    files = {
        f'{slug}/index.html': page,
        f'{slug}/server.py': server,
        f'{slug}/test_app.py': test,
    }
    for relative, text in files.items():
        write_source(work, relative, text)
    return {'ok': True, 'tool': 'owner_fullstack', 'app': slug, 'files': list(files), 'stack': ['html', 'flask', 'sqlite']}
