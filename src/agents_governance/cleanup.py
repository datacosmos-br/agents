"""Fail-closed cleanup for repository-owned generated artifacts."""

from __future__ import annotations

import os
from pathlib import Path


def _remove_tree(path: Path) -> None:
    if path.is_symlink():
        raise RuntimeError(f"refusing to clean symlink: {path}")
    with os.scandir(path) as entries:
        children = list(entries)
    for entry in children:
        child = Path(entry.path)
        if entry.is_symlink():
            raise RuntimeError(f"refusing to clean symlink: {child}")
        if entry.is_dir(follow_symlinks=False):
            _remove_tree(child)
        else:
            child.unlink()
    path.rmdir()


def clean_generated(root: Path) -> tuple[Path, ...]:
    """Remove only the repository's declared, ignored generated surfaces."""

    root = root.resolve()
    candidates = [root / ".waza-cache", root / "results" / "latest"]
    candidates.extend(
        path for path in (root / "skills").rglob("__pycache__") if path.is_dir()
    )
    removed: list[Path] = []
    for path in candidates:
        if not path.exists() and not path.is_symlink():
            continue
        resolved_parent = path.parent.resolve()
        if root != resolved_parent and root not in resolved_parent.parents:
            raise RuntimeError(f"refusing to clean outside repository: {path}")
        _remove_tree(path)
        removed.append(path)
    return tuple(removed)
