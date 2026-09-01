"""Typed approval-authority tags: effective dates and dated docs/ references.

``docs/`` is the only approval authority for ``decision:`` lineage. ADR and
plan documents are discovered physically at validation time; nothing
hand-maintained enumerates approvals.

``supersedes:`` carries two forms. A document reference records approval
lineage and resolves into ``docs/``. An artifact identity — the same
``kind:path`` grammar ``config/governance.json`` already uses — records that
this artifact replaced another one, and :func:`audit_precedence` requires the
named artifact to be absent from the active inventory. Old and new coexisting
is the residue defect the recency law exists to forbid.

``effective:`` is a UTC calendar date. It is rendered into every projection so
the surface that consumes composed governance can order two artifacts by
recency at the point of use.

A malformed, impossible, future-dated, or unresolvable reference fails loud.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

_EFFECTIVE_TAG = re.compile(r"effective:(\d{4})-(\d{2})-(\d{2})\Z")
_DECISION_TAG = re.compile(r"decision:(.+)\Z")
_SUPERSEDES_TAG = re.compile(r"supersedes:(.+)\Z")
_APPROVAL_REFERENCE = re.compile(r"(?:ADR-\d{4}|plan-\d{2})\Z")
_ARTIFACT_IDENTITY = re.compile(r"(?:rule|skill|command):[A-Za-z0-9][A-Za-z0-9._/-]*\Z")

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
    """Validate one effective tag as a non-future UTC calendar date."""

    match = _EFFECTIVE_TAG.fullmatch(tag)
    if match is None:
        raise ValueError(f"malformed effective tag: {tag!r}")
    year, month, day = (int(part) for part in match.groups())
    effective = date(year, month, day)
    if effective > datetime.now(tz=UTC).date():
        raise ValueError(f"effective date is in the future: {tag!r}")


def validate_decision_tag(tag: str) -> str:
    return _reference(tag, "decision", _DECISION_TAG)


def supersedes_identity(tag: str) -> str | None:
    """Return the artifact identity a supersedes tag names, or None for lineage."""

    match = _SUPERSEDES_TAG.fullmatch(tag)
    if match is None:
        raise ValueError(f"malformed supersedes tag: {tag!r}")
    reference = match.group(1)
    if _ARTIFACT_IDENTITY.fullmatch(reference) is None:
        return None
    return reference


def validate_supersedes_tag(tag: str) -> str:
    """Validate a supersedes tag in either the identity or the lineage form."""

    identity = supersedes_identity(tag)
    if identity is not None:
        return identity
    return _reference(tag, "supersedes", _SUPERSEDES_TAG)


def resolve_reference(root: Path, reference: str) -> Path:
    """Resolve one approval reference to exactly one physical docs/ document."""

    if reference.startswith("ADR-"):
        directory = _ADR_DIRECTORY
        pattern = f"{reference}-*.md"
    else:
        plan = reference.removeprefix("plan-")
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

    for kind in ("decision", "effective"):
        matching = tuple(tag for tag in tags if tag.startswith(f"{kind}:"))
        if len(matching) != 1:
            raise ValueError(
                f"{source}: requires exactly one {kind}: tag; got {len(matching)}"
            )
    for tag in tags:
        if tag.startswith("effective:"):
            validate_effective_tag(tag)
        elif tag.startswith("decision:"):
            resolve_reference(root, validate_decision_tag(tag))
        elif tag.startswith("supersedes:"):
            reference = validate_supersedes_tag(tag)
            if supersedes_identity(tag) is None:
                resolve_reference(root, reference)


def approval_note(tags: tuple[str, ...]) -> str:
    """Render the dated approval provenance as one provider-neutral comment.

    Every projected surface appends the same marker, so a consumer reading
    composed governance can order two artifacts by their ``effective:`` date
    at the point of use.
    """

    approval = approval_tags(tags)
    if not approval:
        return ""
    return "\n\n<!-- aihub.approval: " + "; ".join(approval) + " -->"


@dataclass(frozen=True)
class ApprovedArtifact:
    """One active artifact carrying approval tags, addressed by its identity."""

    identity: str
    tags: tuple[str, ...]
    source: Path


def _history_pathspec(identity: str) -> str:
    kind, name = identity.split(":", 1)
    if kind == "rule":
        return f"rules/{name}.md"
    if kind == "skill":
        return f":(glob)skills/**/{name}/SKILL.md"
    if kind == "command":
        return f":(glob)commands/**/{name}.md"
    raise ValueError(f"unsupported artifact identity: {identity!r}")


def _require_historical_identity(root: Path, identity: str, source: Path) -> None:
    result = subprocess.run(
        (
            "git",
            "-C",
            str(root),
            "log",
            "--all",
            "--format=%H",
            "-n",
            "1",
            "--",
            _history_pathspec(identity),
        ),
        check=True,
        capture_output=True,
        text=True,
    )
    if not result.stdout.strip():
        raise ValueError(
            f"{source}: supersedes {identity!r}, which does not resolve through "
            "Git history"
        )


def audit_precedence(root: Path, artifacts: tuple[ApprovedArtifact, ...]) -> None:
    """Require every superseded artifact to be retired from the active inventory.

    An artifact that declares ``supersedes:<kind>:<path>`` asserts it replaced
    that artifact. The assertion is machine-checkable exactly once: the named
    artifact must no longer be active. Keeping both is the old/new coexistence
    the recency law forbids, so it raises instead of being ordered silently.
    """

    active = {artifact.identity: artifact for artifact in artifacts}
    if len(active) != len(artifacts):
        duplicated = sorted(
            identity
            for identity in active
            if sum(one.identity == identity for one in artifacts) > 1
        )
        raise ValueError(f"duplicate artifact identity: {duplicated[0]}")
    for artifact in sorted(artifacts, key=lambda one: one.identity):
        for tag in artifact.tags:
            if not tag.startswith("supersedes:"):
                continue
            identity = supersedes_identity(tag)
            if identity is None:
                continue
            superseded = active.get(identity)
            if superseded is not None:
                raise ValueError(
                    f"{artifact.source}: supersedes {identity!r}, which is still "
                    f"active at {superseded.source}; retire it in this change"
                )
            _require_historical_identity(root, identity, artifact.source)


def core_tags(tags: tuple[str, ...]) -> tuple[str, ...]:
    """Return the tags outside the approval namespaces, order preserved."""

    return tuple(tag for tag in tags if not tag.startswith(_APPROVAL_PREFIXES))


def approval_tags(tags: tuple[str, ...]) -> tuple[str, ...]:
    """Return the approval-namespaced tags, order preserved."""

    return tuple(tag for tag in tags if tag.startswith(_APPROVAL_PREFIXES))


__all__ = (
    "APPROVAL_NAMESPACES",
    "ApprovedArtifact",
    "approval_note",
    "approval_tags",
    "audit_precedence",
    "core_tags",
    "resolve_approval_tags",
    "resolve_reference",
    "supersedes_identity",
    "validate_decision_tag",
    "validate_effective_tag",
    "validate_supersedes_tag",
)
