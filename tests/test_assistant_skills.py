import pytest

from evo.skills import calculate, now, read_page


def test_calculate_does_arithmetic_only():
    assert calculate('2 + 3 * 4')['result'] == 14
    with pytest.raises(Exception):
        calculate("__import__('os').listdir()")


def test_clock_and_page_guard():
    assert 'utc' in now()
    assert read_page('http://example.com')['ok'] is False
