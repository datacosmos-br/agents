"""Regression coverage for the canonical YAML source owner."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from agents_governance.frontmatter import (
    detect_duplicate_key,
    parse_frontmatter,
)


def test_parse_frontmatter_returns_typed_metadata_and_trimmed_body(
    tmp_path: Path,
) -> None:
    path = tmp_path / "source.md"
    path.write_text(
        "---\nname: example\nmetadata:\n  aihub.tags: '[\"activation:always\"]'\n"
        "---\nbody\n",
        encoding="utf-8",
    )

    metadata, body = parse_frontmatter(path)

    assert metadata == {
        "name": "example",
        "metadata": {"aihub.tags": '["activation:always"]'},
    }
    assert body == "body\n"


def test_parse_frontmatter_honors_optional_missing_source(tmp_path: Path) -> None:
    path = tmp_path / "source.md"
    path.write_text("body only\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing YAML frontmatter"):
        parse_frontmatter(path)
    assert parse_frontmatter(path, required=False) == (None, "body only\n")


def test_parse_frontmatter_rejects_duplicate_and_non_string_keys(
    tmp_path: Path,
) -> None:
    duplicate = tmp_path / "duplicate.md"
    duplicate.write_text("---\nname: first\nname: second\n---\n", encoding="utf-8")
    non_string = tmp_path / "non-string.md"
    non_string.write_text("---\ntrue: value\n---\n", encoding="utf-8")

    with pytest.raises(ValueError, match="frontmatter key is duplicated: name"):
        parse_frontmatter(duplicate)
    with pytest.raises(TypeError, match="frontmatter keys must be strings"):
        parse_frontmatter(non_string)


def test_detect_duplicate_key_finds_first_nested_duplicate() -> None:
    document = """
    outer:
      first: 1
      first: 2
    """
    node = yaml.compose(document, Loader=yaml.SafeLoader)

    assert detect_duplicate_key(node) == "first"
