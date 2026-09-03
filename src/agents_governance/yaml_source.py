"""Canonical fail-loud YAML and frontmatter source parsing."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, cast, overload

import yaml
from yaml.nodes import MappingNode, Node, SequenceNode

__all__ = ("detect_duplicate_key", "parse_frontmatter")


def detect_duplicate_key(node: Node) -> str | None:
    """Return the first duplicate mapping key in a YAML node tree."""

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
    """Parse fail-loud YAML frontmatter and return it with the body."""

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
