from evo.coder import read_source
from evo.senior_fullstack import build_senior_stack


def test_senior_stack_rejects_empty_input_in_tests(tmp_path):
    built = build_senior_stack(tmp_path, 'Ledger')
    assert built['stack'] == ['html', 'flask', 'sqlite']
    server = read_source(tmp_path, 'ledger/server.py')
    tests = read_source(tmp_path, 'ledger/test_server.py')
    assert 'class InputError' in server['text']
    assert 'test_empty_item_is_rejected' in tests['text']
