from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import yaml

from agents_governance.approvals import (
    resolve_approval_tags,
    resolve_reference,
    validate_decision_tag,
    validate_effective_tag,
    validate_supersedes_tag,
)
from agents_governance.catalog import Catalog
from agents_governance.commands import (
    CommandIntent,
    CommandRisk,
    CommandRoute,
    CommandSpec,
    CommandTokenBudget,
    audit_command_specs,
    render_command,
)
from agents_governance.rule_adapters import RuleContext, RuleProvider, render_rule
from agents_governance.rules import RuleActivation, audit_rule_specs

_BUDGETS = {
    "router_tokens": 500,
    "frozen_tokens": 1200,
    "on_demand_tokens": 5000,
    "max_lines": 500,
}


def _docs(root: Path) -> None:
    adr = root / "docs" / "adr"
    adr.mkdir(parents=True, exist_ok=True)
    (adr / "ADR-0001-demo.md").write_text("# ADR-0001\n", encoding="utf-8")
    plans = root / "docs" / "execution" / "master-v7"
    plans.mkdir(parents=True, exist_ok=True)
    (plans / "11-distribution.md").write_text("# 11\n", encoding="utf-8")


def _future() -> str:
    stamp = datetime.now(tz=UTC).date() + timedelta(days=1)
    return stamp.isoformat()


def test_effective_tag_accepts_a_real_past_date() -> None:
    validate_effective_tag("effective:2026-08-30")


@pytest.mark.parametrize(
    "tag",
    [
        "effective:2026-08-3",
        "effective:26-08-30",
        "effective:2026/08/30",
        "effective:2026-08-30T00:00:00",
        "effective:yesterday",
    ],
)
def test_effective_tag_rejects_malformed_dates(tag: str) -> None:
    with pytest.raises(ValueError, match="malformed effective tag"):
        validate_effective_tag(tag)


def test_effective_tag_lets_the_raw_calendar_error_escape() -> None:
    with pytest.raises(ValueError):
        validate_effective_tag("effective:2026-02-30")


def test_effective_tag_rejects_future_dates() -> None:
    with pytest.raises(ValueError, match="effective date is in the future"):
        validate_effective_tag(f"effective:{_future()}")


@pytest.mark.parametrize(
    "tag,reference",
    [
        ("decision:ADR-0001", "ADR-0001"),
        ("decision:plan-11", "plan-11"),
        ("decision:plan-11-inc3", "plan-11-inc3"),
    ],
)
def test_decision_tag_returns_its_reference(tag: str, reference: str) -> None:
    assert validate_decision_tag(tag) == reference


@pytest.mark.parametrize(
    "tag",
    ["decision:adr-0001", "decision:ADR-123", "decision:plan-1", "decision:plan-123"],
)
def test_decision_tag_rejects_unsupported_references(tag: str) -> None:
    with pytest.raises(ValueError, match="unsupported approval reference"):
        validate_decision_tag(tag)


def test_supersedes_tag_shares_the_reference_grammar() -> None:
    assert validate_supersedes_tag("supersedes:plan-11") == "plan-11"
    with pytest.raises(ValueError, match="unsupported approval reference"):
        validate_supersedes_tag("supersedes:skill:caveman")


def test_reference_resolves_to_exactly_one_document(tmp_path: Path) -> None:
    _docs(tmp_path)
    assert resolve_reference(tmp_path, "ADR-0001").name == "ADR-0001-demo.md"
    assert resolve_reference(tmp_path, "plan-11").name == "11-distribution.md"
    assert resolve_reference(tmp_path, "plan-11-inc9").name == "11-distribution.md"


def test_unresolvable_reference_fails_loud(tmp_path: Path) -> None:
    _docs(tmp_path)
    with pytest.raises(ValueError, match="exactly one document"):
        resolve_reference(tmp_path, "ADR-0002")
    with pytest.raises(ValueError, match="exactly one document"):
        resolve_reference(tmp_path, "plan-12")


def test_mixed_approval_tags_validate_together(tmp_path: Path) -> None:
    _docs(tmp_path)
    resolve_approval_tags(
        tmp_path,
        (
            "decision:ADR-0001",
            "effective:2026-08-30",
            "supersedes:plan-11",
        ),
        Path("SKILL.md"),
    )
    with pytest.raises(ValueError, match="exactly one document"):
        resolve_approval_tags(
            tmp_path,
            ("decision:plan-12", "effective:2026-08-30"),
            Path("SKILL.md"),
        )


@pytest.mark.parametrize(
    "tags,kind",
    [
        (("effective:2026-08-30",), "decision"),
        (("decision:ADR-0001",), "effective"),
        (
            ("decision:ADR-0001", "decision:plan-11", "effective:2026-08-30"),
            "decision",
        ),
        (
            (
                "decision:ADR-0001",
                "effective:2026-08-29",
                "effective:2026-08-30",
            ),
            "effective",
        ),
    ],
)
def test_approval_tags_require_exactly_one_decision_and_effective(
    tmp_path: Path, tags: tuple[str, ...], kind: str
) -> None:
    _docs(tmp_path)

    with pytest.raises(ValueError, match=rf"exactly one {kind}: tag"):
        resolve_approval_tags(tmp_path, tags, Path("SKILL.md"))


def _rule(
    root: Path, relative: str, tags: tuple[str, ...], *, with_docs: bool = True
) -> Path:
    if with_docs:
        _docs(root)
    path = root / "rules" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(tags, separators=(",", ":"))
    path.write_text(
        "---\n"
        "description: One typed rule.\n"
        "metadata:\n"
        f"  aihub.tags: '{encoded}'\n"
        "---\n\n# Rule\n",
        encoding="utf-8",
    )
    return path


def test_rules_accept_fully_resolved_approval_tags(tmp_path: Path) -> None:
    _rule(
        tmp_path,
        "coordination/approval.md",
        (
            "decision:ADR-0001",
            "effective:2026-08-30",
            "route:project",
            "supersedes:plan-11",
        ),
    )

    rules = audit_rule_specs(tmp_path)

    assert [rule.identity for rule in rules] == ["coordination/approval"]


def test_rules_reject_dangling_approval_references(tmp_path: Path) -> None:
    _rule(
        tmp_path,
        "dangling.md",
        ("decision:ADR-0009", "effective:2026-08-30", "route:personal"),
    )

    with pytest.raises(ValueError, match="exactly one document"):
        audit_rule_specs(tmp_path)


def test_rules_reject_non_approval_extra_tags(tmp_path: Path) -> None:
    _rule(
        tmp_path,
        "extra.md",
        ("domain:gas-city", "effective:2026-08-30", "route:personal"),
    )

    with pytest.raises(ValueError, match="route and approval tags"):
        audit_rule_specs(tmp_path)


def test_rules_still_require_exactly_one_route_tag(tmp_path: Path) -> None:
    _rule(tmp_path, "routed.md", ("decision:ADR-0001", "effective:2026-08-30"))

    with pytest.raises(ValueError, match="exactly one supported route tag"):
        audit_rule_specs(tmp_path)


def _command(root: Path, tags: tuple[str, ...], *, with_docs: bool = True) -> Path:
    if with_docs:
        _docs(root)
    path = root / "commands" / "governance" / "demo-command.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(tags, separators=(",", ":"))
    path.write_text(
        "---\n"
        "name: demo-command\n"
        "description: Demonstrates approval tags.\n"
        "metadata:\n"
        f"  aihub.tags: '{encoded}'\n"
        "---\n\n# Demo command\n",
        encoding="utf-8",
    )
    return path


def test_commands_accept_fully_resolved_approval_tags(tmp_path: Path) -> None:
    _command(
        tmp_path,
        (
            "decision:ADR-0001",
            "effective:2026-08-30",
            "intent:inspection",
            "risk:read",
            "route:project",
        ),
    )

    commands = audit_command_specs(tmp_path)

    assert [command.name for command in commands] == ["demo-command"]


def test_commands_reject_dangling_approval_references(tmp_path: Path) -> None:
    _command(
        tmp_path,
        (
            "decision:plan-12",
            "effective:2026-08-30",
            "intent:inspection",
            "risk:read",
            "route:project",
        ),
    )

    with pytest.raises(ValueError, match="exactly one document"):
        audit_command_specs(tmp_path)


def _skill(root: Path, category: str, name: str, tags: tuple[str, ...]) -> Path:
    directory = root / "skills" / category / name
    directory.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(tags, separators=(",", ":"))
    (directory / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {name}, approval validation\n"
        "metadata:\n"
        f"  aihub.tags: '{encoded}'\n"
        "---\n"
        f"# {name}\n",
        encoding="utf-8",
    )
    return directory


def _config(root: Path) -> None:
    (root / "config").mkdir(exist_ok=True)
    (root / "config" / "skills.json").write_text(
        json.dumps({"version": 2, "budgets": _BUDGETS}), encoding="utf-8"
    )


def test_catalog_resolves_approval_tags_against_its_root(tmp_path: Path) -> None:
    _config(tmp_path)
    _docs(tmp_path)
    _skill(
        tmp_path,
        "agent-wide",
        "approved",
        (
            "decision:ADR-0001",
            "effective:2026-08-30",
            "policy:strict-execution",
            "provenance:agents-owned",
            "updates:manual",
            "usage:on-demand",
        ),
    )

    catalog = Catalog(tmp_path)

    assert tuple(record["name"] for record in catalog.inventory()) == ("approved",)


def test_catalog_rejects_dangling_approval_tags(tmp_path: Path) -> None:
    _config(tmp_path)
    _docs(tmp_path)
    _skill(
        tmp_path,
        "agent-wide",
        "dangling",
        (
            "decision:ADR-0009",
            "effective:2026-08-30",
            "policy:strict-execution",
            "provenance:agents-owned",
            "updates:manual",
            "usage:on-demand",
        ),
    )

    with pytest.raises(ValueError, match="exactly one document"):
        Catalog(tmp_path)


def test_project_skills_resolve_approvals_against_central_authority(
    tmp_path: Path,
) -> None:
    authority_root = tmp_path / "authority"
    project_root = tmp_path / "project"
    authority_root.mkdir()
    project_root.mkdir()
    _config(authority_root)
    _docs(authority_root)
    _skill(
        authority_root,
        "agent-wide",
        "central",
        (
            "decision:ADR-0001",
            "effective:2026-08-30",
            "policy:strict-execution",
            "provenance:agents-owned",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    _skill(
        project_root,
        "tool",
        "local-approved",
        (
            "activation:opt-in",
            "decision:ADR-0001",
            "detect:opt-in:local-approved",
            "effective:2026-08-30",
            "provenance:project-owned",
            "route:project",
            "tool:approvals",
            "updates:manual",
            "usage:on-demand",
        ),
    )

    authority = Catalog(authority_root)
    catalog = Catalog.project(project_root, authority)

    assert tuple(record["name"] for record in catalog.inventory()) == (
        "local-approved",
    )


def _tagged_rule_spec(tmp_path: Path, tags: tuple[str, ...]):
    _docs(tmp_path)
    path = tmp_path / "rules" / "tagged.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Tagged\n", encoding="utf-8")
    return __import__("agents_governance").rules.RuleSpec(
        path,
        "tagged",
        "One tagged rule.",
        RuleActivation.ALWAYS,
        (),
        (),
        "# Tagged\n",
        tags,
    )


def test_rule_projection_carries_the_approval_note(tmp_path: Path) -> None:
    spec = _tagged_rule_spec(
        tmp_path,
        ("decision:ADR-0001", "effective:2026-08-30", "route:personal"),
    )

    content = render_rule(spec, RuleProvider.CLAUDE, RuleContext.PERSONAL).content

    assert "<!-- aihub.approval: decision:ADR-0001; effective:2026-08-30 -->" in content
    assert (
        render_rule(spec, RuleProvider.CLAUDE, RuleContext.PERSONAL).content == content
    )


def test_untagged_rule_projection_has_no_approval_note(tmp_path: Path) -> None:
    spec = _tagged_rule_spec(tmp_path, ("route:personal",))

    content = render_rule(spec, RuleProvider.CLAUDE, RuleContext.PERSONAL).content

    assert "aihub.approval" not in content


def _command_spec(tmp_path: Path, tags: tuple[str, ...]) -> CommandSpec:
    return CommandSpec(
        tmp_path / "commands" / "governance" / "demo-command.md",
        "demo-command",
        "Demonstrates approval tags.",
        None,
        tags,
        CommandRoute.PROJECT,
        (CommandIntent.INSPECTION,),
        CommandRisk.READ,
        "# Demo command\n",
    )


def _budget() -> CommandTokenBudget:
    return CommandTokenBudget(max_tokens=None, counter=lambda content: len(content))


def test_command_projection_carries_the_approval_note(tmp_path: Path) -> None:
    spec = _command_spec(
        tmp_path,
        (
            "decision:ADR-0001",
            "intent:inspection",
            "risk:read",
            "route:project",
        ),
    )

    artifact = render_command(spec, "claude", token_budget=_budget())

    assert "<!-- aihub.approval: decision:ADR-0001 -->" in artifact.content
    again = render_command(spec, "claude", token_budget=_budget())
    assert again.content == artifact.content


def test_untagged_command_projection_has_no_approval_note(tmp_path: Path) -> None:
    spec = _command_spec(
        tmp_path,
        ("intent:inspection", "risk:read", "route:project"),
    )

    artifact = render_command(spec, "claude", token_budget=_budget())

    assert "aihub.approval" not in artifact.content


REPOSITORY = Path(__file__).resolve().parents[1]


def _canonical_tags(path: Path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"missing frontmatter: {path}"
    frontmatter = yaml.safe_load(text[4 : text.find("\n---\n", 4)])
    raw = frontmatter["metadata"]["aihub.tags"]
    return tuple(json.loads(raw))


def test_real_inventory_carries_resolvable_approval_tags() -> None:
    targets = sorted(
        [p for p in (REPOSITORY / "rules").rglob("*.md") if p.is_file()]
        + [p for p in (REPOSITORY / "skills").rglob("SKILL.md") if p.is_file()]
        + [p for p in (REPOSITORY / "commands").rglob("*.md") if p.is_file()]
    )
    assert len(targets) >= 100

    for path in targets:
        tags = _canonical_tags(path)
        decisions = [tag for tag in tags if tag.startswith("decision:")]
        effective = [tag for tag in tags if tag.startswith("effective:")]
        assert len(decisions) == 1, f"{path}: exactly one decision: tag required"
        assert len(effective) == 1, f"{path}: exactly one effective: tag required"
        resolve_approval_tags(REPOSITORY, tags, path)
