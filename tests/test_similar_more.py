from evo.similar.reach import reach
from evo.similar.sandbox import run_sandbox


def test_sandbox_runs_written_code(tmp_path):
    result = run_sandbox(tmp_path, 'hello.py', 'print("ready")')
    assert result['ok'] is True
    assert 'ready' in result['stdout']


def test_reach_refuses_plain_http():
    assert reach('http://example.com')['ok'] is False
