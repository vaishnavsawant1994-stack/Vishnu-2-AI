import pytest

from evo.skills import calculate, check_code, now, read_page


def test_calculate_does_arithmetic_only():
    assert calculate('2 + 3 * 4')['result'] == 14
    with pytest.raises(Exception):
        calculate("__import__('os').listdir()")


def test_code_check_blocks_files_and_imports():
    assert check_code('2 + 2')['result'] == 4
    blocked = check_code('open("/etc/passwd")')
    assert blocked['safe'] is False
    assert check_code('__import__("os")')['safe'] is False


def test_clock_and_page_guard():
    assert 'utc' in now()
    assert read_page('http://example.com')['ok'] is False
