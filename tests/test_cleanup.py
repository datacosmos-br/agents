from pathlib import Path

import pytest

from agents_governance.cleanup import (
    PreparedPublication,
    Publication,
    clean_generated,
    remove_physical,
    run_atomic_publications,
    run_atomic_sequence,
    run_cleanup,
)


def test_clean_generated_removes_only_declared_artifacts(tmp_path: Path) -> None:
    cache = tmp_path / ".waza-cache"
    latest = tmp_path / "results" / "latest"
    skill_pycache = tmp_path / "skills" / "review" / "__pycache__"
    runtime_pycache = tmp_path / "src" / "governance" / "__pycache__"
    scratch = tmp_path / ".test-tmp"
    distribution = tmp_path / "dist"
    preserved = tmp_path / "results" / "baseline" / "results.json"
    for directory in (
        cache,
        latest,
        skill_pycache,
        runtime_pycache,
        scratch,
        distribution,
        preserved.parent,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    (cache / "cache.bin").write_bytes(b"cache")
    (latest / "results.json").write_text("{}", encoding="utf-8")
    (skill_pycache / "skill.pyc").write_bytes(b"pyc")
    (runtime_pycache / "runtime.pyc").write_bytes(b"pyc")
    (distribution / ".gitignore").write_text("*\n", encoding="utf-8")
    wheel = distribution / "package.whl"
    wheel.write_bytes(b"wheel")
    preserved.write_text("{}", encoding="utf-8")

    removed = clean_generated(tmp_path)

    assert set(removed) == {
        cache,
        latest,
        skill_pycache,
        runtime_pycache,
        scratch,
        wheel,
    }
    assert preserved.is_file()
    assert (distribution / ".gitignore").read_text(encoding="utf-8") == "*\n"


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


def test_remove_physical_owns_file_and_tree_removal(tmp_path: Path) -> None:
    file = tmp_path / "file"
    tree = tmp_path / "tree"
    file.write_text("file", encoding="utf-8")
    tree.mkdir()
    (tree / "nested").write_text("nested", encoding="utf-8")

    remove_physical(file)
    remove_physical(tree)

    assert not file.exists()
    assert not tree.exists()


def test_atomic_sequence_rolls_back_published_and_failing_items() -> None:
    published: list[int] = []
    rolled_back: list[int] = []
    cleaned: list[int] = []

    def publish(item: int) -> None:
        published.append(item)
        if item == 2:
            raise RuntimeError("publication failed")

    with pytest.raises(RuntimeError, match="publication failed"):
        run_atomic_sequence(
            (1, 2, 3),
            lambda item: item,
            publish,
            rolled_back.append,
            cleaned.append,
        )

    assert published == [1, 2]
    assert rolled_back == [2, 1]
    assert cleaned == [3, 2, 1]


def test_atomic_sequence_preserves_primary_when_rollback_fails() -> None:
    def publish(_item: int) -> None:
        raise RuntimeError("primary publication failure")

    def rollback(_item: int) -> None:
        raise OSError("secondary rollback failure")

    with pytest.raises(RuntimeError, match="primary publication failure") as captured:
        run_atomic_sequence(
            (1,), lambda item: item, publish, rollback, lambda _item: None
        )

    assert isinstance(captured.value.__cause__, OSError)
    assert captured.value.__notes__ == [
        "rollback or cleanup failed: secondary rollback failure"
    ]


def test_heterogeneous_publications_roll_back_as_one_transaction() -> None:
    events: list[str] = []

    def prepared(name: str, *, fail: bool = False) -> PreparedPublication:
        def publish() -> None:
            events.append(f"publish:{name}")
            if fail:
                raise RuntimeError("publication failed")

        return PreparedPublication(
            publish,
            lambda: events.append(f"rollback:{name}"),
            lambda: events.append(f"cleanup:{name}"),
        )

    with pytest.raises(RuntimeError, match="publication failed"):
        run_atomic_publications(
            (
                Publication(lambda: prepared("directory")),
                Publication(lambda: prepared("hook", fail=True)),
            )
        )

    assert events == [
        "publish:directory",
        "publish:hook",
        "rollback:hook",
        "rollback:directory",
        "cleanup:hook",
        "cleanup:directory",
    ]


def test_cleanup_runs_every_action_and_preserves_secondary_failures() -> None:
    calls: list[str] = []

    def fail(name: str) -> None:
        calls.append(name)
        raise RuntimeError(name)

    with pytest.raises(RuntimeError, match="first") as captured:
        run_cleanup((lambda: fail("first"), lambda: fail("second")))

    assert calls == ["first", "second"]
    assert str(captured.value.__cause__) == "second"
    assert captured.value.__notes__ == ["additional cleanup failed: second"]
