"""Create a Python package with a function and a test."""

from __future__ import annotations

from evo.coder import write_source


def build_python(work, name: str) -> dict:
    slug = ''.join(ch.lower() if ch.isalnum() else '_' for ch in name).strip('_') or 'tool'
    write_source(work, f'{slug}/__init__.py', '')
    write_source(
        work,
        f'{slug}/core.py',
        f'"""Python module {slug}."""\n\n\ndef run(text: str) -> dict:\n    cleaned = " ".join(text.split())\n    return {{"ok": True, "name": "{slug}", "text": cleaned}}\n',
    )
    write_source(
        work,
        f'{slug}/test_core.py',
        f'from {slug}.core import run\n\n\ndef test_run_cleans_text():\n    assert run("  hello   there ")["text"] == "hello there"\n',
    )
    return {'ok': True, 'tool': 'owner_python_dev', 'package': slug, 'files': [f'{slug}/core.py', f'{slug}/test_core.py']}
