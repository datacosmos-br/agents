from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import pytest

from agents_governance.catalog import Catalog
from agents_governance.commands import CommandSpec, audit_command_specs
from agents_governance.governance_config import (
    audit_governance_config,
    load_governance_config,
)
from agents_governance.rules import RuleSpec, audit_rule_specs


def _inventory(
    root: Path,
) -> tuple[Catalog, tuple[CommandSpec, ...], tuple[RuleSpec, ...]]:
    catalog = Catalog(root)
    commands = audit_command_specs(root, (record.name for record in catalog.records()))
    rules = audit_rule_specs(root)
    return catalog, commands, rules


def test_repository_governance_resolves_every_guarantee_owner() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_governance_config(root)
    catalog, commands, rules = _inventory(root)

    audit_governance_config(root, config, catalog, commands, rules)

    assert config.version == 2
    assert "governance-artifact-composition" in config.guarantees
    assert "legacy-source-adjudication" in config.guarantees
    assert "fix-forward-collaboration" in config.guarantees
    assert "operator-precedence" in config.guarantees
    assert "tracker-evidence" in config.guarantees
    assert "architecture/engineering-core" in config.bootstrap_rules
    assert "workflow/beads-traceability" not in config.bootstrap_rules
    assert "fix-forward-collaboration" in config.bootstrap_skills


def test_governance_config_rejects_incomplete_guarantee_map(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root / "config" / "governance.json").read_text())
    payload["guarantees"].pop("fix-forward-collaboration")
    target = tmp_path / "config"
    target.mkdir()
    (target / "governance.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="cover every guarantee exactly"):
        load_governance_config(tmp_path)


def test_governance_config_rejects_retired_v1_schema(tmp_path: Path) -> None:
    target = tmp_path / "config"
    target.mkdir()
    (target / "governance.json").write_text(
        json.dumps(
            {
                "version": 1,
                "bootstrap": {
                    "rules": ["runtime/strict-execution"],
                    "skills": ["caveman"],
                },
                "legacy_core_clauses": {
                    "law-01-truth": ["rule:ethics/professional-integrity"]
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="fields must equal"):
        load_governance_config(tmp_path)


def test_governance_audit_rejects_missing_and_non_always_bootstrap_rules() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_governance_config(root)
    catalog, commands, rules = _inventory(root)

    missing = replace(config, bootstrap_rules=("missing/rule",))
    with pytest.raises(ValueError, match="bootstrap rule is missing"):
        audit_governance_config(root, missing, catalog, commands, rules)

    path_scoped = replace(config, bootstrap_rules=("python/no-hidden-errors",))
    with pytest.raises(ValueError, match="bootstrap rule is not always-on"):
        audit_governance_config(root, path_scoped, catalog, commands, rules)


@pytest.mark.parametrize(
    ("owner", "message"),
    (
        ("rule:missing/rule", "owner rule is missing"),
        ("skill:missing-skill", "owner skill is missing"),
        ("command:missing-command", "owner command is missing"),
        ("document:missing.md", "owner document is missing"),
    ),
)
def test_governance_audit_rejects_missing_guarantee_owner(
    owner: str, message: str
) -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_governance_config(root)
    catalog, commands, rules = _inventory(root)
    invalid = replace(
        config,
        guarantees=MappingProxyType({"invalid-guarantee": (owner,)}),
    )

    with pytest.raises(ValueError, match=message):
        audit_governance_config(root, invalid, catalog, commands, rules)


def test_active_governance_contract_has_no_monolith_residue() -> None:
    root = Path(__file__).resolve().parents[1]
    active = (
        root / "README.md",
        root / "config" / "governance.json",
        root / "src" / "agents_governance" / "governance_config.py",
        root / "docs" / "adr" / "ADR-0005-composed-governance-delivery.md",
        root
        / "docs"
        / "execution"
        / "master-v7"
        / "10-additive-capability-composition-plan.md",
    )
    forbidden = ("UNIVERSAL_CORE", "legacy_core", "law-01-", "operator-00-")

    for path in active:
        body = path.read_text(encoding="utf-8")
        assert not any(term in body for term in forbidden), path.relative_to(root)


def test_governance_map_covers_commands_and_keeps_owner_sets_distinct() -> None:
    """Commands are fully guaranteed; no guarantee shares a single-owner set;
    every bootstrap rule/skill appears in at least one guarantee."""

    root = Path(__file__).resolve().parents[1]
    config = load_governance_config(root)
    _catalog, commands, _rules = _inventory(root)

    mapped: set[str] = set()
    for owners in config.guarantees.values():
        for owner in owners:
            kind, identity = owner.split(":", 1)
            if kind in ("rule", "skill", "command"):
                mapped.add(owner)

    command_ids = {f"command:{command.name}" for command in commands}
    unmapped_commands = command_ids - mapped
    assert not unmapped_commands, (
        f"commands absent from guarantee map: {sorted(unmapped_commands)}"
    )

    single_owner_sets: dict[tuple[str, ...], str] = {}
    for guarantee, owners in sorted(config.guarantees.items()):
        if len(owners) != 1:
            continue
        key = tuple(owners)
        previous = single_owner_sets.setdefault(key, guarantee)
        assert previous == guarantee, (
            f"guarantees {previous} and {guarantee} share single-owner set {key}"
        )

    guaranteed_rules = {
        identity.split(":", 1)[1] for identity in mapped if identity.startswith("rule:")
    }
    guaranteed_skills = {
        identity.split(":", 1)[1]
        for identity in mapped
        if identity.startswith("skill:")
    }
    for identity in config.bootstrap_rules:
        assert identity in guaranteed_rules, (
            f"bootstrap rule not guaranteed: {identity}"
        )
    for name in config.bootstrap_skills:
        assert name in guaranteed_skills, f"bootstrap skill not guaranteed: {name}"
