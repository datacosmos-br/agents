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
from .frontmatter import cast_mapping, require_exact_fields
from .rules import RuleActivation, RuleSpec

_OWNER = re.compile(r"(rule|skill|command|document):([A-Za-z0-9][A-Za-z0-9./_-]*)\Z")
_ROOT_FIELDS = frozenset({"bootstrap", "guarantees", "version"})
_BOOTSTRAP_FIELDS = frozenset({"rules", "skills"})
_EXPECTED_GUARANTEES = frozenset(
    {
        "active-intent",
        "atomic-effects",
        "bead-verification",
        "canonical-command-surface",
        "causal-subprocess",
        "complete-cutover",
        "concise-communication",
        "configuration-authority",
        "configuration-driven-tests",
        "context-lifecycle",
        "continuous-green",
        "correction-learning",
        "cross-runtime-session-handoff",
        "database-migration",
        "delivery-iteration",
        "evidence-backed-blocker",
        "evidence-backed-truth",
        "evidence-for-uncertainty",
        "execution-persistence",
        "execution-traceability",
        "fail-loud",
        "feature-development",
        "file-owned-handoff",
        "finish-through-closure",
        "fix-forward-collaboration",
        "gas-city-operations",
        "generated-boundaries",
        "github-issue-transparency",
        "governance-artifact-composition",
        "history-evidence",
        "immediate-removal",
        "lane-ownership",
        "language-rule-authoring",
        "legacy-source-adjudication",
        "living-documentation",
        "memory-is-not-authority",
        "no-fallback",
        "no-hidden-code",
        "no-keyring",
        "observable-tests",
        "operator-precedence",
        "owner-reuse",
        "preflight-before-effects",
        "production-readiness",
        "professional-integrity",
        "project-law",
        "pull-request-transparency",
        "repository-authority",
        "repository-research",
        "required-environment",
        "root-owner",
        "runtime-first",
        "security-evidence-authority",
        "security-triage-closure",
        "separated-roles",
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
    value = cast_mapping(
        json.loads(path.read_text(encoding="utf-8")), "governance config"
    )
    require_exact_fields(value, _ROOT_FIELDS, "governance config")
    if value["version"] != 2:
        raise ValueError("governance config version must equal 2")
    bootstrap = cast_mapping(value["bootstrap"], "governance bootstrap")
    require_exact_fields(bootstrap, _BOOTSTRAP_FIELDS, "governance bootstrap")
    guarantees = cast_mapping(value["guarantees"], "governance guarantee map")
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
