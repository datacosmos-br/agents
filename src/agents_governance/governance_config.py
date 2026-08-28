"""Typed owner for composed governance and legacy-core clause coverage."""

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
_ROOT_FIELDS = frozenset({"bootstrap", "legacy_core_clauses", "version"})
_BOOTSTRAP_FIELDS = frozenset({"rules", "skills"})


@dataclass(frozen=True)
class GovernanceConfig:
    """Complete immutable composition contract replacing the monolithic core."""

    version: int
    bootstrap_rules: tuple[str, ...]
    bootstrap_skills: tuple[str, ...]
    legacy_core_clauses: MappingProxyType[str, tuple[str, ...]]


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


def _expected_clauses() -> frozenset[str]:
    return frozenset(
        (
            "p0-tests-follow-config",
            "p0-strict-execution",
            "delete-policy",
            *(f"law-{index:02d}-{suffix}" for index, suffix in _LAW_SUFFIXES.items()),
            *(
                f"operator-{index:02d}-{suffix}"
                for index, suffix in _OPERATOR_SUFFIXES.items()
            ),
        )
    )


_LAW_SUFFIXES = {
    1: "truth",
    2: "research",
    3: "active-intent",
    4: "root-owner",
    5: "fix-forward",
    6: "generated-boundaries",
    7: "continuous-green",
    8: "ledger",
    9: "separated-roles",
    10: "no-report-stall",
    11: "history-evidence",
    12: "real-blocker",
    13: "short-slices",
    14: "living-docs",
    15: "runtime-first",
    16: "config-owner",
    17: "command-surface",
    18: "serialized-locks",
    19: "no-hidden-code",
    20: "concurrent-wip",
    21: "finish",
    22: "small-batches",
    23: "canonical-first",
    24: "current-ledger",
    25: "heartbeat",
    26: "evidence-for-uncertainty",
    27: "complete-cutover",
    28: "memory-not-law",
    29: "sprint-closure",
    30: "removal-now",
    31: "stage-gate",
}
_OPERATOR_SUFFIXES = {
    0: "precedence",
    1: "topic-monopoly",
    2: "lane-ownership",
    3: "reuse",
    4: "correction-learning",
    5: "exact-execution",
    6: "ethics",
    7: "real-tests",
    8: "project-law",
    9: "caveman",
    10: "context-lifecycle",
    11: "traceability",
    12: "cli-ux",
}


def load_governance_config(root: Path) -> GovernanceConfig:
    """Load the only accepted composed-governance schema."""

    path = root / "config" / "governance.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("governance config must be a physical regular file")
    value = _mapping(json.loads(path.read_text(encoding="utf-8")), "governance config")
    _exact_fields(value, _ROOT_FIELDS, "governance config")
    if value["version"] != 1:
        raise ValueError("governance config version must equal 1")
    bootstrap = _mapping(value["bootstrap"], "governance bootstrap")
    _exact_fields(bootstrap, _BOOTSTRAP_FIELDS, "governance bootstrap")
    clauses = _mapping(value["legacy_core_clauses"], "legacy core clause map")
    if frozenset(clauses) != _expected_clauses():
        raise ValueError(
            "legacy core clause map must cover every retired clause exactly"
        )
    parsed_clauses = {
        name: _strings(owners, f"legacy core clause {name}")
        for name, owners in clauses.items()
    }
    for clause, owners in parsed_clauses.items():
        for owner in owners:
            if _OWNER.fullmatch(owner) is None:
                raise ValueError(
                    f"legacy core clause {clause} has invalid owner: {owner}"
                )
    return GovernanceConfig(
        1,
        _strings(bootstrap["rules"], "governance bootstrap rules"),
        _strings(bootstrap["skills"], "governance bootstrap skills"),
        MappingProxyType(dict(sorted(parsed_clauses.items()))),
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
    for owners in config.legacy_core_clauses.values():
        for owner in owners:
            kind, identity = owner.split(":", 1)
            if kind == "rule" and identity not in rule_index:
                raise ValueError(f"legacy core owner rule is missing: {identity}")
            if kind == "skill" and identity not in skill_names:
                raise ValueError(f"legacy core owner skill is missing: {identity}")
            if kind == "command" and identity not in command_names:
                raise ValueError(f"legacy core owner command is missing: {identity}")
            if kind == "document":
                document = root / identity
                if document.is_symlink() or not document.is_file():
                    raise ValueError(
                        f"legacy core owner document is missing: {identity}"
                    )


__all__ = (
    "GovernanceConfig",
    "audit_governance_config",
    "load_governance_config",
)
