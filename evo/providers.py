"""Provider setup cards. Secrets are flags, never stored here."""


def provider_card(name: str, configured: bool) -> dict:
    return {
        'name': name.strip()[:80],
        'configured': configured,
        'secret_stored': False,
        'test': 'not run',
    }
