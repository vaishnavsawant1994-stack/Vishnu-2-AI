"""Legal mind states. A replan returns to plan. It does not replan again."""

TRANSITIONS = {
    'PLAN': {'EXECUTE'},
    'EXECUTE': {'VERIFY', 'BLOCKED', 'STOPPED'},
    'VERIFY': {'RECONCILE'},
    'RECONCILE': {'DECIDE'},
    'DECIDE': {'PLAN', 'REPLAN', 'BLOCKED', 'WAITING', 'COMPLETE'},
    'REPLAN': {'PLAN', 'BLOCKED'},
    'STOPPED': {'STOPPED'},
}


def allow(current: str, nxt: str) -> dict:
    legal = nxt in TRANSITIONS.get(current, set())
    return {'ok': legal, 'current': current, 'next': nxt, 'reason': 'allowed' if legal else 'illegal transition'}
