from pathlib import Path

from agent.executor import AgentExecutor
from evo.mind import start_goal


class Memory:
    def __init__(self, path):
        self.path = path

    def add_message(self, *args, **kwargs):
        return None

    def audit(self, *args, **kwargs):
        return None


class Events:
    def emit(self, *args, **kwargs):
        return None


class Tools:
    emergency_stop = False


def executor(tmp_path):
    return AgentExecutor(models=None, tools=Tools(), memory=Memory(tmp_path / 'memory.sqlite3'), events=Events())


def test_conflict_enters_replan_once(tmp_path):
    start_goal(tmp_path, 'Get the fix into main', ['pull request merged'], conversation_id='chat-1')
    result = executor(tmp_path).enter_conflict('chat-1', 'wrong base')
    assert result['state'] == 'PLAN'
    assert result['criteria'] == ['pull request merged']
    assert result['context'].startswith('REVISED STEP 2')
    again = executor(tmp_path).enter_conflict('chat-1', 'wrong base')
    assert again['context'].startswith('REVISED STEP 2')
    assert again['goal_changed'] is False


def test_missing_goal_is_blocked(tmp_path):
    result = executor(tmp_path).enter_conflict('chat-1', 'wrong base')
    assert result['state'] == 'BLOCKED'
    assert result['advanced'] is False


def test_stop_does_not_enter_replan(tmp_path):
    start_goal(tmp_path, 'Get the fix into main', ['pull request merged'], conversation_id='chat-1')
    tools = Tools()
    tools.emergency_stop = True
    agent = AgentExecutor(models=None, tools=tools, memory=Memory(tmp_path / 'memory.sqlite3'), events=Events())
    assert agent.enter_conflict('chat-1')['state'] == 'STOPPED'


def test_hook_does_not_execute_the_revised_step():
    source = Path('agent/executor.py').read_text()
    assert 'def enter_conflict' in source
    assert 'advance(' in source
    assert 'tool.handler' not in source[source.find('def enter_conflict'):source.find('def set_learning')]
