"""Project-owned authorization boundary for tracked agent projection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_SELECTION = Path(".agents/projection.json")


@dataclass(frozen=True)
class ProjectAuthorization:
    """One immutable project-selection snapshot shared by every projector."""

    project: Path
    path: Path
    payload: bytes | None

    @property
    def selected(self) -> bool:
        return self.payload is not None


def load_project_authorization(project: Path) -> ProjectAuthorization:
    """Read the project selection exactly once before planning any effect."""

    path = project / PROJECT_SELECTION
    if not path.exists() and not path.is_symlink():
        return ProjectAuthorization(project, path, None)
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"projection selection must be a physical file: {path}")
    return ProjectAuthorization(project, path, path.read_bytes())


__all__ = ("PROJECT_SELECTION", "ProjectAuthorization", "load_project_authorization")
