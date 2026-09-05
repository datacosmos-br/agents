"""Observable contract tests for the public semantic bundle facade."""

from __future__ import annotations

from importlib.metadata import distribution

from agents_governance import (
    BUNDLE_SCHEMA_VERSION,
    EvalPolicy,
    GovernanceBundle,
    __version__,
)


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
    assert skills["python-development"].parents == ("solid",)
    assert skills["flext-development"].parents == ("python-development",)


def test_distribution_exposes_no_runtime_executable() -> None:
    metadata = distribution("agents-governance")
    assert not metadata.entry_points
