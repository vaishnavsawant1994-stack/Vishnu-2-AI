"""One dispatcher for the added idea surfaces."""

from __future__ import annotations

from evo.circuit import connection_plan
from evo.desktop import desktop_plan
from evo.geo import route_plan
from evo.heal import repair_note
from evo.home import home_command
from evo.media import music_command
from evo.phone import screen_call
from evo.providers import provider_card
from evo.trace import ExecutionTrace

SURFACES = (
    'circuit',
    'heal',
    'trace',
    'geo',
    'music',
    'providers',
    'desktop',
    'home',
    'phone',
    'forge',
)


def handle(kind: str, payload: dict) -> dict:
    kind = kind.strip().lower()
    if kind not in SURFACES:
        raise KeyError(kind)
    if kind == 'circuit':
        return connection_plan(payload['board'], payload['part'])
    if kind == 'heal':
        return repair_note(payload['error'], payload.get('path', 'evo/hub.py'))
    if kind == 'trace':
        trace = ExecutionTrace()
        trace.add(payload.get('step', 'plan'), payload.get('detail', ''))
        return trace.export()
    if kind == 'geo':
        return route_plan(payload['origin'], payload['destination'])
    if kind == 'music':
        return music_command(payload['text'])
    if kind == 'providers':
        return provider_card(payload['name'], bool(payload.get('configured')))
    if kind == 'desktop':
        return desktop_plan(payload['action'])
    if kind == 'home':
        return home_command(payload['device'], payload['action'])
    if kind == 'phone':
        return screen_call(payload['caller'], payload.get('note', ''))
    return {'surface': 'forge', 'status': 'use skills.forge'}
