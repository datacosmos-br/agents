from pathlib import Path

import pytest

from agents_governance.atomic_io import atomic_write_text


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
