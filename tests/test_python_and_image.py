from pathlib import Path

from evo.image_tool import create_image
from evo.python_tool import run_python


def test_python_runs_a_print_and_blocks_the_vault():
    assert '3' in run_python('print(1 + 2)')['stdout']
    blocked = run_python('import security.vault')
    assert blocked['ok'] is False


def test_image_file_is_created(tmp_path: Path):
    made = create_image('Evening note', tmp_path)
    assert made['ok'] is True
    assert Path(made['path']).exists()
