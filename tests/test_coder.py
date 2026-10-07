from pathlib import Path

import pytest

from evo.coder import list_project, read_source, write_source


def test_coder_can_write_and_read_a_module(tmp_path: Path):
    written = write_source(tmp_path, 'app.py', 'def add(a, b):\n    return a + b\n')
    assert written['ok'] is True
    found = read_source(tmp_path, 'app.py')
    assert 'def add' in found['text']
    assert 'app.py' in list_project(tmp_path)['files']


def test_coder_cannot_edit_stop_or_leave_workspace(tmp_path: Path):
    with pytest.raises(ValueError):
        write_source(tmp_path, 'security/vault.py', 'x = 1')
    with pytest.raises(ValueError):
        read_source(tmp_path, '../secret.txt')
