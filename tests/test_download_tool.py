from evo.download_tool import download_file


def test_local_and_http_urls_are_refused(tmp_path):
    assert download_file('http://example.com/a.txt', tmp_path)['ok'] is False
    assert download_file('https://127.0.0.1/a.txt', tmp_path)['ok'] is False
    assert download_file('https://localhost/a.txt', tmp_path)['ok'] is False
