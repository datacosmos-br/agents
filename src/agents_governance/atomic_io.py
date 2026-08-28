"""Destination-local atomic publication for canonical text artifacts."""

from __future__ import annotations

import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .cleanup import PreparedPublication, Publication, run_cleanup, run_with_cleanup


@dataclass(frozen=True)
class _TextState:
    destination: Path
    desired: str
    desired_mode: int
    previous: str | None
    previous_mode: int | None


@dataclass
class _StagedText:
    state: _TextState
    candidate: Path
    backup: Path | None
    installed: bool = False


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

    def write() -> Path:
        nonlocal descriptor
        stream = os.fdopen(descriptor, "w", encoding="utf-8")
        descriptor = -1
        with stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        candidate.chmod(mode)
        return candidate

    def cleanup() -> None:
        run_cleanup(
            (
                lambda: os.close(descriptor) if descriptor >= 0 else None,
                lambda: discard_physical_file(candidate),
            )
        )

    return run_with_cleanup(write, cleanup)


def atomic_write_text(destination: Path, text: str, *, mode: int = 0o644) -> None:
    """Publish text by atomic replacement while preserving an existing owner."""

    candidate = stage_text(destination, text, mode=mode)
    run_with_cleanup(
        lambda: candidate.replace(destination),
        lambda: discard_physical_file(candidate),
    )


def _current_text(destination: Path) -> tuple[str | None, int | None]:
    if destination.is_symlink():
        raise RuntimeError(f"text publication destination is a symlink: {destination}")
    if not destination.exists():
        return None, None
    metadata = destination.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(
            f"text publication destination is not a regular file: {destination}"
        )
    return destination.read_text(encoding="utf-8"), stat.S_IMODE(metadata.st_mode)


def text_publication(
    destination: Path, text: str, *, mode: int = 0o644
) -> Publication | None:
    """Prepare one changed text owner for a shared atomic publication set."""

    previous, previous_mode = _current_text(destination)
    desired_mode = previous_mode if previous_mode is not None else mode
    if (previous, previous_mode) == (text, desired_mode):
        return None
    state = _TextState(destination, text, desired_mode, previous, previous_mode)

    def prepare() -> PreparedPublication:
        candidate = stage_text(destination, text, mode=desired_mode)
        backup: Path | None = None

        def stage_backup() -> _StagedText:
            nonlocal backup
            if previous is not None:
                assert previous_mode is not None
                backup = stage_text(destination, previous, mode=previous_mode)
            return _StagedText(state, candidate, backup)

        staged = run_with_cleanup(
            stage_backup,
            lambda: run_cleanup(
                (
                    lambda: discard_physical_file(candidate),
                    lambda: (
                        discard_physical_file(backup) if backup is not None else None
                    ),
                )
            ),
        )

        def publish() -> None:
            current = _current_text(destination)
            if current != (state.previous, state.previous_mode):
                raise RuntimeError(
                    f"text publication changed after preflight: {destination}"
                )
            staged.candidate.replace(destination)
            staged.installed = True

        def rollback() -> None:
            if not staged.installed:
                return
            if _current_text(destination) != (state.desired, state.desired_mode):
                raise RuntimeError(
                    f"installed text changed before rollback: {destination}"
                )
            if staged.backup is None:
                destination.unlink()
            else:
                staged.backup.replace(destination)
            staged.installed = False

        def cleanup() -> None:
            run_cleanup(
                (
                    lambda: discard_physical_file(staged.candidate),
                    lambda: (
                        discard_physical_file(staged.backup)
                        if staged.backup is not None
                        else None
                    ),
                )
            )

        return PreparedPublication(publish, rollback, cleanup)

    return Publication(prepare)
