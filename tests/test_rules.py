from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from agents_governance.rules import (
    RuleActivation,
    RuleDistribution,
    audit_rule_specs,
)


def _rule(root: Path, relative: str, content: str) -> Path:
    path = root / "rules" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_recursive_discovery_returns_complete_strict_inventory(tmp_path: Path) -> None:
    baseline = _rule(tmp_path, "baseline.md", "# Baseline\n")
    scoped = _rule(
        tmp_path,
        "python/typing.md",
        "---\n"
        "description: Apply strict Python typing.\n"
        "globs: ['*.py', '**/*.py']\n"
        "metadata:\n"
        "  aihub.tags: '[\"route:project\"]'\n"
        "---\n\n"
        "# Python typing\n\nRead [baseline](../baseline.md).\n",
    )

    rules = audit_rule_specs(tmp_path)

    assert [rule.path for rule in rules] == [baseline, scoped]
    assert rules[0].activation is RuleActivation.ALWAYS
    assert rules[0].distribution is RuleDistribution.BOTH
    assert rules[1].activation is RuleActivation.PATH_SCOPED
    assert rules[1].distribution is RuleDistribution.PROJECT
    assert rules[1].references == ("rules/baseline.md",)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("---\ndescription: [broken\n---\n# Rule\n", "expected"),
        ("---\nname: invented\n---\n# Rule\n", "unknown rule fields"),
        ("---\ndescription: ''\n---\n# Rule\n", "description"),
        ("---\nglobs: []\n---\n# Rule\n", "must not be empty"),
        ("---\nglobs: ../outside.py\n---\n# Rule\n", "repository-local"),
        ("---\ndescription: Valid.\n---\n   \n", "body must be non-empty"),
    ],
)
def test_invalid_rule_raises_first_defect(
    tmp_path: Path, content: str, message: str
) -> None:
    _rule(tmp_path, "invalid.md", content)

    with pytest.raises((TypeError, ValueError, yaml.YAMLError), match=message):
        audit_rule_specs(tmp_path)


@pytest.mark.parametrize(
    "target",
    ["missing.md", "../../outside.md", "/absolute.md", "file:///outside.md"],
)
def test_invalid_local_reference_raises(tmp_path: Path, target: str) -> None:
    _rule(tmp_path, "workflow/source.md", f"Read [target]({target}).\n")

    with pytest.raises((FileNotFoundError, ValueError)):
        audit_rule_specs(tmp_path)


def test_invalid_physical_inventory_raises(tmp_path: Path) -> None:
    _rule(tmp_path, "valid.md", "# Valid\n")
    (tmp_path / "rules" / "foreign.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Markdown"):
        audit_rule_specs(tmp_path)


def test_duplicate_bodies_raise_at_second_sorted_owner(tmp_path: Path) -> None:
    _rule(tmp_path, "first.md", "# One authority\n")
    _rule(tmp_path, "nested/second.md", "# One authority\n")

    with pytest.raises(ValueError, match="nested/second.md"):
        audit_rule_specs(tmp_path)


def test_rule_spec_rejects_mutated_derived_contract(tmp_path: Path) -> None:
    _rule(tmp_path, "baseline.md", "# Baseline\n")
    spec = audit_rule_specs(tmp_path)[0]

    with pytest.raises(ValueError, match="activation"):
        replace(spec, activation=RuleActivation.PATH_SCOPED)
    with pytest.raises(ValueError, match="path-derived"):
        replace(spec, identity="different")


def test_canonical_inventory_is_discovered_without_extinct_hook_rules() -> None:
    root = Path(__file__).resolve().parents[1]
    identities = tuple(spec.identity for spec in audit_rule_specs(root))

    assert "architecture/engineering-core" in identities
    assert "security/prompt-defense" in identities
    assert not any(identity.startswith("hooks/") for identity in identities)
