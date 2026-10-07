from pathlib import Path

from evo.image_tool import create_image
from evo.python_tool import run_python


def test_python_runs_in_a_scratch_folder(tmp_path: Path):
    result = run_python('print(2 + 2)', tmp_path)
    assert result['ok'] is True
    assert '4' in result['stdout']
    assert result['tool'] == 'owner_python'


def test_python_times_out(tmp_path: Path):
    result = run_python('while True:\n    pass', tmp_path, timeout=1)
    assert result['ok'] is False
    assert result['reason'] == 'timed out'


def test_image_is_written(tmp_path: Path):
    result = create_image('a gold ring on a dark desk', tmp_path)
    assert result['ok'] is True
    assert Path(result['path']).exists()
    assert result['tool'] == 'owner_image'
