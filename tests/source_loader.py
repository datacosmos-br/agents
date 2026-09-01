"""Load catalog scripts for tests without writing beside canonical sources."""

from __future__ import annotations

from pathlib import Path
from types import ModuleType


def load_source_module(name: str, path: Path) -> ModuleType:
    """Compile and execute one source file without importlib bytecode caching."""

    source = path.read_bytes()
    module = ModuleType(name)
    module.__file__ = str(path)
    module.__package__ = ""
    exec(  # noqa: S102 -- test loader executes the explicitly selected source
        compile(source, str(path), "exec", dont_inherit=True), module.__dict__
    )
    return module
