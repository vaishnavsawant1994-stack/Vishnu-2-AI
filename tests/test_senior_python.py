from evo.coder import read_source
from evo.senior_python import build_senior


def test_senior_builder_includes_failure_tests(tmp_path):
    built = build_senior(tmp_path, 'Billing Service')
    assert 'failure tests' in built['checks']
    source = read_source(tmp_path, 'billing_service/service.py')
    tests = read_source(tmp_path, 'billing_service/test_service.py')
    assert 'class InputError' in source['text']
    assert 'test_run_rejects_empty_and_non_text' in tests['text']
