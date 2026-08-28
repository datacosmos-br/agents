from __future__ import annotations

from pathlib import Path

import pytest

from agents_governance.catalog import Catalog
from agents_governance.validation import require_description, validate


@pytest.mark.parametrize(
    "description",
    [
        "c++, cmake, service development",
        "agent behavior, session recovery, tool debugging",
        "rest api, resource naming, error semantics",
    ],
)
def test_description_contract_accepts_nominal_discovery_terms(
    description: str,
) -> None:
    assert require_description(description) == description


@pytest.mark.parametrize(
    ("description", "message"),
    [
        (None, "missing description"),
        (" review, security, validation", "trimmed line"),
        ("review, code", "3-10"),
        ("Code review, security, validation", "lowercase"),
        ("code review when deployed, security, validation", "nominal phrases"),
        ("code@review, security, validation", "technical identifiers"),
        ("review,security, validation", "separated"),
        ("code review, code review, validation", "unique"),
    ],
)
def test_description_contract_raises_first_defect(
    description: object, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        require_description(description)


def test_canonical_validation_executes_complete_offline_authority() -> None:
    root = Path(__file__).resolve().parents[1]

    validate(Catalog(root))
