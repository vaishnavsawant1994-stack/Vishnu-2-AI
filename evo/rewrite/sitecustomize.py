"""Pin owner-kernel modules into qualification containers as read-only imports."""
from __future__ import annotations

import importlib.abc
import importlib.util
from pathlib import Path

OWNER = Path("/owner-kernel")
EXACT = {
    "tools.registry": OWNER / "tools" / "registry.py",
    "core.permissions": OWNER / "core" / "permissions.py",
    "desktop.operator_context": OWNER / "desktop" / "operator_context.py",
}


class OwnerKernelFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in EXACT:
            candidate = EXACT[fullname]
            if candidate.is_file():
                return importlib.util.spec_from_file_location(fullname, candidate)
        if fullname == "security" or fullname.startswith("security."):
            suffix = Path(*fullname.split("." )[1:])
            base = OWNER / "security" / suffix
            package = base / "__init__.py"
            if package.is_file():
                return importlib.util.spec_from_file_location(fullname, package, submodule_search_locations=[str(base)])
            module = base.with_suffix(".py")
            if module.is_file():
                return importlib.util.spec_from_file_location(fullname, module)
        return None


import sys
sys.meta_path.insert(0, OwnerKernelFinder())
