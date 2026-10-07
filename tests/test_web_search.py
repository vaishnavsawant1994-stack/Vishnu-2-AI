from evo.search import search_web


def test_empty_query_does_not_call_the_web():
    assert search_web('   ')['ok'] is False
