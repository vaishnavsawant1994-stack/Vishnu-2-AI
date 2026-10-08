"""The real local registry rejects duplicate names before tools are exposed."""
from pathlib import Path
from types import SimpleNamespace

from tools.evo_tools import register
from tools.registry import ToolRegistry


def test_real_evo_registry_has_unique_names(tmp_path):
    settings = SimpleNamespace(autonomy_mode="ask", data_dir=tmp_path, base_dir=Path.cwd())
    registry = ToolRegistry(settings)
    register(registry, settings)
    names = [tool.name for tool in registry.all()]
    assert len(names) == len(set(names))
    assert "workspace_python_run" in names
    assert names.count("sandbox_run") == 1
