"""Stdlib-dataclass project with no Pydantic dependency anywhere."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParseResult:
    """One parsed row with its source offset."""

    offset: int
    value: str
