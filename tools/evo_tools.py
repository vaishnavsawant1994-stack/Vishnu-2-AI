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
from evo.owner_tools import owner_code, owner_math, owner_search
from evo.python_tool import run_python
from evo.image_tool import create_image
from evo.download_tool import download_file
from evo.read_tool import read_anything
from evo.vision_tool import describe_image
from evo.phone_screen import add_line, append_audio, capture_audio, finish_screen, start_screen
from evo.workspace_memory import recall, remember
from evo.debugger import debug_project
from evo.desktop_open import open_file
from evo.board import add_agent, add_task, design_check, list_agents, list_tasks, recall, retain, storyboard, topic_script, update_task
from evo.coder import list_project, read_source, run_project, write_source
from evo.fullstack import build_app
from evo.python_dev import build_python
from evo.senior_python import build_senior
from evo.senior_fullstack import build_senior_stack
from evo.media import music_command
from evo.phone import screen_call
from tools.registry import Risk, Tool


def register(reg, settings, models=None):
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

    def own_math(payload):
        return owner_math(str(payload.get('expression') or '0'))
    def own_code(payload):
        return owner_code(str(payload.get('source') or ''))
    def own_search(payload):
        return owner_search(str(payload.get('query') or ''))
    reg.register(Tool('owner_math', 'Vaishnav math tool: arithmetic only', own_math, Risk.READ_ONLY))
    reg.register(Tool('owner_code', 'Vaishnav code tool: pure expression, no files or imports', own_code, Risk.READ_ONLY))
    reg.register(Tool('owner_search', 'Vaishnav search tool: public web titles', own_search, Risk.READ_ONLY))

    def own_python(payload):
        return run_python(str(payload.get('source') or ''))
    def own_image(payload):
        return create_image(str(payload.get('title') or 'Vishnu-2'), Path(settings.data_dir) / 'images')
    reg.register(Tool('owner_python', 'Run a short Python snippet in a subprocess', own_python, Risk.REVERSIBLE))
    reg.register(Tool('owner_image', 'Create a PNG image file from a title', own_image, Risk.REVERSIBLE))

    def own_download(payload):
        return download_file(str(payload.get('url') or ''), Path(getattr(settings, 'data_dir', root)))
    reg.register(Tool('owner_download', 'Download a public HTTPS file into the data folder, max 2 GB', own_download, Risk.EXTERNAL_SIDE_EFFECT))

    def own_read(payload):
        return read_anything(str(payload.get('target') or ''), Path(getattr(settings, 'data_dir', root)))
    reg.register(Tool('owner_read', 'Read a website, text file, PDF, or image', own_read, Risk.READ_ONLY))

    def own_vision(payload):
        return describe_image(str(payload.get('path') or ''), str(payload.get('question') or ''), models)
    reg.register(Tool('owner_vision', 'Describe an image with the configured vision model', own_vision, Risk.READ_ONLY))

    def phone_start(payload):
        return start_screen(str(payload.get('caller') or 'unknown'), Path(getattr(settings, 'data_dir', root)))
    def phone_line(payload):
        return add_line(str(payload.get('call_id') or ''), str(payload.get('speaker') or 'caller'), str(payload.get('text') or ''), Path(getattr(settings, 'data_dir', root)))
    def phone_finish(payload):
        return finish_screen(str(payload.get('call_id') or ''), Path(getattr(settings, 'data_dir', root)))
    reg.register(Tool('phone_screen_start', 'Start screening a call and open a transcript', phone_start, Risk.EXTERNAL_SIDE_EFFECT))
    reg.register(Tool('phone_screen_line', 'Add a caller or Vishnu line to the screened call', phone_line, Risk.READ_ONLY))
    def phone_capture(payload):
        raw = payload.get('audio') or b''
        if isinstance(raw, str):
            raw = raw.encode('utf-8')
        return capture_audio(str(payload.get('call_id') or ''), Path(getattr(settings, 'data_dir', root)), bytes(raw), int(payload.get('seconds') or 5))
    reg.register(Tool('phone_screen_finish', 'Finish the screened call and return the transcript and summary', phone_finish, Risk.READ_ONLY))
    reg.register(Tool('phone_screen_capture', 'Store a live audio clip on the screened call', phone_capture, Risk.EXTERNAL_SIDE_EFFECT))

    def coder_list(_):
        return list_project(Path(getattr(settings, 'data_dir', root)))
    def coder_read(payload):
        return read_source(Path(getattr(settings, 'data_dir', root)), str(payload.get('path') or ''))
    def coder_write(payload):
        return write_source(Path(getattr(settings, 'data_dir', root)), str(payload.get('path') or ''), str(payload.get('text') or ''))
    def coder_test(payload):
        return run_project(Path(getattr(settings, 'data_dir', root)), str(payload.get('path') or ''))
    reg.register(Tool('coder_list', 'List files in the coding workspace', coder_list, Risk.READ_ONLY))
    reg.register(Tool('coder_read', 'Read a source file in the coding workspace', coder_read, Risk.READ_ONLY))
    reg.register(Tool('coder_write', 'Write a source file in the coding workspace', coder_write, Risk.REVERSIBLE))
    reg.register(Tool('coder_test', 'Run pytest in the coding workspace', coder_test, Risk.REVERSIBLE))

    def fullstack(payload):
        return build_app(Path(getattr(settings, 'data_dir', root)), str(payload.get('name') or 'app'))
    reg.register(Tool('fullstack_build', 'Create a page, Flask API, and SQLite app in the coding workspace', fullstack, Risk.REVERSIBLE))

    def python_dev(payload):
        return build_python(Path(getattr(settings, 'data_dir', root)), str(payload.get('name') or 'tool'))
    reg.register(Tool('python_develop', 'Create a Python package, function, and test in the coding workspace', python_dev, Risk.REVERSIBLE))

    def senior(payload):
        return build_senior(Path(getattr(settings, 'data_dir', root)), str(payload.get('name') or 'service'))
    reg.register(Tool('senior_python', 'Create a typed Python service with validation, errors, and failure tests', senior, Risk.REVERSIBLE))

    def senior_stack(payload):
        return build_senior_stack(Path(getattr(settings, 'data_dir', root)), str(payload.get('name') or 'app'))
    reg.register(Tool('senior_fullstack', 'Create a reviewed page, API, database, and failure tests', senior_stack, Risk.REVERSIBLE))

    def memory_add(payload):
        return remember(Path(getattr(settings, 'data_dir', root)), str(payload.get('kind') or 'note'), str(payload.get('text') or ''))
    def memory_list(_):
        return recall(Path(getattr(settings, 'data_dir', root)))
    def debug(payload):
        return debug_project(Path(getattr(settings, 'data_dir', root)), str(payload.get('path') or ''))
    def desktop_open(payload):
        return open_file(str(payload.get('path') or ''))
    def phone_stream(payload):
        raw = payload.get('chunk') or b''
        if isinstance(raw, str):
            raw = raw.encode('utf-8')
        return append_audio(str(payload.get('call_id') or ''), Path(getattr(settings, 'data_dir', root)), bytes(raw))
    reg.register(Tool('workspace_remember', 'Remember a coding workspace note', memory_add, Risk.READ_ONLY))
    reg.register(Tool('workspace_recall', 'Recall coding workspace notes', memory_list, Risk.READ_ONLY))
    reg.register(Tool('coder_debug', 'Run a workspace test and record the failure', debug, Risk.REVERSIBLE))
    reg.register(Tool('desktop_open', 'Open a file with the machine default app', desktop_open, Risk.EXTERNAL_SIDE_EFFECT))
    reg.register(Tool('phone_screen_stream', 'Append a live audio chunk to a screened call', phone_stream, Risk.EXTERNAL_SIDE_EFFECT))

    def task_add(payload):
        return add_task(Path(getattr(settings, 'data_dir', root)), str(payload.get('title') or 'task'))
    def task_list(_):
        return list_tasks(Path(getattr(settings, 'data_dir', root)))
    def agent_add(payload):
        return add_agent(Path(getattr(settings, 'data_dir', root)), str(payload.get('name') or 'agent'), str(payload.get('role') or 'worker'))
    def memory_retain(payload):
        return retain(Path(getattr(settings, 'data_dir', root)), str(payload.get('text') or ''))
    def memory_recall(payload):
        return recall(Path(getattr(settings, 'data_dir', root)), str(payload.get('query') or ''))
    def design(payload):
        return design_check(str(payload.get('text') or ''))
    def board_story(payload):
        return storyboard(str(payload.get('title') or 'story'))
    def script(payload):
        return topic_script(str(payload.get('topic') or 'topic'))
    reg.register(Tool('task_add', 'Add a work task', task_add, Risk.READ_ONLY))
    reg.register(Tool('task_list', 'List work tasks', task_list, Risk.READ_ONLY))
    def task_update(payload):
        return update_task(Path(getattr(settings, 'data_dir', root)), int(payload.get('id') or 0), str(payload.get('status') or 'open'))
    def agent_list(_):
        return list_agents(Path(getattr(settings, 'data_dir', root)))
    reg.register(Tool('task_update', 'Move a task to open, doing, or done', task_update, Risk.READ_ONLY))
    reg.register(Tool('agent_list', 'List the agent roster', agent_list, Risk.READ_ONLY))
    reg.register(Tool('agent_add', 'Add an agent to the roster', agent_add, Risk.READ_ONLY))
    reg.register(Tool('memory_retain', 'Store a learned memory', memory_retain, Risk.READ_ONLY))
    reg.register(Tool('memory_recall', 'Recall a learned memory by words', memory_recall, Risk.READ_ONLY))
    reg.register(Tool('design_check', 'Check a design note for heading, action, and failure', design, Risk.READ_ONLY))
    reg.register(Tool('storyboard', 'Write an HTML storyboard without rendering video', board_story, Risk.READ_ONLY))
    reg.register(Tool('topic_script', 'Write a narration script without making a video', script, Risk.READ_ONLY))
