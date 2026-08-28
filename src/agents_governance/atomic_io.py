"""Destination-local atomic publication for canonical text artifacts."""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path


def _symlink_component(path: Path) -> Path | None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            return current
        if not current.exists():
            break
    return None


def discard_physical_file(path: Path) -> None:
    """Remove one exact owned file without following a link."""

    if path.is_symlink():
        raise RuntimeError(f"refusing to discard symlink: {path}")
    if path.exists():
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"refusing to discard non-regular file: {path}")
        path.unlink()


def stage_text(destination: Path, text: str, *, mode: int = 0o644) -> Path:
    """Write and sync one destination-local candidate without publishing it."""

    symlink = _symlink_component(destination)
    if symlink is not None:
        raise RuntimeError(f"publication path symlink forbidden: {symlink}")
    parent = destination.parent
    if not parent.is_dir():
        raise FileNotFoundError(f"publication parent is not a directory: {parent}")
    if destination.exists():
        metadata = destination.lstat()
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(
                f"publication destination is not a regular file: {destination}"
            )
        mode = stat.S_IMODE(metadata.st_mode)

    descriptor, raw_candidate = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".candidate", dir=parent
    )
    candidate = Path(raw_candidate)
    try:
        stream = os.fdopen(descriptor, "w", encoding="utf-8")
        descriptor = -1
        with stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        candidate.chmod(mode)
        return candidate
    except BaseException as error:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            discard_physical_file(candidate)
        except (OSError, RuntimeError) as cleanup_error:
            error.add_note(f"candidate cleanup failed: {cleanup_error}")
            raise error from cleanup_error
        raise


def atomic_write_text(destination: Path, text: str, *, mode: int = 0o644) -> None:
    """Publish text by atomic replacement while preserving an existing owner."""

    candidate = stage_text(destination, text, mode=mode)
    try:
        candidate.replace(destination)
    except BaseException as error:
        try:
            discard_physical_file(candidate)
        except (OSError, RuntimeError) as cleanup_error:
            error.add_note(f"candidate rollback failed: {cleanup_error}")
            raise error from cleanup_error
        raise
