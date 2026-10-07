"""Music command parser. It does not store or call a music account."""


def music_command(text: str) -> dict:
    lowered = text.strip().lower()
    if lowered.startswith('play '):
        return {'action': 'play', 'query': text.strip()[5:], 'connected': False}
    if lowered in {'pause', 'next', 'previous'}:
        return {'action': lowered, 'query': '', 'connected': False}
    return {'action': 'unknown', 'query': text, 'connected': False}
