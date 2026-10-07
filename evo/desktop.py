"""Desktop action plan. It does not send OS input."""


def desktop_plan(action: str) -> dict:
    allowed = {'volume', 'brightness', 'list-processes', 'arrange-windows'}
    name = action.strip().lower()
    return {'action': name, 'allowed': name in allowed, 'executed': False}
