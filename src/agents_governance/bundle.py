"""Public immutable semantic governance bundle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .agent_profiles import AgentProfile, audit_agent_profiles
from .approvals import ApprovedArtifact, audit_precedence
from .catalog import Catalog, SkillRecord
from .commands import CommandSpec, audit_command_specs
from .governance_config import (
    GovernanceConfig,
    audit_governance_config,
    load_governance_config,
)
from .law_surface import LawSurface
from .provenance import version as distribution_version
from .resources import resource_root
from .rules import RuleSpec, audit_rule_specs
from .skill_evals import EvalPolicy, audit_skill_evals
from .skill_metadata import SkillMetadata
from .skill_metadata import validate as validate_skill_metadata

BUNDLE_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class GovernanceBundle:
    """A validated snapshot of the package's provider-neutral governance."""

    root: Path
    schema_version: int
    distribution_version: str
    config: GovernanceConfig
    eval_policy: EvalPolicy
    skills: tuple[SkillRecord, ...]
    skill_metadata: tuple[SkillMetadata, ...]
    commands: tuple[CommandSpec, ...]
    agents: tuple[AgentProfile, ...]
    rules: tuple[RuleSpec, ...]
    law: LawSurface

    @classmethod
    def load(cls, root: Path | None = None) -> GovernanceBundle:
        """Load and audit one complete snapshot or raise on its first defect."""

        source = (resource_root() if root is None else root).resolve(strict=True)
        catalog = Catalog(source)
        skills = catalog.records()
        eval_policy = audit_skill_evals(source, skills)
        commands = audit_command_specs(source, (skill.name for skill in skills))
        agents = audit_agent_profiles(source)
        rules = audit_rule_specs(source)
        config = load_governance_config(source)
        audit_governance_config(source, config, catalog, commands, rules)
        audit_precedence(source, _approved_artifacts(skills, commands, rules, agents))
        metadata = validate_skill_metadata(source)
        law = LawSurface.load(source)
        return cls(
            source,
            BUNDLE_SCHEMA_VERSION,
            distribution_version(),
            config,
            eval_policy,
            skills,
            metadata,
            commands,
            agents,
            rules,
            law,
        )


def _approved_artifacts(
    skills: tuple[SkillRecord, ...],
    commands: tuple[CommandSpec, ...],
    rules: tuple[RuleSpec, ...],
    agents: tuple[AgentProfile, ...],
) -> tuple[ApprovedArtifact, ...]:
    return (
        *(
            ApprovedArtifact(f"rule:{rule.identity}", rule.tags, rule.path)
            for rule in rules
        ),
        *(
            ApprovedArtifact(
                f"skill:{skill.name}", skill.tags, skill.directory / "SKILL.md"
            )
            for skill in skills
        ),
        *(
            ApprovedArtifact(f"command:{command.name}", command.tags, command.path)
            for command in commands
        ),
        *(
            ApprovedArtifact(f"agent:{agent.name}", agent.tags, agent.path)
            for agent in agents
        ),
    )


__all__ = ("BUNDLE_SCHEMA_VERSION", "GovernanceBundle")
