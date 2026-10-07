from pathlib import Path

from skills.external_local import external_skill


def test_missing_home_does_not_clone(tmp_path: Path):
    result = external_skill('', tmp_path)
    assert result['available'] is False
    assert 'clone' not in result['reason']


def test_code_inside_vishnu_repo_is_refused(tmp_path: Path):
    (tmp_path / 'main.py').write_text('print(1)\n', encoding='utf-8')
    result = external_skill(str(tmp_path), tmp_path)
    assert result['available'] is False


def test_separate_local_checkout_can_be_called(tmp_path: Path):
    repo = tmp_path / 'vishnu'
    other = tmp_path / 'other-app'
    repo.mkdir()
    other.mkdir()
    (other / 'main.py').write_text('print(1)\n', encoding='utf-8')
    result = external_skill(str(other), repo)
    assert result['available'] is True
    assert result['stored_in_vishnu'] is False
    assert result['cloned'] is False
