from pathlib import Path

from skills.external_app import external_status


def test_missing_install_is_not_copied(tmp_path: Path):
    status = external_status(None, tmp_path)
    assert status['available'] is False


def test_path_inside_repo_is_refused(tmp_path: Path):
    inside = tmp_path / 'vendor'
    inside.mkdir()
    status = external_status(str(inside), tmp_path)
    assert status['available'] is False
    assert 'outside' in status['reason']
