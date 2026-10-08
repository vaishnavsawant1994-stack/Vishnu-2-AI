"""A bounded, persistent first skill: extract actionable checklist lines.

No arbitrary generated Python is executed. A vetted skill template is qualified
against held-out examples in a separate isolated Python interpreter.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ID = "extract_action_items_v1"
SOURCE = '''def run(payload):
    text = payload["text"]
    items = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- [ ] "):
            task = line[6:].strip()
            if task:
                items.append(task)
    return {"items": items}
'''
PROBE = """import json, sys
ns = {"__builtins__": {"str": str}}
exec(compile(json.loads(sys.stdin.readline()), "<qualified-skill>", "exec"), ns)
cases = json.loads(sys.stdin.readline())
print(json.dumps([ns["run"](case) for case in cases]))
"""
CASES = [
    ({"text": "- [ ] Send report\n- [x] Done\n- [ ] Review draft"}, {"items": ["Send report", "Review draft"]}),
    ({"text": "Notes\n- [ ] Call supplier\n- [ ]  "}, {"items": ["Call supplier"]}),
    ({"text": "Nothing actionable"}, {"items": []}),
]


def _folder(data_dir: Path) -> Path:
    return Path(data_dir) / "skills" / "qualified"


def _qualify(source: str) -> bool:
    # The candidate is the fixed, audited template, not arbitrary model output.
    if source != SOURCE:
        return False
    inputs = [item[0] for item in CASES]
    expected = [item[1] for item in CASES]
    proc = subprocess.run(
        [sys.executable, "-I", "-c", PROBE],
        input=json.dumps(source) + "\\n" + json.dumps(inputs) + "\\n",
        capture_output=True, text=True, timeout=8,
        env={"PATH": os.environ.get("PATH", "")},
    )
    return proc.returncode == 0 and json.loads(proc.stdout) == expected


def execute_action_items(data_dir: Path, text: str) -> dict:
    """Qualify once, persist, and reuse after restart; reject tampered skills."""
    if not isinstance(text, str) or len(text) > 100_000:
        raise ValueError("text must be a string of at most 100000 characters")
    folder = _folder(data_dir)
    path = folder / (SKILL_ID + ".json")
    created = False
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("skill_id") != SKILL_ID or saved.get("sha256") != hashlib.sha256(SOURCE.encode()).hexdigest() or saved.get("source") != SOURCE:
            raise ValueError("stored skill failed integrity verification")
    else:
        if not _qualify(SOURCE):
            raise RuntimeError("candidate failed independent qualification")
        folder.mkdir(parents=True, exist_ok=True)
        record = {"skill_id": SKILL_ID, "source": SOURCE, "sha256": hashlib.sha256(SOURCE.encode()).hexdigest()}
        fd, temporary = tempfile.mkstemp(prefix=".skill-", dir=folder)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(record, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        created = True
    result = subprocess.run(
        [sys.executable, "-I", "-c", PROBE],
        input=json.dumps(SOURCE) + "\\n" + json.dumps([{"text": text}]) + "\\n",
        capture_output=True, text=True, timeout=8,
        env={"PATH": os.environ.get("PATH", "")},
    )
    if result.returncode:
        raise RuntimeError("qualified skill execution failed")
    return {"skill_id": SKILL_ID, "forged": created, "reused": not created, "result": json.loads(result.stdout)[0]}
