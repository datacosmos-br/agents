"""Typed owner for composed governance and semantic guarantee coverage."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import cast

from .catalog import Catalog
from .commands import CommandSpec
from .rules import RuleActivation, RuleSpec

_OWNER = re.compile(r"(rule|skill|command|document):([A-Za-z0-9][A-Za-z0-9./_-]*)\Z")
_ROOT_FIELDS = frozenset({"bootstrap", "guarantees", "version"})
_BOOTSTRAP_FIELDS = frozenset({"rules", "skills"})
_EXPECTED_GUARANTEES = frozenset(
    {
        "active-intent",
        "canonical-command-surface",
        "canonical-first",
        "cli-usability",
        "complete-cutover",
        "concise-communication",
        "concurrent-work-adoption",
        "configuration-authority",
        "configuration-driven-tests",
        "context-lifecycle",
        "continuous-green",
        "correction-learning",
        "current-tracker-state",
        "evidence-backed-blocker",
        "evidence-backed-truth",
        "evidence-for-uncertainty",
        "exact-execution",
        "execution-persistence",
        "execution-traceability",
        "finish-through-closure",
        "fix-forward-collaboration",
        "generated-boundaries",
        "governance-artifact-composition",
        "history-evidence",
        "immediate-removal",
        "lane-ownership",
        "living-documentation",
        "legacy-source-adjudication",
        "memory-is-not-authority",
        "no-hidden-code",
        "observable-tests",
        "operator-precedence",
        "owner-reuse",
        "professional-integrity",
        "project-law",
        "repository-research",
        "root-owner",
        "runtime-first",
        "safe-deletion",
        "separated-roles",
        "serialized-shared-state",
        "session-heartbeat",
        "short-integration-slices",
        "small-batches",
        "sprint-closure",
        "stage-gate",
        "strict-execution",
        "topic-monopoly",
        "tracker-evidence",
    }
)


@dataclass(frozen=True)
class GovernanceConfig:
    """Complete immutable composition contract for distributed governance."""

    version: int
    bootstrap_rules: tuple[str, ...]
    bootstrap_skills: tuple[str, ...]
    guarantees: MappingProxyType[str, tuple[str, ...]]


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{label} must be an object with string keys")
    return cast(dict[str, object], value)


def _exact_fields(
    value: dict[str, object], expected: frozenset[str], label: str
) -> None:
    if frozenset(value) != expected:
        raise ValueError(f"{label} fields must equal {', '.join(sorted(expected))}")


def _strings(value: object, label: str) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or not value
        or not all(
            isinstance(item, str) and item and item == item.strip() for item in value
        )
    ):
        raise TypeError(f"{label} must be a non-empty array of trimmed strings")
    parsed = tuple(cast(list[str], value))
    if len(parsed) != len(set(parsed)) or parsed != tuple(sorted(parsed)):
        raise ValueError(f"{label} must be unique and sorted")
    return parsed


def load_governance_config(root: Path) -> GovernanceConfig:
    """Load the only accepted composed-governance schema."""

    path = root / "config" / "governance.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("governance config must be a physical regular file")
    value = _mapping(json.loads(path.read_text(encoding="utf-8")), "governance config")
    _exact_fields(value, _ROOT_FIELDS, "governance config")
    if value["version"] != 2:
        raise ValueError("governance config version must equal 2")
    bootstrap = _mapping(value["bootstrap"], "governance bootstrap")
    _exact_fields(bootstrap, _BOOTSTRAP_FIELDS, "governance bootstrap")
    guarantees = _mapping(value["guarantees"], "governance guarantee map")
    if frozenset(guarantees) != _EXPECTED_GUARANTEES:
        raise ValueError("governance guarantee map must cover every guarantee exactly")
    parsed_guarantees = {
        name: _strings(owners, f"governance guarantee {name}")
        for name, owners in guarantees.items()
    }
    for guarantee, owners in parsed_guarantees.items():
        for owner in owners:
            if _OWNER.fullmatch(owner) is None:
                raise ValueError(
                    f"governance guarantee {guarantee} has invalid owner: {owner}"
                )
    return GovernanceConfig(
        2,
        _strings(bootstrap["rules"], "governance bootstrap rules"),
        _strings(bootstrap["skills"], "governance bootstrap skills"),
        MappingProxyType(dict(sorted(parsed_guarantees.items()))),
    )


def audit_governance_config(
    root: Path,
    config: GovernanceConfig,
    catalog: Catalog,
    commands: tuple[CommandSpec, ...],
    rules: tuple[RuleSpec, ...],
) -> None:
    """Resolve every mapped owner and require always-on bootstrap rules."""

    rule_index = {rule.identity: rule for rule in rules}
    skill_names = {record.name for record in catalog.records()}
    command_names = {command.name for command in commands}
    for identity in config.bootstrap_rules:
        rule = rule_index.get(identity)
        if rule is None:
            raise ValueError(f"governance bootstrap rule is missing: {identity}")
        if rule.activation is not RuleActivation.ALWAYS:
            raise ValueError(f"governance bootstrap rule is not always-on: {identity}")
    for name in config.bootstrap_skills:
        if name not in skill_names:
            raise ValueError(f"governance bootstrap skill is missing: {name}")
    for owners in config.guarantees.values():
        for owner in owners:
            kind, identity = owner.split(":", 1)
            if kind == "rule" and identity not in rule_index:
                raise ValueError(f"governance owner rule is missing: {identity}")
            if kind == "skill" and identity not in skill_names:
                raise ValueError(f"governance owner skill is missing: {identity}")
            if kind == "command" and identity not in command_names:
                raise ValueError(f"governance owner command is missing: {identity}")
            if kind == "document":
                document = root / identity
                if document.is_symlink() or not document.is_file():
                    raise ValueError(
                        f"governance owner document is missing: {identity}"
                    )


__all__ = (
    "GovernanceConfig",
    "audit_governance_config",
    "load_governance_config",
)
