from pathlib import Path

import pytest

from agents_governance.atomic_io import atomic_write_text, text_publication
from agents_governance.cleanup import (
    PreparedPublication,
    Publication,
    run_atomic_publications,
)


def test_atomic_write_preserves_existing_file_when_promotion_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    destination = tmp_path / "owner.json"
    destination.write_text("old\n", encoding="utf-8")
    original_replace = Path.replace

    def fail_promotion(source: Path, target: Path) -> Path:
        if target == destination:
            raise OSError("injected promotion failure")
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", fail_promotion)

    with pytest.raises(OSError, match="injected promotion failure"):
        atomic_write_text(destination, "new\n")

    assert destination.read_text(encoding="utf-8") == "old\n"
    assert list(tmp_path.glob("*.candidate")) == []


def test_unchanged_text_has_no_publication(tmp_path: Path) -> None:
    destination = tmp_path / "owner.json"
    destination.write_text("current\n", encoding="utf-8")

    assert text_publication(destination, "current\n") is None
    assert list(tmp_path.glob("*.candidate")) == []


def test_text_publication_rolls_back_when_later_publication_fails(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "owner.json"
    destination.write_text("old\n", encoding="utf-8")
    publication = text_publication(destination, "new\n")
    assert publication is not None

    def fail() -> None:
        raise OSError("injected later publication failure")

    failing = Publication(lambda: PreparedPublication(fail, lambda: None, lambda: None))

    with pytest.raises(OSError, match="injected later publication failure"):
        run_atomic_publications((publication, failing))

    assert destination.read_text(encoding="utf-8") == "old\n"
    assert list(tmp_path.glob("*.candidate")) == []
