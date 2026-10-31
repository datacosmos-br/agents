"""Exercise evaluation metric validation through the public bundle loader."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml

from agents_governance import GovernanceBundle


@pytest.mark.parametrize("field", ("weight", "threshold"))
@pytest.mark.parametrize(
    ("value", "error", "message"),
    (
        (True, TypeError, "must be numeric"),
        ("1.0", TypeError, "must be numeric"),
        (None, TypeError, "must be numeric"),
        (0.0, ValueError, "must equal 1.0"),
        (0.9999999999, ValueError, "must equal 1.0"),
        (1.0000000001, ValueError, "must equal 1.0"),
    ),
)
def test_metric_rejects_values_outside_exact_numeric_contract(
    governance_source_fixture: Path,
    field: str,
    value: bool | str | float | None,
    error: type[Exception],
    message: str,
) -> None:
    path = governance_source_fixture / "config" / "evals.json"
    document = json.loads(path.read_text())
    document["metric"][field] = value
    path.write_text(json.dumps(document))
    with pytest.raises(error, match=message):
        GovernanceBundle.load(governance_source_fixture)


def test_happy_path_task_requires_scenario_fixture(
    governance_source_fixture: Path,
) -> None:
    suite = min((governance_source_fixture / "evals").iterdir())
    path = suite / "tasks" / "basic-usage.yaml"
    task = yaml.safe_load(path.read_text())
    del task["inputs"]["files"]
    path.write_text(yaml.safe_dump(task))
    with pytest.raises(
        ValueError,
        match=f"{re.escape(str(path.resolve()))}: happy_path requires inputs.files",
    ):
        GovernanceBundle.load(governance_source_fixture)
