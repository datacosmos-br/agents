"""Canonical YAML frontmatter parsing and metadata validation.

Single source of truth for frontmatter-bearing Markdown parsing across
all agents_governance modules. Every module that reads YAML frontmatter
or validates parsed mapping nodes delegates here: no local copy or variant
is permitted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, cast, overload

import yaml
from yaml.nodes import MappingNode, Node, SequenceNode

__all__ = (
    "cast_mapping",
    "detect_duplicate_key",
    "parse_frontmatter",
    "require_exact_fields",
    "string_array",
)


def detect_duplicate_key(node: Node) -> str | None:
    """Return the first duplicate mapping key in a YAML node tree, else None."""

    if isinstance(node, MappingNode):
        seen: set[str] = set()
        for key_node, value_node in node.value:
            key = str(getattr(key_node, "value", "<non-scalar>"))
            if key in seen:
                return key
            seen.add(key)
            duplicate = detect_duplicate_key(value_node)
            if duplicate is not None:
                return duplicate
    elif isinstance(node, SequenceNode):
        for child in node.value:
            duplicate = detect_duplicate_key(child)
            if duplicate is not None:
                return duplicate
    return None


@overload
def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]: ...


@overload
def parse_frontmatter(
    path: Path, *, required: Literal[False]
) -> tuple[dict[str, object] | None, str]: ...


@overload
def parse_frontmatter(
    path: Path, *, required: bool
) -> tuple[dict[str, object] | None, str]: ...


def parse_frontmatter(
    path: Path, *, required: bool = True
) -> tuple[dict[str, object] | None, str]:
    """Parse YAML frontmatter from a Markdown file.

    When *required* is True (the default), raise ``ValueError`` if the file
    lacks a frontmatter block.  When False, return ``(None, full_text)``.
    Duplicate keys, non-string keys, and non-mapping frontmatter all raise
    loudly.
    """

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        if not required:
            return None, text
        raise ValueError(f"{path}: missing YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
    source = text[4:marker]
    node = yaml.compose(source, Loader=yaml.SafeLoader)
    loaded = yaml.safe_load(source)
    if not isinstance(node, MappingNode) or not isinstance(loaded, dict):
        raise TypeError(f"{path}: frontmatter must be a mapping")
    duplicate = detect_duplicate_key(node)
    if duplicate is not None:
        raise ValueError(f"{path}: frontmatter key is duplicated: {duplicate}")
    raw = cast(dict[object, object], loaded)
    if not all(isinstance(key, str) for key in raw):
        raise TypeError(f"{path}: frontmatter keys must be strings")
    return cast(dict[str, object], raw), text[marker + 5 :].removeprefix("\n")


def cast_mapping(value: object, context: str) -> dict[str, object]:
    """Validate that *value* is a dict with string keys, returning it typed."""

    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{context} must be an object with string keys")
    return cast(dict[str, object], value)


def string_array(
    value: object,
    context: str,
    *,
    require_unique: bool = True,
    require_sorted: bool = False,
) -> tuple[str, ...]:
    """Return one non-empty array of trimmed strings under explicit invariants."""

    if (
        not isinstance(value, list)
        or not value
        or not all(
            isinstance(item, str) and item and item == item.strip() for item in value
        )
    ):
        raise TypeError(f"{context} must be a non-empty array of trimmed strings")
    strings = tuple(cast(list[str], value))
    if require_unique and len(strings) != len(set(strings)):
        raise ValueError(f"{context} values must be unique")
    if require_sorted and strings != tuple(sorted(strings)):
        raise ValueError(f"{context} values must be sorted")
    return strings


def require_exact_fields(
    value: dict[str, object], fields: frozenset[str], context: str
) -> None:
    """Raise if *value* does not contain exactly the set *fields*."""

    if frozenset(value) != fields:
        raise ValueError(
            f"{context} fields must equal {', '.join(sorted(fields))}; "
            f"got {', '.join(sorted(value)) or 'none'}"
        )
