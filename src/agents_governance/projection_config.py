"""Strict owner for the provider/context/surface projection matrix."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType

from .agent_profiles import AgentProvider


class ProjectionContext(StrEnum):
    """Projection ownership context."""

    PERSONAL = "personal"
    PROJECT = "project"


class ProjectionSurface(StrEnum):
    """Public artifact surfaces governed by the projection owner."""

    SKILLS = "skills"
    COMMANDS = "commands"
    AGENTS = "agents"
    RULES = "rules"
    HOOKS = "hooks"


class ProjectionStatus(StrEnum):
    """Closed support classification for every matrix cell."""

    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


class HookCoverage(StrEnum):
    """Fidelity of a provider event to one logical governance boundary."""

    EXACT = "exact"
    EQUIVALENT = "equivalent"
    ADVISORY = "advisory"


class HookClient(StrEnum):
    """Provider client scope where one native lifecycle event exists."""

    CLOUD = "cloud"
    LOCAL = "local"


class RuleLayout(StrEnum):
    """Native storage shape for synchronized rule instructions."""

    DIRECTORY = "directory"
    DOCUMENT = "document"


class DetectionConditionType(StrEnum):
    """Closed set of project detection predicates."""

    FILE_CONTAINS = "file_contains"
    FILE_NOT_CONTAINS = "file_not_contains"
    PATH_EXISTS = "path_exists"
    PATH_MISSING = "path_missing"


class DetectionOperator(StrEnum):
    """Boolean composition supported by one project detection rule."""

    ALL = "all"
    ANY = "any"
    NONE = "none"


@dataclass(frozen=True)
class DetectionCondition:
    """One validated project detection condition."""

    condition_type: DetectionConditionType
    pattern: str
    paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProjectDetectionRule:
    """One validated declarative project classification rule."""

    rule_id: str
    activate_tags: tuple[str, ...]
    operator: DetectionOperator
    conditions: tuple[DetectionCondition, ...]


@dataclass(frozen=True)
class HookEvent:
    """One logical lifecycle boundary with explicit native support."""

    status: ProjectionStatus
    native: tuple[str, ...] = ()
    coverage: HookCoverage | None = None
    clients: tuple[HookClient, ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class ProjectionCell:
    """One validated provider/context/surface capability contract."""

    provider: AgentProvider
    context: ProjectionContext
    surface: ProjectionSurface
    status: ProjectionStatus
    path: str | None = None
    reason: str | None = None
    max_tokens: int | None = None
    events: MappingProxyType[str, HookEvent] | None = None
    layout: RuleLayout | None = None


@dataclass(frozen=True)
class ProjectionConfig:
    """Complete immutable calculated projection contract."""

    version: int
    projection_manifest_version: int
    hook_manifest_version: int
    project_detection_rules: tuple[ProjectDetectionRule, ...]
    cells: MappingProxyType[
        tuple[AgentProvider, ProjectionContext, ProjectionSurface], ProjectionCell
    ]

    def cell(
        self,
        provider: AgentProvider | str,
        context: ProjectionContext | str,
        surface: ProjectionSurface | str,
    ) -> ProjectionCell:
        key = (
            AgentProvider(provider),
            ProjectionContext(context),
            ProjectionSurface(surface),
        )
        return self.cells[key]


def _project_detection_rules() -> tuple[ProjectDetectionRule, ...]:
    """Calculate portable capability tags from generated project evidence."""

    return (
        ProjectDetectionRule(
            "associated-internal",
            ("internal",),
            DetectionOperator.ANY,
            (
                DetectionCondition(
                    DetectionConditionType.FILE_CONTAINS,
                    '"project_profile": "internal"',
                    (".aihub/project.json",),
                ),
            ),
        ),
        ProjectDetectionRule(
            "associated-internal-flext",
            ("internal-flext",),
            DetectionOperator.ANY,
            (
                DetectionCondition(
                    DetectionConditionType.FILE_CONTAINS,
                    '"project_profile": "internal_flext"',
                    (".aihub/project.json",),
                ),
            ),
        ),
        ProjectDetectionRule(
            "associated-upstream-fork",
            ("third-party-fork",),
            DetectionOperator.ANY,
            (
                DetectionCondition(
                    DetectionConditionType.FILE_CONTAINS,
                    '"project_profile": "third_party_fork"',
                    (".aihub/project.json",),
                ),
            ),
        ),
        ProjectDetectionRule(
            "flext-capability",
            ("flext",),
            DetectionOperator.ANY,
            (
                DetectionCondition(
                    DetectionConditionType.FILE_CONTAINS,
                    "@flext-managed",
                    ("pyproject.toml",),
                ),
            ),
        ),
    )


def _surface_path(
    provider: AgentProvider, context: ProjectionContext, surface: ProjectionSurface
) -> str | None:
    """Derive native destinations from provider, context, and artifact type."""

    personal = context is ProjectionContext.PERSONAL
    home = "${HOME}/" if personal else ""
    roots = {
        AgentProvider.CLAUDE: ".claude",
        AgentProvider.CODEX: ".codex" if personal else ".agents",
        AgentProvider.CURSOR: ".cursor",
        AgentProvider.COPILOT: ".copilot" if personal else ".github",
        AgentProvider.GEMINI: ".gemini",
        AgentProvider.OPENCODE: ".config/opencode" if personal else ".opencode",
        AgentProvider.ANTIGRAVITY: ".gemini/antigravity-cli" if personal else ".agents",
        AgentProvider.POOL: ".poolside",
    }
    root = home + roots[provider]
    if surface in {
        ProjectionSurface.SKILLS,
        ProjectionSurface.COMMANDS,
        ProjectionSurface.AGENTS,
    }:
        return f"{root}/{surface.value}"
    if surface is ProjectionSurface.RULES:
        names = {
            AgentProvider.CODEX: "AGENTS.md",
            AgentProvider.GEMINI: "GEMINI.md",
            AgentProvider.OPENCODE: "AGENTS.md",
            AgentProvider.ANTIGRAVITY: "GEMINI.md",
        }
        if provider in names:
            if provider is AgentProvider.CODEX and not personal:
                return "AGENTS.md"
            if provider is AgentProvider.GEMINI and not personal:
                return "GEMINI.md"
            if provider is AgentProvider.OPENCODE and not personal:
                return "AGENTS.md"
            if provider is AgentProvider.ANTIGRAVITY:
                return "${HOME}/.gemini/GEMINI.md"
            return f"{root}/{names[provider]}"
        return (
            f"{root}/{'instructions' if provider is AgentProvider.COPILOT else 'rules'}"
        )
    hook_names = {
        AgentProvider.CLAUDE: "settings.json",
        AgentProvider.CODEX: "hooks.json",
        AgentProvider.CURSOR: "hooks.json",
        AgentProvider.COPILOT: "hooks/aihub-governance.json",
        AgentProvider.GEMINI: "settings.json",
        AgentProvider.OPENCODE: "plugins/aihub-governance.ts",
        AgentProvider.ANTIGRAVITY: "plugins/aihub-governance/hooks.json"
        if personal
        else "hooks.json",
    }
    name = hook_names.get(provider)
    if name is None:
        return None
    hook_root = (
        ("${HOME}/.codex" if personal else ".codex")
        if provider is AgentProvider.CODEX
        else root
    )
    return f"{hook_root}/{name}"


def _supported(
    provider: AgentProvider, context: ProjectionContext, surface: ProjectionSurface
) -> bool:
    """Derive support from the provider-native renderer inventory."""

    if provider is AgentProvider.POOL:
        return (
            surface is ProjectionSurface.SKILLS and context is ProjectionContext.PROJECT
        )
    if surface in {ProjectionSurface.SKILLS, ProjectionSurface.HOOKS}:
        return True
    if surface is ProjectionSurface.COMMANDS:
        return provider in {
            AgentProvider.CLAUDE,
            AgentProvider.GEMINI,
            AgentProvider.OPENCODE,
        } or (provider is AgentProvider.CURSOR and context is ProjectionContext.PROJECT)
    if surface is ProjectionSurface.AGENTS:
        return provider in {
            AgentProvider.CLAUDE,
            AgentProvider.COPILOT,
            AgentProvider.GEMINI,
            AgentProvider.OPENCODE,
        }
    return (
        provider
        in {
            AgentProvider.CLAUDE,
            AgentProvider.CODEX,
            AgentProvider.COPILOT,
            AgentProvider.GEMINI,
            AgentProvider.OPENCODE,
        }
        or (provider is AgentProvider.CURSOR and context is ProjectionContext.PROJECT)
        or (
            provider is AgentProvider.ANTIGRAVITY
            and context is ProjectionContext.PERSONAL
        )
    )


def _hook_events(provider: AgentProvider) -> MappingProxyType[str, HookEvent]:
    """Return native lifecycle evidence owned by each hook adapter."""

    local = (HookClient.LOCAL,)
    cloud_local = (HookClient.CLOUD, HookClient.LOCAL)
    unsupported = HookEvent(
        ProjectionStatus.UNSUPPORTED,
        reason=f"UNSUPPORTED: {provider.value} exposes no documented subagent lifecycle boundary",
    )
    clients: tuple[tuple[HookClient, ...], ...]
    if provider in {AgentProvider.CLAUDE, AgentProvider.CODEX}:
        names = ("SessionStart", "UserPromptSubmit", "SessionStart", "SubagentStart")
        coverages = (HookCoverage.EXACT,) * 4
        clients = (local,) * 4
    elif provider is AgentProvider.CURSOR:
        names = ("sessionStart", "beforeSubmitPrompt", "preCompact", "subagentStart")
        coverages = (
            HookCoverage.EXACT,
            HookCoverage.ADVISORY,
            HookCoverage.ADVISORY,
            HookCoverage.ADVISORY,
        )
        clients = (local, cloud_local, cloud_local, cloud_local)
    elif provider is AgentProvider.COPILOT:
        names = ("sessionStart", "userPromptSubmitted", "preCompact", "subagentStart")
        coverages = (
            HookCoverage.EXACT,
            HookCoverage.ADVISORY,
            HookCoverage.ADVISORY,
            HookCoverage.EXACT,
        )
        clients = (local,) * 4
    elif provider is AgentProvider.GEMINI:
        return MappingProxyType(
            {
                "session_start": HookEvent(
                    ProjectionStatus.SUPPORTED,
                    ("SessionStart",),
                    HookCoverage.EXACT,
                    local,
                ),
                "prompt_submit": HookEvent(
                    ProjectionStatus.SUPPORTED,
                    ("BeforeAgent",),
                    HookCoverage.EXACT,
                    local,
                ),
                "context_refresh": HookEvent(
                    ProjectionStatus.SUPPORTED,
                    ("PreCompress", "BeforeAgent"),
                    HookCoverage.EQUIVALENT,
                    local,
                ),
                "subagent_start": unsupported,
            }
        )
    elif provider is AgentProvider.OPENCODE:
        event = "experimental.chat.system.transform"
        return MappingProxyType(
            {
                "session_start": HookEvent(
                    ProjectionStatus.SUPPORTED, (event,), HookCoverage.EQUIVALENT, local
                ),
                "prompt_submit": HookEvent(
                    ProjectionStatus.SUPPORTED, (event,), HookCoverage.EQUIVALENT, local
                ),
                "context_refresh": HookEvent(
                    ProjectionStatus.SUPPORTED,
                    ("experimental.session.compacting", event),
                    HookCoverage.EXACT,
                    local,
                ),
                "subagent_start": unsupported,
            }
        )
    else:
        names = ("PreInvocation",) * 4
        coverages = (HookCoverage.EQUIVALENT,) * 4
        clients = (local,) * 4
    return MappingProxyType(
        {
            name: HookEvent(
                ProjectionStatus.SUPPORTED, (native,), coverage, selected_clients
            )
            for name, native, coverage, selected_clients in zip(
                ("session_start", "prompt_submit", "context_refresh", "subagent_start"),
                names,
                coverages,
                clients,
                strict=True,
            )
        }
    )


def calculated_projection_config(_root: Path) -> ProjectionConfig:
    """Build the complete contract without a project or provider registry file."""

    cells: dict[
        tuple[AgentProvider, ProjectionContext, ProjectionSurface], ProjectionCell
    ] = {}
    for provider in AgentProvider:
        for context in ProjectionContext:
            for surface in ProjectionSurface:
                supported = _supported(provider, context, surface)
                path = _surface_path(provider, context, surface) if supported else None
                cells[(provider, context, surface)] = ProjectionCell(
                    provider,
                    context,
                    surface,
                    ProjectionStatus.SUPPORTED
                    if supported
                    else ProjectionStatus.UNSUPPORTED,
                    path=path,
                    reason=None
                    if supported
                    else f"UNSUPPORTED: {provider.value} has no native {context.value} {surface.value} contract",
                    events=_hook_events(provider)
                    if supported and surface is ProjectionSurface.HOOKS
                    else None,
                    layout=(
                        RuleLayout.DOCUMENT
                        if path is not None and path.endswith(".md")
                        else RuleLayout.DIRECTORY
                    )
                    if supported and surface is ProjectionSurface.RULES
                    else None,
                )
    return ProjectionConfig(
        8, 6, 3, _project_detection_rules(), MappingProxyType(cells)
    )


def load_projection_config(root: Path) -> ProjectionConfig:
    """Return provider-native contracts calculated by their typed owner."""

    return calculated_projection_config(root)


__all__ = (
    "DetectionCondition",
    "DetectionConditionType",
    "DetectionOperator",
    "HookClient",
    "HookCoverage",
    "HookEvent",
    "ProjectDetectionRule",
    "ProjectionCell",
    "ProjectionConfig",
    "ProjectionContext",
    "ProjectionStatus",
    "ProjectionSurface",
    "RuleLayout",
    "load_projection_config",
)
