"""Fail-closed cleanup for repository-owned generated artifacts."""

from __future__ import annotations

import os
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Never


@dataclass(frozen=True)
class PreparedPublication:
    """One staged publication with its compensating operations."""

    publish: Callable[[], None]
    rollback: Callable[[], None]
    cleanup: Callable[[], None]


@dataclass(frozen=True)
class Publication:
    """Deferred preparation for one publication target."""

    prepare: Callable[[], PreparedPublication]


def run_with_cleanup[Result](
    operation: Callable[[], Result], cleanup: Callable[[], None]
) -> Result:
    """Run one operation and preserve its exception if cleanup also fails."""

    try:
        return operation()
    except BaseException as error:
        try:
            cleanup()
        except BaseException as cleanup_error:
            error.add_note(f"cleanup failed: {cleanup_error}")
            raise error from cleanup_error
        raise


def _cleanup_all[Item](
    items: Sequence[Item], cleanup: Callable[[Item], None]
) -> list[BaseException]:
    failures: list[BaseException] = []
    for item in reversed(items):
        try:
            cleanup(item)
        except BaseException as caught_failure:  # noqa: BLE001 - cleanup owner
            failures.append(caught_failure)
    return failures


def _raise_with_secondary(
    primary: BaseException, secondary: list[BaseException]
) -> Never:
    for error in secondary:
        primary.add_note(f"rollback or cleanup failed: {error}")
    if secondary:
        raise primary from secondary[0]
    raise primary


def run_cleanup(actions: Sequence[Callable[[], None]]) -> None:
    """Run every cleanup action and preserve all secondary failures."""

    failures = _cleanup_all(tuple(reversed(actions)), lambda action: action())
    if failures:
        primary = failures[0]
        for secondary in failures[1:]:
            primary.add_note(f"additional cleanup failed: {secondary}")
        if len(failures) > 1:
            raise primary from failures[1]
        raise primary


def run_atomic_sequence[Input, Prepared](
    inputs: Sequence[Input],
    prepare: Callable[[Input], Prepared],
    publish: Callable[[Prepared], None],
    rollback: Callable[[Prepared], None],
    cleanup: Callable[[Prepared], None],
) -> None:
    """Prepare all items, publish in order, and centrally own rollback catches."""

    prepared: list[Prepared] = []
    try:
        for input_item in inputs:
            prepared.append(prepare(input_item))
    except BaseException as primary_failure:  # noqa: BLE001 - rollback owner
        _raise_with_secondary(primary_failure, _cleanup_all(prepared, cleanup))

    published: list[Prepared] = []
    try:
        for prepared_item in prepared:
            published.append(prepared_item)
            publish(prepared_item)
    except BaseException as primary_failure:  # noqa: BLE001 - rollback owner
        rollback_failures = _cleanup_all(published, rollback)
        if rollback_failures:
            _raise_with_secondary(primary_failure, rollback_failures)
        _raise_with_secondary(primary_failure, _cleanup_all(prepared, cleanup))

    cleanup_failures = _cleanup_all(prepared, cleanup)
    if cleanup_failures:
        primary = cleanup_failures[0]
        for secondary_failure in cleanup_failures[1:]:
            primary.add_note(f"additional cleanup failed: {secondary_failure}")
        raise primary


def run_atomic_publications(publications: Sequence[Publication]) -> None:
    """Prepare heterogeneous targets, then publish them as one transaction."""

    prepared: list[PreparedPublication] = []
    try:
        for publication in publications:
            prepared.append(publication.prepare())
    except BaseException as primary_failure:  # noqa: BLE001 - rollback owner
        _raise_with_secondary(
            primary_failure,
            _cleanup_all(prepared, lambda item: item.cleanup()),
        )

    published: list[PreparedPublication] = []
    try:
        for prepared_item in prepared:
            published.append(prepared_item)
            prepared_item.publish()
    except BaseException as primary_failure:  # noqa: BLE001 - rollback owner
        rollback_failures = _cleanup_all(published, lambda item: item.rollback())
        cleanup_failures = _cleanup_all(prepared, lambda item: item.cleanup())
        _raise_with_secondary(primary_failure, [*rollback_failures, *cleanup_failures])

    cleanup_failures = _cleanup_all(prepared, lambda item: item.cleanup())
    if cleanup_failures:
        primary = cleanup_failures[0]
        for secondary_failure in cleanup_failures[1:]:
            primary.add_note(f"additional cleanup failed: {secondary_failure}")
        raise primary


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
        elif entry.is_file(follow_symlinks=False):
            child.unlink()
        else:
            raise RuntimeError(f"refusing to clean special file: {child}")
    path.rmdir()


def _validate_tree(path: Path) -> None:
    """Prove an entire generated tree is physical before any deletion starts."""

    if path.is_symlink():
        raise RuntimeError(f"refusing to clean symlink: {path}")
    if not path.is_dir():
        raise RuntimeError(f"generated cleanup target is not a directory: {path}")
    with os.scandir(path) as entries:
        children = list(entries)
    for entry in children:
        child = Path(entry.path)
        if entry.is_symlink():
            raise RuntimeError(f"refusing to clean symlink: {child}")
        if entry.is_dir(follow_symlinks=False):
            _validate_tree(child)
        elif not entry.is_file(follow_symlinks=False):
            raise RuntimeError(f"refusing to clean special file: {child}")


def validate_physical(path: Path) -> None:
    """Require one existing path and its descendants to be physical."""

    if path.is_symlink():
        raise RuntimeError(f"refusing physical operation on symlink: {path}")
    if path.is_dir():
        _validate_tree(path)
    elif not path.is_file():
        raise RuntimeError(f"physical path is neither file nor directory: {path}")


def remove_physical(path: Path) -> None:
    """Remove one validated physical file or directory without following links."""

    validate_physical(path)
    if path.is_dir():
        _remove_tree(path)
    else:
        path.unlink()


def clean_generated(root: Path) -> tuple[Path, ...]:
    """Remove only the repository's declared, ignored generated surfaces."""

    root = root.resolve()
    candidates = [path for path in root.rglob("__pycache__") if path.is_dir()]
    distribution = root / "dist"
    if distribution.is_dir() and not distribution.is_symlink():
        candidates.extend(
            path for path in sorted(distribution.iterdir()) if path.name != ".gitignore"
        )
    candidates.extend(
        (
            root / ".pytest_cache",
            root / ".test-tmp",
            root / ".waza-cache",
            root / "results" / "latest",
        )
    )
    present: list[Path] = []
    for path in candidates:
        if not path.exists() and not path.is_symlink():
            continue
        resolved_parent = path.parent.resolve()
        if root != resolved_parent and root not in resolved_parent.parents:
            raise RuntimeError(f"refusing to clean outside repository: {path}")
        validate_physical(path)
        present.append(path)
    removed: list[Path] = []
    for path in present:
        remove_physical(path)
        removed.append(path)
    return tuple(removed)


__all__ = (
    "PreparedPublication",
    "Publication",
    "clean_generated",
    "remove_physical",
    "run_atomic_publications",
    "run_atomic_sequence",
    "run_cleanup",
    "run_with_cleanup",
    "validate_physical",
)
