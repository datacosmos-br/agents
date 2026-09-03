from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from conftest import approved, seed_approval_docs

from agents_governance.rules import (
    RuleActivation,
    RuleDistribution,
    audit_rule_specs,
    prompt_defense_body,
)


def _approved(
    body: str,
    *,
    description: str = "One typed rule.",
    extra: str = "",
    tags: tuple[str, ...] = (),
) -> str:
    """Build rule content that satisfies the mandatory approval contract."""

    routed = (
        tags
        if any(tag.startswith("route:") for tag in tags)
        else (
            *tags,
            "route:both",
        )
    )
    encoded = json.dumps(list(approved(routed)), separators=(",", ":"))
    return (
        "---\n"
        f"description: {description}\n"
        f"{extra}"
        "metadata:\n"
        f"  aihub.tags: '{encoded}'\n"
        "---\n\n"
        f"{body}"
    )


def _rule(root: Path, relative: str, content: str) -> Path:
    seed_approval_docs(root)
    path = root / "rules" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_recursive_discovery_returns_complete_strict_inventory(tmp_path: Path) -> None:
    baseline = _rule(tmp_path, "baseline.md", _approved("# Baseline\n"))
    scoped = _rule(
        tmp_path,
        "python/typing.md",
        _approved(
            "# Python typing\n\nRead [baseline](../baseline.md).\n",
            description="Apply strict Python typing.",
            extra="globs: ['*.py', '**/*.py']\n",
            tags=("route:project",),
        ),
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
        (_approved("   \n", description="Valid."), "body must be non-empty"),
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
    _rule(tmp_path, "first.md", _approved("# One authority\n"))
    _rule(tmp_path, "nested/second.md", _approved("# One authority\n"))

    with pytest.raises(ValueError, match="nested/second.md"):
        audit_rule_specs(tmp_path)


def test_rule_spec_rejects_mutated_derived_contract(tmp_path: Path) -> None:
    _rule(tmp_path, "baseline.md", _approved("# Baseline\n"))
    spec = audit_rule_specs(tmp_path)[0]

    with pytest.raises(ValueError, match="activation"):
        replace(spec, activation=RuleActivation.PATH_SCOPED)
    with pytest.raises(ValueError, match="path-derived"):
        replace(spec, identity="different")


def test_canonical_inventory_is_discovered_without_extinct_hook_rules() -> None:
    root = Path(__file__).resolve().parents[1]
    specs = {spec.identity: spec for spec in audit_rule_specs(root)}
    engineering_core = specs["architecture/engineering-core"].body

    assert "Every other executable" in engineering_core
    assert "authorized, selected" in engineering_core
    assert "PATH presence never selects" in engineering_core
    assert "managed-private owner set" in engineering_core
    assert "exact SSH remote" in engineering_core
    assert "HTTPS" in engineering_core
    assert "The first exception escapes" in engineering_core
    assert "complete the approved landing cycle" in " ".join(engineering_core.split())
    assert "security/prompt-defense" in specs
    assert (
        prompt_defense_body(tuple(specs.values()))
        == specs["security/prompt-defense"].body
    )
    assert not specs["security/prompt-defense"].body.lstrip().startswith("---")
    assert not any(identity.startswith("hooks/") for identity in specs)


def test_prompt_defense_body_requires_the_rule_owner() -> None:
    with pytest.raises(ValueError, match="prompt-defense owner is missing"):
        prompt_defense_body(())


def test_governance_artifact_composition_is_project_scoped() -> None:
    root = Path(__file__).resolve().parents[1]
    specs = {spec.identity: spec for spec in audit_rule_specs(root)}
    rule = specs["architecture/governance-artifact-composition"]

    assert rule.activation is RuleActivation.PATH_SCOPED
    assert rule.distribution is RuleDistribution.PROJECT
    assert {
        "commands/**/*.md",
        "config/governance.json",
        "evals/**",
        "rules/**/*.md",
        "skills/**",
    } == set(rule.globs)
    assert "historical artifacts are evidence only" in rule.body
