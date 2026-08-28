"""Project-owned authorization boundary for tracked agent projection."""

from __future__ import annotations

from pathlib import Path

PROJECT_SELECTION = Path(".agents/projection.json")


def project_projection_authorized(project: Path) -> bool:
    """Return explicit project authorization or raise on an ambiguous owner."""

    path = project / PROJECT_SELECTION
    if not path.exists() and not path.is_symlink():
        return False
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"projection selection must be a physical file: {path}")
    return True


__all__ = ("PROJECT_SELECTION", "project_projection_authorized")
