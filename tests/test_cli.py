import json
from pathlib import Path

from agents_governance.cli import main


def test_waza_artifact_fails_closed_for_empty_or_invalid_output(tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    empty.touch()
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{}\n", encoding="utf-8")

    assert main(["waza-artifact", str(empty)]) == 1
    assert main(["waza-artifact", str(invalid)]) == 1


def test_waza_artifact_accepts_scored_dimensions(tmp_path: Path) -> None:
    artifact = tmp_path / "quality.json"
    artifact.write_text(json.dumps({"dimensions": [{"name": "clarity", "score": 4}]}), encoding="utf-8")

    assert main(["waza-artifact", str(artifact)]) == 0
