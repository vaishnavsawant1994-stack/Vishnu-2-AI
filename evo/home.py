"""Smart-home command record. It does not call a device cloud."""


def home_command(device: str, action: str) -> dict:
    if action not in {'on', 'off', 'set'}:
        raise ValueError('action must be on, off, or set')
    return {'device': device[:80], 'action': action, 'sent': False}
