"""Test fixtures that obey repository-local scratch policy."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
from collections.abc import Iterator
from pathlib import Path

import pytest

type _DirectoryIdentity = tuple[int, int]


def _identity(metadata: os.stat_result) -> _DirectoryIdentity:
    return metadata.st_dev, metadata.st_ino


def _empty_owned_directory(directory_fd: int) -> None:
    """Delete entries through the pinned directory, never through its pathname."""

    with os.scandir(directory_fd) as entries:
        snapshot = list(entries)
    for entry in snapshot:
        try:
            if entry.is_dir(follow_symlinks=False):
                shutil.rmtree(entry.name, dir_fd=directory_fd)
            else:
                os.unlink(entry.name, dir_fd=directory_fd)
        except FileNotFoundError:
            continue


def _remove_owned_directory(owned: Path, expected: _DirectoryIdentity) -> None:
    """Remove only the original physical fixture directory."""

    try:
        current = owned.stat(follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISDIR(current.st_mode):
        raise RuntimeError(f"test scratch must remain the original directory: {owned}")
    if _identity(current) != expected:
        raise RuntimeError(f"test scratch identity changed: {owned}")

    parent_fd = os.open(
        owned.parent,
        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
    )
    directory_fd: int | None = None
    try:
        try:
            directory_fd = os.open(
                owned.name,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=parent_fd,
            )
        except OSError as error:
            raise RuntimeError(f"test scratch identity changed: {owned}") from error
        pinned = os.fstat(directory_fd)
        if not stat.S_ISDIR(pinned.st_mode):
            raise RuntimeError(
                f"test scratch must remain the original directory: {owned}"
            )
        if _identity(pinned) != expected:
            raise RuntimeError(f"test scratch identity changed: {owned}")
        _empty_owned_directory(directory_fd)
        try:
            current = os.stat(owned.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError as error:
            raise RuntimeError(f"test scratch identity changed: {owned}") from error
        if not stat.S_ISDIR(current.st_mode):
            raise RuntimeError(
                f"test scratch must remain the original directory: {owned}"
            )
        if _identity(current) != expected:
            raise RuntimeError(f"test scratch identity changed: {owned}")
        try:
            os.rmdir(owned.name, dir_fd=parent_fd)
        except FileNotFoundError as error:
            raise RuntimeError(f"test scratch identity changed: {owned}") from error
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
        os.close(parent_fd)


@pytest.fixture
def tmp_path(
    tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest
) -> Iterator[Path]:
    """Create one deterministic test directory without pytest's current symlink."""

    identity = hashlib.sha256(request.node.nodeid.encode()).hexdigest()
    owned = tmp_path_factory.mktemp(f"case-{identity}", numbered=False)
    owned_identity = _identity(owned.stat(follow_symlinks=False))
    yield owned
    _remove_owned_directory(owned, owned_identity)


APPROVAL_DECISION = "decision:ADR-0001"
APPROVAL_EFFECTIVE = "effective:2026-08-29"
APPROVAL_TAGS: tuple[str, ...] = (APPROVAL_DECISION, APPROVAL_EFFECTIVE)


def seed_approval_docs(root: Path) -> None:
    """Publish the physical docs/ approvals every canonical tag resolves to."""

    adr = root / "docs" / "adr"
    adr.mkdir(parents=True, exist_ok=True)
    (adr / "ADR-0001-fixture.md").write_text("# ADR-0001\n", encoding="utf-8")
    plans = root / "docs" / "execution" / "master-v7"
    plans.mkdir(parents=True, exist_ok=True)
    (plans / "11-fixture.md").write_text("# plan-11\n", encoding="utf-8")


def approved(tags: tuple[str, ...]) -> tuple[str, ...]:
    """Return tags carrying exactly one decision and one effective approval."""

    kept = tuple(tag for tag in tags if not tag.startswith(("decision:", "effective:")))
    merged = APPROVAL_TAGS + kept
    if list(kept) != sorted(kept):
        return merged
    return tuple(sorted(merged))
