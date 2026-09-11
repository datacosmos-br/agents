"""Typed delivery contract: capsule budget and lifecycle event payloads.

The session capsule is delivered as provider hook output, which truncates at
10,000 characters. This module owns the machine-checkable delivery contract:
the declared per-event payload map consumed by the runtime distributor, and
the measured budget proof that the always-on capsule composition fits the
declared ceiling before any projection is rendered.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import cast

from .catalog import SkillRecord
from .law_surface import LawSurface
from .rules import RuleSpec

_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_PAYLOAD = re.compile(rf"payload:{_SLUG.pattern}")

_FIELDS = frozenset({"capsule_budget_chars", "events", "restore_list_reserve_chars"})


@dataclass(frozen=True)
class DeliveryContract:
    """One validated delivery contract: budget ceilings and event payloads."""

    capsule_budget_chars: int
    restore_list_reserve_chars: int
    events: MappingProxyType[str, tuple[str, ...]]

    @classmethod
    def from_mapping(cls, value: object, source: str) -> DeliveryContract:
        """Build one contract from the parsed governance ``delivery`` mapping."""

        if not isinstance(value, Mapping):
            raise TypeError(f"{source}: delivery must be a mapping")
        mapping = cast(Mapping[str, object], value)
        unknown = frozenset(mapping) - _FIELDS
        if unknown:
            raise ValueError(
                f"{source}: unknown delivery fields: {', '.join(sorted(unknown))}"
            )
        budget = mapping.get("capsule_budget_chars")
        reserve = mapping.get("restore_list_reserve_chars")
        if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
            raise ValueError(
                f"{source}: delivery capsule_budget_chars must be a positive int"
            )
        if not isinstance(reserve, int) or isinstance(reserve, bool) or reserve <= 0:
            raise ValueError(
                f"{source}: delivery restore_list_reserve_chars must be a positive int"
            )
        events_raw = mapping.get("events")
        if not isinstance(events_raw, Mapping) or not events_raw:
            raise ValueError(f"{source}: delivery events must be a non-empty mapping")
        events_mapping = cast(Mapping[str, object], events_raw)
        if tuple(events_mapping) != tuple(sorted(events_mapping)):
            raise ValueError(f"{source}: delivery events must be sorted")
        events: dict[str, tuple[str, ...]] = {}
        for event, payloads in events_mapping.items():
            if not isinstance(event, str) or _SLUG.fullmatch(event) is None:
                raise ValueError(f"{source}: invalid delivery event name: {event}")
            if (
                not isinstance(payloads, list)
                or not payloads
                or not all(isinstance(one, str) for one in payloads)
            ):
                raise TypeError(
                    f"{source}: event {event} payloads must be non-empty strings"
                )
            ordered = tuple(cast(list[str], payloads))
            if ordered != tuple(sorted(ordered)) or len(ordered) != len(set(ordered)):
                raise ValueError(
                    f"{source}: event {event} payloads must be sorted and unique"
                )
            invalid = tuple(one for one in ordered if _PAYLOAD.fullmatch(one) is None)
            if invalid:
                raise ValueError(
                    f"{source}: event {event} payloads must match "
                    f"payload:<slug>: {', '.join(invalid)}"
                )
            events[event] = ordered
        return cls(
            budget,
            reserve,
            MappingProxyType(dict(sorted(events.items()))),
        )


@dataclass(frozen=True)
class DeliverySnapshot:
    """One measured capsule composition proven against the declared budget."""

    contract: DeliveryContract
    prelude_chars: int
    rule_summary_chars: int
    skill_index_chars: int
    total_chars: int

    @property
    def headroom_chars(self) -> int:
        return (
            self.contract.capsule_budget_chars
            - self.contract.restore_list_reserve_chars
            - self.total_chars
        )


def audit_delivery(
    config: DeliveryContract,
    law: LawSurface,
    rules: tuple[RuleSpec, ...],
    skills: tuple[SkillRecord, ...],
    bootstrap_rules: tuple[str, ...],
    bootstrap_skills: tuple[str, ...],
) -> DeliverySnapshot:
    """Measure the always-on capsule composition or raise past the budget."""

    by_identity = {rule.identity: rule for rule in rules}
    missing = tuple(ident for ident in bootstrap_rules if ident not in by_identity)
    if missing:
        raise ValueError(
            f"bootstrap rules missing from inventory: {', '.join(missing)}"
        )
    summary_chars = 0
    for ident in bootstrap_rules:
        summary = by_identity[ident].capsule_summary
        if not summary:
            raise ValueError(f"bootstrap rule {ident} declares no capsule_summary")
        summary_chars += len(summary)
    by_name = {skill.name: skill for skill in skills}
    missing_skills = tuple(name for name in bootstrap_skills if name not in by_name)
    if missing_skills:
        raise ValueError(
            f"bootstrap skills missing from inventory: {', '.join(missing_skills)}"
        )
    index_chars = sum(
        len(by_name[name].name) + len(by_name[name].description)
        for name in bootstrap_skills
    )
    prelude_chars = len(law.prelude)
    total = prelude_chars + summary_chars + index_chars
    ceiling = config.capsule_budget_chars - config.restore_list_reserve_chars
    if total > ceiling:
        raise ValueError(
            "session capsule exceeds its delivery budget: "
            f"{total} chars (prelude {prelude_chars} + rule summaries "
            f"{summary_chars} + skill index {index_chars}) against ceiling "
            f"{ceiling} (budget {config.capsule_budget_chars} minus restore-list "
            f"reserve {config.restore_list_reserve_chars})"
        )
    return DeliverySnapshot(
        config,
        prelude_chars,
        summary_chars,
        index_chars,
        total,
    )


__all__ = ("DeliveryContract", "DeliverySnapshot", "audit_delivery")
