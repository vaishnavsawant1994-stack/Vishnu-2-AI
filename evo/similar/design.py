"""Design review for a page note."""

from __future__ import annotations


def review(text: str) -> dict:
    checks = {
        'heading': text.lstrip().startswith('#'),
        'action': any(word in text.lower() for word in ('click', 'submit', 'choose', 'type')),
        'failure': any(word in text.lower() for word in ('error', 'empty', 'invalid', 'fail')),
        'limit': any(word in text.lower() for word in ('max', 'limit', 'character')),
    }
    return {'ok': all(checks.values()), 'checks': checks, 'missing': [name for name, passed in checks.items() if not passed]}
