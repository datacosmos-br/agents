"""Typed approval-authority tags: effective dates and dated docs/ references.

``docs/`` is the only approval authority. One reference grammar serves both
``decision:`` and ``supersedes:`` tags. ADR and plan documents are discovered
physically at validation time; nothing hand-maintained enumerates approvals.
A malformed, impossible, future-dated, or unresolvable reference fails loud.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from pathlib import Path

_EFFECTIVE_TAG = re.compile(r"effective:(\d{4})-(\d{2})-(\d{2})\Z")
_DECISION_TAG = re.compile(r"decision:(.+)\Z")
_SUPERSEDES_TAG = re.compile(r"supersedes:(.+)\Z")
_APPROVAL_REFERENCE = re.compile(r"(?:ADR-\d{4}|plan-\d{2}(?:-inc\d+)?)\Z")

_ADR_DIRECTORY = Path("docs") / "adr"
_PLAN_DIRECTORY = Path("docs") / "execution" / "master-v7"

APPROVAL_NAMESPACES = frozenset({"decision", "effective", "supersedes"})
_APPROVAL_PREFIXES = tuple(f"{namespace}:" for namespace in sorted(APPROVAL_NAMESPACES))


def _reference(tag: str, kind: str, pattern: re.Pattern[str]) -> str:
    match = pattern.fullmatch(tag)
    if match is None:
        raise ValueError(f"malformed {kind} tag: {tag!r}")
    reference = match.group(1)
    if _APPROVAL_REFERENCE.fullmatch(reference) is None:
        raise ValueError(f"unsupported approval reference in {kind} tag: {tag!r}")
    return reference


def validate_effective_tag(tag: str) -> None:
    match = _EFFECTIVE_TAG.fullmatch(tag)
    if match is None:
        raise ValueError(f"malformed effective tag: {tag!r}")
    year, month, day = (int(part) for part in match.groups())
    effective = date(year, month, day)
    if effective > datetime.now(tz=UTC).date():
        raise ValueError(f"effective date is in the future: {tag!r}")


def validate_decision_tag(tag: str) -> str:
    return _reference(tag, "decision", _DECISION_TAG)


def validate_supersedes_tag(tag: str) -> str:
    return _reference(tag, "supersedes", _SUPERSEDES_TAG)


def resolve_reference(root: Path, reference: str) -> Path:
    """Resolve one approval reference to exactly one physical docs/ document."""

    if reference.startswith("ADR-"):
        directory = _ADR_DIRECTORY
        pattern = f"{reference}-*.md"
    else:
        plan = reference.split("-inc", 1)[0].removeprefix("plan-")
        directory = _PLAN_DIRECTORY
        pattern = f"{plan}-*.md"
    matches = tuple(sorted((root / directory).glob(pattern)))
    if len(matches) != 1:
        raise ValueError(
            "approval reference does not resolve to exactly one document: "
            f"{reference!r} -> {directory / pattern}"
        )
    return matches[0]


def resolve_approval_tags(root: Path, tags: tuple[str, ...], source: Path) -> None:
    """Validate format and resolution of every approval tag or raise loud."""

    for tag in tags:
        if tag.startswith("effective:"):
            validate_effective_tag(tag)
        elif tag.startswith("decision:"):
            resolve_reference(root, validate_decision_tag(tag))
        elif tag.startswith("supersedes:"):
            resolve_reference(root, validate_supersedes_tag(tag))


def core_tags(tags: tuple[str, ...]) -> tuple[str, ...]:
    """Return the tags outside the approval namespaces, order preserved."""

    return tuple(tag for tag in tags if not tag.startswith(_APPROVAL_PREFIXES))


__all__ = (
    "APPROVAL_NAMESPACES",
    "core_tags",
    "resolve_approval_tags",
    "resolve_reference",
    "validate_decision_tag",
    "validate_effective_tag",
    "validate_supersedes_tag",
)
