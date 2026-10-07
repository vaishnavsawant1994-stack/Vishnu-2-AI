"""Actions that run on the machine where Vishnu-2 is started."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path

from skills.forge import forge


def snapshot() -> dict:
    return {
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine(),
        'python': platform.python_version(),
        'hostname': platform.node(),
        'cwd': os.getcwd(),
    }


def processes(limit: int = 8) -> dict:
    system = platform.system().lower()
    if system == 'windows':
        command = ['powershell', '-NoProfile', '-Command', 'Get-Process | Sort-Object CPU -Descending | Select-Object -First 8 Name,Id | Format-Table -HideTableHeaders']
    else:
        command = ['ps', '-eo', 'pid,comm', '--sort=-pcpu']
    try:
        run = subprocess.run(command, capture_output=True, text=True, timeout=8)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'ok': False, 'error': str(exc), 'rows': []}
    rows = [line.strip() for line in run.stdout.splitlines() if line.strip()][:limit]
    return {'ok': run.returncode == 0, 'rows': rows, 'system': system}


def set_volume(percent: int) -> dict:
    percent = max(0, min(100, int(percent)))
    system = platform.system().lower()
    if system == 'windows':
        command = ['powershell', '-NoProfile', '-Command', f'(New-Object -ComObject WScript.Shell).SendKeys([char]173)']
        return {'ok': False, 'system': system, 'percent': percent, 'reason': 'Windows volume needs the desktop session; use the Settings app volume slider'}
    if shutil.which('pactl'):
        run = subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{percent}%'], capture_output=True, text=True, timeout=8)
        return {'ok': run.returncode == 0, 'system': system, 'percent': percent, 'error': run.stderr.strip()}
    if shutil.which('osascript'):
        run = subprocess.run(['osascript', '-e', f'set volume output volume {percent}'], capture_output=True, text=True, timeout=8)
        return {'ok': run.returncode == 0, 'system': system, 'percent': percent, 'error': run.stderr.strip()}
    return {'ok': False, 'system': system, 'percent': percent, 'reason': 'no supported volume control on this machine'}


def make_skill(goal: str, root: Path | None = None) -> dict:
    return forge(goal, root or Path.cwd())
