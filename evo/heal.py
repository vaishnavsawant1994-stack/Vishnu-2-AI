"""Record a repair note. Never patch security files."""

PROTECTED = ('security/', 'core/permissions.py', 'tools/registry.py', 'learning/engine.py')


def repair_note(error: str, path: str) -> dict:
    normalized = path.replace('\\', '/')
    if any(normalized.endswith(item) or item in normalized for item in PROTECTED):
        return {'applied': False, 'reason': 'protected file', 'path': normalized}
    return {
        'applied': False,
        'path': normalized,
        'summary': f'Review {normalized}: {error[:180]}',
        'next': 'owner can apply a code change; the agent only records the note',
    }
