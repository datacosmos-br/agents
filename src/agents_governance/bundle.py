"""Public immutable semantic governance bundle."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

from .agent_profiles import AgentProfile, audit_agent_profiles
from .approvals import ApprovedArtifact, audit_precedence
from .catalog import Catalog, SkillRecord
from .commands import CommandSpec, audit_command_specs
from .delivery import DeliverySnapshot, audit_delivery
from .governance_config import (
    GovernanceConfig,
    audit_governance_config,
    load_governance_config,
)
from .law_surface import LawSurface
from .provenance import version as distribution_version
from .resources import (
    CatalogResource,
    capture_resources,
    catalog_resources,
    resource_root,
)
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
    delivery: DeliverySnapshot
    _catalog_resources: tuple[CatalogResource, ...] = field(repr=False)

    @classmethod
    def load(cls, root: Path | None = None) -> GovernanceBundle:
        """Load and audit one complete snapshot or raise on its first defect."""

        source = (resource_root() if root is None else root).resolve(strict=True)
        captured = capture_resources(source)
        inputs = MappingProxyType(
            {source / resource.relative_path: resource for resource in captured}
        )
        catalog = Catalog(source, captured=inputs)
        skills = catalog.records()
        eval_policy = audit_skill_evals(source, skills, captured=inputs)
        commands = audit_command_specs(
            source, (skill.name for skill in skills), captured=inputs
        )
        agents = audit_agent_profiles(source, captured=inputs)
        rules = audit_rule_specs(source, captured=inputs)
        config = load_governance_config(source, captured=inputs)
        audit_governance_config(source, config, catalog, commands, rules)
        audit_precedence(source, _approved_artifacts(skills, commands, rules, agents))
        metadata = validate_skill_metadata(source, captured=inputs)
        law = LawSurface.load(source, captured=inputs)
        delivery = audit_delivery(
            config.delivery,
            law,
            rules,
            skills,
            config.bootstrap_rules,
            config.bootstrap_skills,
        )
        bundle = cls(
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
            delivery,
            captured,
        )
        catalog_resources(bundle)
        return bundle


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
