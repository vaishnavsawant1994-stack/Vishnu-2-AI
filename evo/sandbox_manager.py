"""An experiment workspace. It does not inherit the vault and cannot promote itself."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path


def open_sandbox(work: Path, goal: str) -> dict:
    run_id = uuid.uuid4().hex[:12]
    folder = Path(work) / 'sandboxes' / run_id
    folder.mkdir(parents=True)
    (folder / 'workspace').mkdir()
    manifest = {
        'run_id': run_id,
        'goal': goal[:160],
        'filesystem': 'workspace only',
        'vault': 'denied',
        'stop': 'denied',
        'credentials': 'denied',
        'promote': 'qualification required',
        'cpu': 'unset',
        'memory': 'unset',
        'network_policy': 'default deny',
        'network_enforced': 'false',
        'cpu_configured': 'false',
        'memory_configured': 'false',
        'isolation': 'WORKSPACE',
    }
    (folder / 'manifest.txt').write_text('\n'.join(f'{key}: {value}' for key, value in manifest.items()), encoding='utf-8')
    return {'ok': True, 'tool': 'sandbox', 'run_id': run_id, 'path': str(folder), 'vault': 'denied'}


def run_in_sandbox(work: Path, run_id: str, source: str) -> dict:
    folder = Path(work) / 'sandboxes' / run_id / 'workspace'
    if not folder.is_dir():
        return {'ok': False, 'reason': 'sandbox not found'}
    if any(word in source.lower() for word in ('vault', 'emergency_stop', 'credentials')):
        return {'ok': False, 'reason': 'sandbox cannot touch vault, stop, or credentials'}
    script = folder / 'main.py'
    script.write_text(source, encoding='utf-8')
    try:
        run = subprocess.run(
            [sys.executable, str(script)],
            cwd=folder,
            env={'PATH': os.environ.get('PATH', ''), 'PYTHONDONTWRITEBYTECODE': '1'},
            capture_output=True,
            text=True,
            timeout=8,
        )
    except subprocess.TimeoutExpired:
        return {'ok': False, 'reason': 'timed out'}
    return {'ok': run.returncode == 0, 'stdout': run.stdout[-400:], 'promoted': False}


def qualify(claimed_better: bool, evidence_better: bool) -> dict:
    promoted = bool(evidence_better)
    return {
        'ok': True,
        'claimed_better': claimed_better,
        'evidence_better': evidence_better,
        'promoted': promoted,
        'reason': 'qualification evidence' if promoted else 'a claim is not proof',
    }


def compare_baseline(baseline: float, candidate: float, security_passed: bool) -> dict:
    """Compare a frozen baseline with a candidate. The candidate does not supply the scores."""
    better = candidate > baseline and security_passed
    return {
        'ok': True,
        'baseline': baseline,
        'candidate': candidate,
        'security_passed': security_passed,
        'promoted': better,
        'reason': 'independent comparison' if better else 'not better than the frozen baseline',
    }


LEVELS = {'NONE': 0, 'WORKSPACE': 1, 'PROCESS': 2, 'CONTAINER': 3, 'VM': 4, 'REMOTE_ISOLATED': 5}

def require_isolation(required: str, available: str = 'WORKSPACE') -> dict:
    if LEVELS[required] > LEVELS[available]:
        return {'ok': False, 'available': available, 'required': required, 'reason': 'this machine cannot isolate that experiment'}
    return {'ok': True, 'available': available, 'required': required}


def discover_capabilities(container: bool = False, vm: bool = False) -> dict:
    return {
        'available_isolation': 'VM' if vm else 'CONTAINER' if container else 'WORKSPACE',
        'workspace': True,
        'process_limits': False,
        'container': container,
        'vm': vm,
        'cpu_limit': False,
        'memory_limit': False,
        'network_isolation': False,
        'stripped_environment': True,
        'credentials_injected': False,
    }


def admit(required: str, capabilities: dict) -> dict:
    decision = require_isolation(required, capabilities['available_isolation'])
    if not decision['ok']:
        decision['failure'] = 'INSUFFICIENT_ISOLATION'
        decision['downgraded'] = False
    return decision


def qualify_experiment(baseline: float, candidate: float, security_passed: bool, isolation_satisfied: bool) -> dict:
    promoted = candidate > baseline and security_passed and isolation_satisfied
    return {'promoted': promoted, 'reason': 'qualified' if promoted else 'score, security, or isolation failed'}


def respond_to_isolation(required: str, capabilities: dict) -> dict:
    decision = admit(required, capabilities)
    if decision['ok']:
        return {'action': 'run', 'failure': None}
    if not capabilities.get('container') and not capabilities.get('vm'):
        return {'action': 'block', 'failure': 'INSUFFICIENT_ISOLATION', 'install_docker': False, 'goal_changed': False}
    return {'action': 'use_stronger_backend', 'failure': 'INSUFFICIENT_ISOLATION', 'install_docker': False}


def isolation_evidence(required: str, capabilities: dict, baseline: float, candidate: float, security_passed: bool) -> dict:
    satisfied = admit(required, capabilities)['ok']
    return {
        'required_isolation': required,
        'actual_isolation': capabilities['available_isolation'],
        'security_passed': security_passed,
        'baseline': baseline,
        'candidate': candidate,
        'promoted': qualify_experiment(baseline, candidate, security_passed, satisfied)['promoted'],
    }
