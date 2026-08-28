from __future__ import annotations

from pathlib import Path

import conftest
import pytest
from conftest import _remove_owned_directory


def _identity(path: Path) -> tuple[int, int]:
    metadata = path.stat(follow_symlinks=False)
    return metadata.st_dev, metadata.st_ino


def test_owned_test_directory_cleanup_removes_the_original_directory(
    tmp_path: Path,
) -> None:
    owned = tmp_path / "owned"
    owned.mkdir()
    (owned / "artifact").write_text("owned\n", encoding="utf-8")

    _remove_owned_directory(owned, _identity(owned))

    assert not owned.exists()


def test_owned_test_directory_cleanup_accepts_an_already_removed_path(
    tmp_path: Path,
) -> None:
    owned = tmp_path / "owned"
    owned.mkdir()
    identity = _identity(owned)
    owned.rmdir()

    _remove_owned_directory(owned, identity)

    assert not owned.exists()


def test_owned_test_directory_cleanup_preserves_a_replacement_directory(
    tmp_path: Path,
) -> None:
    owned = tmp_path / "owned"
    original = tmp_path / "original"
    owned.mkdir()
    identity = _identity(owned)
    owned.rename(original)
    owned.mkdir()
    sentinel = owned / "foreign"
    sentinel.write_text("preserve\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="identity changed"):
        _remove_owned_directory(owned, identity)

    assert sentinel.read_text(encoding="utf-8") == "preserve\n"
    assert original.is_dir()


def test_owned_test_directory_cleanup_preserves_a_replacement_symlink(
    tmp_path: Path,
) -> None:
    owned = tmp_path / "owned"
    outside = tmp_path / "outside"
    owned.mkdir()
    outside.mkdir()
    identity = _identity(owned)
    owned.rmdir()
    owned.symlink_to(outside, target_is_directory=True)

    with pytest.raises(RuntimeError, match="must remain the original directory"):
        _remove_owned_directory(owned, identity)

    assert owned.is_symlink()
    assert outside.is_dir()


def test_owned_cleanup_detects_concurrent_top_level_substitution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owned = tmp_path / "owned"
    moved_original = tmp_path / "moved-original"
    owned.mkdir()
    (owned / "original").write_text("owned\n", encoding="utf-8")
    identity = _identity(owned)
    original_empty = conftest._empty_owned_directory

    def substitute_after_pin(directory_fd: int) -> None:
        owned.rename(moved_original)
        owned.mkdir()
        (owned / "foreign").write_text("preserve\n", encoding="utf-8")
        original_empty(directory_fd)

    monkeypatch.setattr(conftest, "_empty_owned_directory", substitute_after_pin)

    with pytest.raises(RuntimeError, match="identity changed"):
        _remove_owned_directory(owned, identity)

    assert (owned / "foreign").read_text(encoding="utf-8") == "preserve\n"
    assert list(moved_original.iterdir()) == []


def test_owned_cleanup_reports_concurrent_top_level_removal(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owned = tmp_path / "owned"
    moved_original = tmp_path / "moved-original"
    owned.mkdir()
    identity = _identity(owned)
    original_empty = conftest._empty_owned_directory

    def remove_name_after_pin(directory_fd: int) -> None:
        owned.rename(moved_original)
        original_empty(directory_fd)

    monkeypatch.setattr(conftest, "_empty_owned_directory", remove_name_after_pin)

    with pytest.raises(RuntimeError, match="identity changed"):
        _remove_owned_directory(owned, identity)

    assert moved_original.is_dir()
