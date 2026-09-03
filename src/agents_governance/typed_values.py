"""Canonical typed validation for string-keyed mappings and exact fields."""

from __future__ import annotations

from typing import cast

__all__ = ("cast_mapping", "require_exact_fields")


def cast_mapping(value: object, context: str) -> dict[str, object]:
    """Return a string-keyed mapping or raise on its first contract defect."""

    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{context} must be an object with string keys")
    return cast(dict[str, object], value)


def require_exact_fields(
    value: dict[str, object], fields: frozenset[str], context: str
) -> None:
    """Reject a mapping whose key set differs from the exact owner schema."""

    if frozenset(value) != fields:
        raise ValueError(
            f"{context} fields must equal {', '.join(sorted(fields))}; "
            f"got {', '.join(sorted(value)) or 'none'}"
        )
