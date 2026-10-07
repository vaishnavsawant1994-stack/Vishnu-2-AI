"""Open a file with the machine's default application."""

from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path


def open_file(path: str) -> dict:
    target = Path(path).expanduser()
    if not target.exists():
        return {'ok': False, 'tool': 'owner_desktop', 'reason': 'file not found'}
    system = platform.system().lower()
    if system == 'windows':
        command = ['cmd', '/c', 'start', '', str(target)]
    elif system == 'darwin':
        command = ['open', str(target)]
    elif shutil.which('xdg-open'):
        command = ['xdg-open', str(target)]
    else:
        return {'ok': False, 'tool': 'owner_desktop', 'reason': 'no opener on this machine'}
    subprocess.Popen(command)
    return {'ok': True, 'tool': 'owner_desktop', 'path': str(target), 'system': system}
