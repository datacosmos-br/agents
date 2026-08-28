from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

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


def test_repository_governance_resolves_every_retired_clause_owner() -> None:
    root = Path(__file__).resolve().parents[1]
    config = load_governance_config(root)
    catalog, commands, rules = _inventory(root)

    audit_governance_config(root, config, catalog, commands, rules)

    assert len(config.legacy_core_clauses) == 47
    assert "architecture/engineering-core" in config.bootstrap_rules
    assert "coordination/fix-forward-collaboration" in config.bootstrap_rules
    assert "workflow/beads-traceability" not in config.bootstrap_rules
    assert "fix-forward-collaboration" in config.bootstrap_skills


def test_governance_config_rejects_incomplete_clause_map(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root / "config" / "governance.json").read_text())
    payload["legacy_core_clauses"].pop("law-05-fix-forward")
    target = tmp_path / "config"
    target.mkdir()
    (target / "governance.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="cover every retired clause exactly"):
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
