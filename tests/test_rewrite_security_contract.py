"""Security probes pinned outside candidate-controlled application writes."""
from types import SimpleNamespace

import pytest

from agent.executor import AgentExecutor
from core.permissions import PermissionEngine
from evo.mind import interrupt_step, start_goal
from evo.recover import recover
from tools.registry import Risk, Tool, ToolRegistry


class Memory:
    def __init__(self, path):
        self.path = path
    def audit(self, *args, **kwargs):
        return None


class Events:
    def emit(self, *args, **kwargs):
        return None


def test_stop_blocks_execution_before_handler_dispatch(tmp_path):
    calls = []
    tools = SimpleNamespace(emergency_stop=True)
    executor = object.__new__(AgentExecutor)
    executor.tools = tools
    executor.events = Events()
    executor.memory = Memory(tmp_path / "memory.sqlite3")
    executor.telemetry = None
    with pytest.raises(PermissionError, match="emergency stop"):
        executor._execute_step("run", 0, SimpleNamespace(name="probe", handler=lambda _: calls.append(1)), {}, {})
    assert calls == []


def test_permission_denial_does_not_execute_handler(tmp_path):
    calls = []
    settings = SimpleNamespace(autonomy_mode="ask", data_dir=tmp_path)
    registry = ToolRegistry(settings)
    tool = Tool("probe", "test", lambda _: calls.append(1), Risk.REVERSIBLE)
    registry.register(tool)
    decision = registry.authorize(tool, confirmed=False, parameters={})
    assert not decision.allowed
    assert PermissionEngine("ask").decide(int(Risk.REVERSIBLE)).allowed is False
    assert calls == []


def test_restart_recovery_does_not_repeat_finished_step(tmp_path):
    start = start_goal(tmp_path, "Complete one operation", ["verified"], conversation_id="rewrite-test")
    assert start["ok"]
    interrupted = interrupt_step(tmp_path, start["id"], "send the operation", "operation-1")
    assert interrupted["state"] == "INTERRUPTED"
    result = recover(tmp_path, "rewrite-test", {"operation-1": True})
    assert result["ok"] is True
    assert result["repeated"] is False
    assert result["state"] == "VERIFIED"
