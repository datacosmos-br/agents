from pathlib import Path

import pytest

from agents_governance.cleanup import clean_generated


def test_clean_generated_removes_only_declared_artifacts(tmp_path: Path) -> None:
    cache = tmp_path / ".waza-cache"
    latest = tmp_path / "results" / "latest"
    pycache = tmp_path / "skills" / "review" / "__pycache__"
    preserved = tmp_path / "results" / "baseline" / "results.json"
    for directory in (cache, latest, pycache, preserved.parent):
        directory.mkdir(parents=True, exist_ok=True)
    (cache / "cache.bin").write_bytes(b"cache")
    (latest / "results.json").write_text("{}", encoding="utf-8")
    (pycache / "module.pyc").write_bytes(b"pyc")
    preserved.write_text("{}", encoding="utf-8")

    removed = clean_generated(tmp_path)

    assert set(removed) == {cache, latest, pycache}
    assert preserved.is_file()


def test_clean_generated_refuses_symlink(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "keep"
    marker.write_text("keep", encoding="utf-8")
    (tmp_path / ".waza-cache").symlink_to(outside, target_is_directory=True)

    with pytest.raises(RuntimeError, match="symlink"):
        clean_generated(tmp_path)

    assert marker.read_text(encoding="utf-8") == "keep"
    (tmp_path / ".waza-cache").unlink()


def test_clean_generated_preflights_every_candidate_before_deleting_anything(
    tmp_path: Path,
) -> None:
    cache = tmp_path / ".waza-cache"
    cache.mkdir()
    cache_marker = cache / "preserve-on-failure"
    cache_marker.write_text("keep", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    latest = tmp_path / "results" / "latest"
    latest.mkdir(parents=True)
    (latest / "foreign").symlink_to(outside, target_is_directory=True)

    with pytest.raises(RuntimeError, match="symlink"):
        clean_generated(tmp_path)

    assert cache_marker.read_text(encoding="utf-8") == "keep"
