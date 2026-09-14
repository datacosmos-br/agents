"""Shared projection utilities for fixed-point generation verification."""

from __future__ import annotations

import hashlib
from pathlib import Path


def snapshot(root: Path) -> tuple[tuple[str, str], ...]:
    """Return a sorted, content-addressed snapshot of every physical path under root."""
    entries: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError(f"projection contains a non-physical path: {path}")
        digest = (
            "directory"
            if path.is_dir()
            else hashlib.sha256(path.read_bytes()).hexdigest()
        )
        entries.append((relative, digest))
    return tuple(entries)
