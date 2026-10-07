"""Call-screen note. It does not answer a phone."""


def screen_call(caller: str, note: str = '') -> dict:
    return {'caller': caller[:80], 'note': note[:240], 'answered': False, 'transcript': ''}
