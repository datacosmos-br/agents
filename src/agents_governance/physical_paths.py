"""Canonical inspection of repository-local physical path boundaries."""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ("absolute_path", "symlink_component")


def absolute_path(path: Path) -> Path:
    """Return one absolute physical path without resolving links."""

    return Path(os.path.abspath(path))


def symlink_component(path: Path) -> Path | None:
    """Return the first existing symlink component in an absolute path."""

    absolute = absolute_path(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            return current
        if not current.exists():
            break
    return None
