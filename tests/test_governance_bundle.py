"""Observable contract tests for the public semantic bundle facade."""

from __future__ import annotations

from importlib.metadata import distribution

import pytest

from agents_governance import (
    BUNDLE_SCHEMA_VERSION,
    EvalPolicy,
    GovernanceBundle,
    __version__,
)
from agents_governance.delivery import DeliveryContract


def test_public_bundle_is_complete_and_versioned(
    governance_bundle: GovernanceBundle,
) -> None:
    assert governance_bundle.schema_version == BUNDLE_SCHEMA_VERSION
    assert governance_bundle.distribution_version == __version__
    assert isinstance(governance_bundle.eval_policy, EvalPolicy)
    assert governance_bundle.root.is_dir()
    assert governance_bundle.skills
    assert governance_bundle.commands
    assert governance_bundle.agents
    assert governance_bundle.rules
    assert governance_bundle.config.guarantees
    assert governance_bundle.law.prelude


def test_public_inventories_have_unique_physical_owners(
    governance_bundle: GovernanceBundle,
) -> None:
    skills = {skill.name: skill.directory for skill in governance_bundle.skills}
    commands = {command.name: command.path for command in governance_bundle.commands}
    agents = {agent.name: agent.path for agent in governance_bundle.agents}
    rules = {rule.identity: rule.path for rule in governance_bundle.rules}

    assert len(skills) == len(governance_bundle.skills)
    assert len(commands) == len(governance_bundle.commands)
    assert len(agents) == len(governance_bundle.agents)
    assert len(rules) == len(governance_bundle.rules)
    assert all(path.is_dir() and not path.is_symlink() for path in skills.values())
    assert all(path.is_file() and not path.is_symlink() for path in commands.values())
    assert all(path.is_file() and not path.is_symlink() for path in agents.values())
    assert all(path.is_file() and not path.is_symlink() for path in rules.values())


def test_public_skill_hierarchy_composes_general_to_specialized(
    governance_bundle: GovernanceBundle,
) -> None:
    skills = {skill.name: skill for skill in governance_bundle.skills}

    assert skills["solid"].parents == ()
    assert skills["py-dev"].parents == ("solid",)
    assert skills["flext-development"].parents == ("py-dev",)


def test_distribution_exposes_no_runtime_executable() -> None:
    metadata = distribution("agents-governance")
    assert not metadata.entry_points


def test_delivery_budget_holds_with_measured_composition(
    governance_bundle: GovernanceBundle,
) -> None:
    delivery = governance_bundle.delivery
    contract = delivery.contract

    assert contract.capsule_budget_chars > contract.restore_list_reserve_chars > 0
    assert contract.events
    assert delivery.total_chars == (
        delivery.prelude_chars
        + delivery.rule_summary_chars
        + delivery.skill_index_chars
    )
    assert delivery.total_chars <= contract.capsule_budget_chars - (
        contract.restore_list_reserve_chars
    )
    assert delivery.headroom_chars >= 0


def test_delivery_contract_rejects_payload_outside_grammar() -> None:
    with pytest.raises(ValueError, match="payload:<slug>"):
        DeliveryContract.from_mapping(
            {
                "capsule_budget_chars": 10000,
                "restore_list_reserve_chars": 512,
                "events": {
                    "instructions-loaded": ["rule-bodies-by-routing"],
                    "post-compact": ["payload:capsule-full", "payload:restore-list"],
                    "prompt-submit": ["payload:operator-precedence-reminder"],
                    "session-end": ["payload:findings-harvest"],
                    "session-start": ["payload:capsule-full"],
                    "subagent-start": ["payload:authority-subset"],
                },
            },
            "test",
        )


def test_delivery_contract_rejects_unsorted_events() -> None:
    with pytest.raises(ValueError, match="events must be sorted"):
        DeliveryContract.from_mapping(
            {
                "capsule_budget_chars": 10000,
                "restore_list_reserve_chars": 512,
                "events": {
                    "session-start": ["payload:capsule-full"],
                    "instructions-loaded": ["payload:rule-bodies-by-routing"],
                    "post-compact": ["payload:capsule-full", "payload:restore-list"],
                    "prompt-submit": ["payload:operator-precedence-reminder"],
                    "session-end": ["payload:findings-harvest"],
                    "subagent-start": ["payload:authority-subset"],
                },
            },
            "test",
        )


def test_agent_approval_lineage_is_complete(
    governance_bundle: GovernanceBundle,
) -> None:
    for agent in governance_bundle.agents:
        namespaces = {tag.split(":", 1)[0] for tag in agent.tags}
        assert {"decision", "effective"} <= namespaces
