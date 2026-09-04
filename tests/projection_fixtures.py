"""Shared projection test types and fixtures.

`test_projection.py` and `test_projection_config.py` both describe projection
documents, so the JSON type aliases and the canonical detection-rule fixture
have one owner here rather than a copy in each module.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

# Why: Sequence/Mapping recursion keeps nested JSON documents assignable under
# invariance (ag-2wq detection-rule fixtures).
type JsonValue = (
    None | bool | int | float | str | Sequence["JsonValue"] | Mapping[str, "JsonValue"]
)
type JsonDocument = dict[str, JsonValue]


def flext_detection_rule() -> JsonDocument:
    """Return the canonical FLEXT project-detection rule used across projection tests.

    Returns:
        The detection rule that activates the ``flext`` tag on a project whose
        ``pyproject.toml`` carries the ``@flext-managed`` marker.

    """
    return {
        "activate_tags": ["flext"],
        "id": "flext-managed",
        "when": {
            "any": [
                {
                    "paths": ["pyproject.toml"],
                    "pattern": "@flext-managed",
                    "type": "file_contains",
                }
            ]
        },
    }
