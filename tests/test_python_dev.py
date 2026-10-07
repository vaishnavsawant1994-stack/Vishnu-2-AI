from evo.coder import read_source
from evo.python_dev import build_python


def test_python_developer_creates_a_package(tmp_path):
    built = build_python(tmp_path, 'Invoice Tool')
    assert built['package'] == 'invoice_tool'
    source = read_source(tmp_path, 'invoice_tool/core.py')
    test = read_source(tmp_path, 'invoice_tool/test_core.py')
    assert 'def run' in source['text']
    assert 'test_run_cleans_text' in test['text']
