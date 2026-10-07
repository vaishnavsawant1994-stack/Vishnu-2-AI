"""Scaffold a reviewed Python module, not a one-line function."""

from __future__ import annotations

from evo.coder import write_source


def build_senior(work, name: str) -> dict:
    slug = ''.join(ch.lower() if ch.isalnum() else '_' for ch in name).strip('_') or 'service'
    write_source(work, f'{slug}/__init__.py', '')
    write_source(
        work,
        f'{slug}/service.py',
        f'''"""Reviewed {slug} service."""

from __future__ import annotations


class InputError(ValueError):
    pass


def run(text: str) -> dict:
    if not isinstance(text, str):
        raise InputError('text must be a string')
    cleaned = ' '.join(text.split())
    if not cleaned:
        raise InputError('text is required')
    if len(cleaned) > 500:
        raise InputError('text is too long')
    return {{'ok': True, 'name': '{slug}', 'text': cleaned, 'length': len(cleaned)}}
''',
    )
    write_source(
        work,
        f'{slug}/test_service.py',
        f'''import pytest

from {slug}.service import InputError, run


def test_run_cleans_and_counts():
    result = run('  hello   there ')
    assert result['text'] == 'hello there'
    assert result['length'] == 11


def test_run_rejects_empty_and_non_text():
    with pytest.raises(InputError):
        run('   ')
    with pytest.raises(InputError):
        run(None)
''',
    )
    write_source(
        work,
        f'{slug}/DESIGN.md',
        f'# {slug}\n\nValidate input before work. Raise InputError for empty, non-text, and over-long values. Return a small result dict.\n',
    )
    return {
        'ok': True,
        'tool': 'owner_senior_python',
        'package': slug,
        'checks': ['types', 'validation', 'errors', 'failure tests', 'design note'],
    }
