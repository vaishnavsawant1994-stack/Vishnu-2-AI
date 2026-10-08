"""Owner-controlled, isolated application rewrite pipeline.

The package is intentionally excluded from every candidate workspace. Candidate
code is never imported by this owner-kernel package in the host process.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APPLICATION_ROOT = Path(os.environ.get("VISHNU_APP_ROOT", PROJECT_ROOT)).resolve()
DEFAULT_DATA_DIR = Path(os.environ.get("PERSONAL_AI_DATA_DIR", Path.home() / ".vishnu" / "data"))
EXCLUDED_SEGMENTS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules", "vault", "secrets",
    "secret", "credentials", "data", "security", "owner_kernel", "qualification", "rollback", "rewrite",
}
PROTECTED_SEGMENTS = EXCLUDED_SEGMENTS | {"auth", "stop", "tests", ".github"}
PROTECTED_FILES = {"core/permissions.py", "tools/registry.py", "desktop/operator_context.py"}
REWRITE_DIRS = ("rewrite", "baselines", "runs")
TEST_COMMAND = ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]
PHASE0_COMMAND = ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_phase0_executor.py"]
SECURITY_COMMAND = [
    "python", "-m", "pytest", "-q", "-p", "no:cacheprovider",
    "tests/test_registry_unique.py",
    "tests/test_rewrite_security_contract.py",
]
TEST_SUITE_VERSION = "rewrite-tests-v1"
SECURITY_SUITE_VERSION = "rewrite-security-v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def excluded(relative: Path) -> bool:
    if Path(relative).as_posix() in PROTECTED_FILES:
        return True
    for part in relative.parts:
        lowered = part.lower()
        if lowered in EXCLUDED_SEGMENTS or lowered.startswith(".env"):
            return True
    return False


def tree_hashes(root: Path) -> dict[str, str]:
    root = Path(root).resolve()
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if excluded(relative) or path.is_symlink() or not path.is_file():
            continue
        result[relative.as_posix()] = digest_file(path)
    return result


def copy_application(source: Path, destination: Path) -> None:
    """Copy regular application files only; never follow source symlinks."""
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    for current, dirs, names in os.walk(source, followlinks=False):
        current_path = Path(current)
        relative_dir = current_path.relative_to(source)
        dirs[:] = [
            name for name in dirs
            if not excluded(relative_dir / name)
            and not (current_path / name).is_symlink()
        ]
        for name in names:
            src = current_path / name
            relative = src.relative_to(source)
            if excluded(relative) or src.is_symlink() or not src.is_file():
                continue
            dst = destination / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def json_write(path: Path, value: dict, *, exclusive: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if exclusive else "w"
    with path.open(mode, encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def json_read(path: Path) -> dict:
    with Path(path).open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def data_root(data_dir: Path | None = None) -> Path:
    return Path(data_dir).resolve() if data_dir is not None else DEFAULT_DATA_DIR.resolve()


def rewrite_root(data_dir: Path | None = None) -> Path:
    return data_root(data_dir) / "rewrite"


def _checked_id(value: str) -> str:
    identifier = str(value)
    if re.fullmatch(r"[a-f0-9]{32}", identifier) is None:
        raise ValueError("rewrite identifiers must be 32 lowercase hex characters")
    return identifier


def baseline_dir(data_dir: Path | None, baseline_id: str) -> Path:
    return rewrite_root(data_dir) / "baselines" / _checked_id(baseline_id)


def run_dir(data_dir: Path | None, run_id: str) -> Path:
    return rewrite_root(data_dir) / "runs" / _checked_id(run_id)


def actual_isolation() -> str:
    """CONTAINER means the configured isolated test image can actually start."""
    image = os.environ.get("VISHNU_REWRITE_CONTAINER_IMAGE", "").strip()
    docker = shutil.which("docker")
    if not image or not docker:
        return "WORKSPACE"
    try:
        result = subprocess.run(
            [docker, "image", "inspect", image],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "WORKSPACE"
    return "CONTAINER" if result.returncode == 0 else "WORKSPACE"


def required_isolation() -> str:
    value = os.environ.get("VISHNU_REWRITE_REQUIRED_ISOLATION", "CONTAINER").upper().strip()
    if value not in {"WORKSPACE", "CONTAINER"}:
        raise ValueError("VISHNU_REWRITE_REQUIRED_ISOLATION must be WORKSPACE or CONTAINER")
    return value


def isolation_satisfied(required: str, actual: str) -> bool:
    levels = {"WORKSPACE": 1, "CONTAINER": 2}
    return levels.get(actual, 0) >= levels.get(required, 99)


def make_read_only(root: Path) -> None:
    root = Path(root)
    for path in root.rglob("*"):
        try:
            path.chmod(0o555 if path.is_dir() else 0o444)
        except OSError:
            pass
    try:
        root.chmod(0o555)
    except OSError:
        pass


def append_audit(data_dir: Path | None, event: dict) -> None:
    path = rewrite_root(data_dir) / "audit.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"at": now(), **event}
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def safe_app_path(app_root: Path, relative: str) -> Path:
    text = str(relative)
    candidate = Path(text)
    if not text or candidate.is_absolute() or any(part in {"", ".", ".."} for part in text.replace("\\", "/").split("/")):
        raise ValueError("candidate path must be a safe relative path")
    if excluded(candidate) or any(part.lower() in PROTECTED_SEGMENTS for part in candidate.parts):
        raise PermissionError("candidate path is protected")
    root = Path(app_root).resolve()
    target = (root / candidate).resolve()
    if target != root and root not in target.parents:
        raise PermissionError("candidate path escapes the rewrite workspace")
    probe = root
    for part in candidate.parts:
        probe = probe / part
        if probe.is_symlink():
            raise PermissionError("candidate path crosses a symlink")
    return target
