"""Register local idea surfaces as Vishnu tools."""

from __future__ import annotations

from pathlib import Path

from evo.circuit import connection_plan
from evo.geo import route_plan
from evo.heal import repair_note
from evo.home import home_command
from evo.local import make_skill, processes, set_volume, snapshot
from evo.search import search_web
from evo.skills import calculate, check_code, now, read_page
from evo.media import music_command
from evo.phone import screen_call
from tools.registry import Risk, Tool


def register(reg, settings):
    root = Path(getattr(settings, 'base_dir', Path.cwd()))

    def system_snapshot(_):
        return snapshot()

    def system_processes(_):
        return processes()

    def system_volume(payload):
        return set_volume(int(payload.get('percent', 30)))

    def skill_forge(payload):
        return make_skill(str(payload.get('goal') or 'new skill'), root)

    def circuit(payload):
        return connection_plan(str(payload.get('board') or ''), str(payload.get('part') or ''))

    def geo(payload):
        return route_plan(str(payload.get('origin') or ''), str(payload.get('destination') or ''))

    def music(payload):
        return music_command(str(payload.get('text') or ''))

    def heal(payload):
        return repair_note(str(payload.get('error') or ''), str(payload.get('path') or 'evo/local.py'))

    def home(payload):
        return home_command(str(payload.get('device') or 'device'), str(payload.get('action') or 'off'))

    def phone(payload):
        return screen_call(str(payload.get('caller') or 'unknown'), str(payload.get('note') or ''))

    reg.register(Tool('system_snapshot', 'Read this machine name, OS, and Python version', system_snapshot, Risk.READ_ONLY))
    reg.register(Tool('system_processes', 'List the busiest processes on this machine', system_processes, Risk.READ_ONLY))
    reg.register(Tool('system_volume', 'Set output volume when this OS supports it', system_volume, Risk.REVERSIBLE))
    reg.register(Tool('skill_forge', 'Write and test a new local skill', skill_forge, Risk.REVERSIBLE))
    reg.register(Tool('circuit_plan', 'Return a known board and part wiring plan', circuit, Risk.READ_ONLY))
    reg.register(Tool('route_plan', 'Return a known city-to-city route plan', geo, Risk.READ_ONLY))
    reg.register(Tool('music_command', 'Parse a music command without contacting an account', music, Risk.READ_ONLY))
    reg.register(Tool('repair_note', 'Record a repair note without patching security files', heal, Risk.READ_ONLY))
    reg.register(Tool('home_command', 'Record a home command without sending it', home, Risk.READ_ONLY))
    reg.register(Tool('call_note', 'Record a call-screen note without answering the phone', phone, Risk.READ_ONLY))
    def external(_):
        return external_status(__import__('os').getenv('BRAHMA_HOME'), root)
    reg.register(Tool('external_app_status', 'Check a separately installed local app without copying it', external, Risk.READ_ONLY))
    def web_search(payload):
        return search_web(str(payload.get('query') or ''))
    reg.register(Tool('web_search', 'Search the public web and return result titles', web_search, Risk.READ_ONLY))
    def calc(payload):
        return calculate(str(payload.get('expression') or '0'))
    def clock(_):
        return now()
    def page(payload):
        return read_page(str(payload.get('url') or ''))
    reg.register(Tool('calculate', 'Evaluate an arithmetic expression', calc, Risk.READ_ONLY))
    reg.register(Tool('current_time', 'Return the current UTC time', clock, Risk.READ_ONLY))
    reg.register(Tool('read_page', 'Read public text from an https page', page, Risk.READ_ONLY))
    def code(payload):
        return check_code(str(payload.get('source') or ''))
    reg.register(Tool('code_check', 'Check and run a pure expression; imports and file access are blocked', code, Risk.READ_ONLY))
