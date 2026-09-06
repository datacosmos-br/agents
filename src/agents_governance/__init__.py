"""Provider-neutral governance records for AI Hub consumers."""

from .agent_profiles import AgentProfile
from .bundle import BUNDLE_SCHEMA_VERSION, GovernanceBundle
from .catalog import SkillCategory, SkillRecord
from .commands import CommandIntent, CommandRisk, CommandRoute, CommandSpec
from .governance_config import GovernanceConfig
from .law_surface import LawSurface
from .provenance import version as _distribution_version
from .rules import RuleActivation, RuleDistribution, RuleSpec
from .skill_evals import (
    EvalBehaviorGraderPolicy,
    EvalExecutionPolicy,
    EvalMetricPolicy,
    EvalPolicy,
)
from .skill_metadata import InterfaceMetadata, SkillMetadata, ToolDependency

__version__ = _distribution_version()

__all__ = (
    "BUNDLE_SCHEMA_VERSION",
    "AgentProfile",
    "CommandIntent",
    "CommandRisk",
    "CommandRoute",
    "CommandSpec",
    "EvalBehaviorGraderPolicy",
    "EvalExecutionPolicy",
    "EvalMetricPolicy",
    "EvalPolicy",
    "GovernanceBundle",
    "GovernanceConfig",
    "InterfaceMetadata",
    "LawSurface",
    "RuleActivation",
    "RuleDistribution",
    "RuleSpec",
    "SkillCategory",
    "SkillMetadata",
    "SkillRecord",
    "ToolDependency",
    "__version__",
)
