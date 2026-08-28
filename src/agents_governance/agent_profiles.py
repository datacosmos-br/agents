"""Typed validation for canonical, provider-neutral agent profiles."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import cast

import yaml

from .catalog import NON_PORTABLE_PROJECT_REFERENCE

_DISTRIBUTIONS = frozenset({"agent-wide", "project-wide"})
_ACTIVATIONS = frozenset(
    {"activation:always", "activation:detected", "activation:opt-in"}
)
_MODES = frozenset(
    {"mode:debug", "mode:execute", "mode:operate", "mode:plan", "mode:review"}
)
_RETIRED_SURFACES = frozenset({"dispatcher.md", "manifest.json"})
_PROMPT_DEFENSE_RULE = "rules/security/prompt-defense.md"
_INLINE_PROMPT_DEFENSE = "## Prompt Defense Baseline"
_TOP_LEVEL_FIELDS = frozenset({"name", "description", "tools", "metadata", "model"})
_TOOL = re.compile(r"^[A-Za-z0-9_.:-]+$")
_MCP_CAPABILITY = re.compile(
    r"^mcp:(?P<server>[a-z0-9][a-z0-9-]*):(?P<tool>[A-Za-z0-9][A-Za-z0-9_.-]*)$"
)
_CANONICAL_CAPABILITIES = frozenset(
    {
        "filesystem:glob",
        "filesystem:grep",
        "filesystem:read",
        "filesystem:write",
        "shell:execute",
        "web:fetch",
        "web:search",
    }
)


class AgentProvider(StrEnum):
    """Provider identities with explicit native agent contracts."""

    CLAUDE = "claude"
    CODEX = "codex"
    CURSOR = "cursor"
    COPILOT = "copilot"
    GEMINI = "gemini"
    OPENCODE = "opencode"
    ANTIGRAVITY = "antigravity"


class AgentContext(StrEnum):
    """Supported projection contexts."""

    PERSONAL = "personal"
    PROJECT = "project"


class AgentAdapterStatus(StrEnum):
    """Typed adapter outcome; unsupported never means skipped."""

    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class AgentProfile:
    """One validated, provider-neutral agent profile."""

    path: Path
    name: str
    description: str
    distribution: str
    tags: tuple[str, ...]
    rule_paths: tuple[str, ...]
    tools: tuple[str, ...]
    activation: str
    mode: str
    role: str
    detectors: tuple[str, ...]
    instructions: str


@dataclass(frozen=True)
class AgentArtifact:
    """One complete provider-native agent projection."""

    provider: AgentProvider
    context: AgentContext
    name: str
    destination: PurePosixPath
    content: str
    status: AgentAdapterStatus = field(default=AgentAdapterStatus.SUPPORTED, init=False)

    def __post_init__(self) -> None:
        if (
            self.destination.is_absolute()
            or ".." in self.destination.parts
            or self.destination.name in {"", ".", ".."}
        ):
            raise ValueError("agent destination must be a relative physical path")
        if not self.content.strip():
            raise ValueError("agent artifact content must be non-empty")


@dataclass(frozen=True)
class UnsupportedAgent:
    """An explicit provider/context incompatibility."""

    provider: AgentProvider
    context: AgentContext
    name: str
    reason: str
    status: AgentAdapterStatus = field(
        default=AgentAdapterStatus.UNSUPPORTED, init=False
    )

    def __post_init__(self) -> None:
        if not self.reason.startswith("UNSUPPORTED: "):
            raise ValueError("unsupported agent reason must be explicit")


type AgentRender = AgentArtifact | UnsupportedAgent


class AgentRenderError(ValueError):
    """A supported adapter refused a lossy or unsafe projection."""


@dataclass(frozen=True)
class AgentProfileFinding:
    """One blocking agent-profile contract violation."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class AgentProfileAudit:
    """Validated profiles and every blocking finding discovered together."""

    profiles: tuple[AgentProfile, ...]
    findings: tuple[AgentProfileFinding, ...]


def _frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise ValueError("unterminated YAML frontmatter")
    loaded = yaml.safe_load(text[4:marker])
    if not isinstance(loaded, dict):
        raise TypeError("frontmatter must be a mapping")
    raw = cast(dict[object, object], loaded)
    if not all(isinstance(key, str) for key in raw):
        raise TypeError("frontmatter keys must be strings")
    metadata = cast(dict[str, object], raw)
    unknown = sorted(set(metadata) - _TOP_LEVEL_FIELDS)
    if unknown:
        raise ValueError(f"unknown agent frontmatter fields: {', '.join(unknown)}")
    return metadata, text[marker + 5 :]


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _finding(path: str, code: str, message: str) -> AgentProfileFinding:
    return AgentProfileFinding(path, code, message)


def _tag_values(metadata: dict[str, object]) -> tuple[str, ...]:
    container = metadata.get("metadata")
    if not isinstance(container, dict):
        raise TypeError("metadata must be a mapping")
    raw = container.get("aihub.tags")
    if not isinstance(raw, str):
        raise TypeError("metadata.aihub.tags must be a JSON string")
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("metadata.aihub.tags must contain valid JSON") from error
    if not isinstance(loaded, list) or not all(
        isinstance(item, str) and item and not any(char.isspace() for char in item)
        for item in loaded
    ):
        raise TypeError("metadata.aihub.tags must be a JSON array of non-empty tags")
    return tuple(loaded)


def _one_tag(tags: tuple[str, ...], prefix: str) -> tuple[str, ...]:
    return tuple(tag for tag in tags if tag.startswith(prefix))


def _tag_findings(
    relative: str, distribution: str, tags: tuple[str, ...]
) -> list[AgentProfileFinding]:
    findings: list[AgentProfileFinding] = []
    if len(tags) != len(set(tags)):
        findings.append(_finding(relative, "agent-profile-tags", "tags must be unique"))
    if tags != tuple(sorted(tags)):
        findings.append(_finding(relative, "agent-profile-tags", "tags must be sorted"))

    activations = _one_tag(tags, "activation:")
    modes = _one_tag(tags, "mode:")
    roles = _one_tag(tags, "role:")
    detectors = _one_tag(tags, "detect:")
    if len(activations) != 1 or activations[0] not in _ACTIVATIONS:
        findings.append(
            _finding(
                relative,
                "agent-profile-activation",
                "exactly one supported activation tag is required",
            )
        )
    if len(modes) != 1 or modes[0] not in _MODES:
        findings.append(
            _finding(
                relative,
                "agent-profile-mode",
                "exactly one supported mode tag is required",
            )
        )
    if len(roles) != 1 or roles[0] == "role:":
        findings.append(
            _finding(
                relative,
                "agent-profile-role",
                "exactly one non-empty role tag is required",
            )
        )
    activation = activations[0] if len(activations) == 1 else None
    if distribution == "agent-wide" and activation != "activation:always":
        findings.append(
            _finding(
                relative,
                "agent-profile-distribution",
                "agent-wide profiles require activation:always",
            )
        )
    if distribution == "project-wide" and activation == "activation:always":
        findings.append(
            _finding(
                relative,
                "agent-profile-distribution",
                "project-wide profiles cannot use activation:always",
            )
        )
    if activation == "activation:detected" and not detectors:
        findings.append(
            _finding(
                relative,
                "agent-profile-detector",
                "detected profiles require at least one detect tag",
            )
        )
    if activation != "activation:detected" and detectors:
        findings.append(
            _finding(
                relative,
                "agent-profile-detector",
                "detect tags are allowed only with activation:detected",
            )
        )
    for detector in detectors:
        parts = detector.split(":", 2)
        if (
            len(parts) != 3
            or parts[1] not in {"dependency", "extension", "marker"}
            or not parts[2]
        ):
            findings.append(
                _finding(
                    relative,
                    "agent-profile-detector",
                    f"unsupported detector tag: {detector}",
                )
            )
            continue
        value = parts[2]
        if parts[1] == "marker":
            marker = PurePosixPath(value)
            if (
                marker.is_absolute()
                or marker == PurePosixPath(".")
                or ".." in marker.parts
            ):
                findings.append(
                    _finding(
                        relative,
                        "agent-profile-detector",
                        f"detector marker must remain inside a project: {detector}",
                    )
                )
        elif "/" in value or "\\" in value or any(char.isspace() for char in value):
            findings.append(
                _finding(
                    relative,
                    "agent-profile-detector",
                    f"invalid detector value: {detector}",
                )
            )
    return findings


def _tools(raw: object) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, str):
        values = tuple(part.strip() for part in raw.split(","))
    elif isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        values = tuple(cast(list[str], raw))
    else:
        raise TypeError("tools must be a comma-delimited string or an array of strings")
    if (
        not values
        or any(value != value.strip() or not _TOOL.fullmatch(value) for value in values)
        or len(values) != len(set(values))
    ):
        raise ValueError("tools must contain unique provider-neutral capability names")
    unsupported = tuple(
        value
        for value in values
        if value not in _CANONICAL_CAPABILITIES
        and _MCP_CAPABILITY.fullmatch(value) is None
    )
    if unsupported:
        raise ValueError(
            "unsupported provider-neutral capabilities: " + ", ".join(unsupported)
        )
    return values


def _candidate_paths(
    root: Path, agents: Path
) -> tuple[list[Path], list[AgentProfileFinding]]:
    candidates: list[Path] = []
    findings: list[AgentProfileFinding] = []
    for path in sorted(agents.rglob("*")):
        relative = _relative(root, path)
        parts = path.relative_to(agents).parts
        if len(parts) == 1:
            if path.name in _RETIRED_SURFACES:
                findings.append(
                    _finding(
                        relative,
                        "agent-profile-retired-surface",
                        "retired manifest/dispatcher surface is forbidden",
                    )
                )
            elif path.is_symlink():
                findings.append(
                    _finding(
                        relative, "agent-profile-symlink", "agent path is a symlink"
                    )
                )
            elif not path.is_dir() or path.name not in _DISTRIBUTIONS:
                findings.append(
                    _finding(
                        relative,
                        "agent-profile-path",
                        "profiles must use agents/{agent-wide,project-wide}/<slug>.md",
                    )
                )
            continue

        if parts[0] not in _DISTRIBUTIONS:
            continue
        if len(parts) != 2 or path.suffix != ".md":
            findings.append(
                _finding(
                    relative,
                    "agent-profile-path",
                    "profiles must use agents/{agent-wide,project-wide}/<slug>.md",
                )
            )
            continue
        if path.is_symlink():
            findings.append(
                _finding(
                    relative,
                    "agent-profile-symlink",
                    "agent profile must be a physical regular file",
                )
            )
        elif not path.is_file():
            findings.append(
                _finding(
                    relative,
                    "agent-profile-regular-file",
                    "agent profile must be a regular file",
                )
            )
        else:
            candidates.append(path)
    return candidates, findings


def audit_agent_profiles(root: Path) -> AgentProfileAudit:
    """Discover strict recursive profiles and reject ambiguous metadata."""

    agents = root / "agents"
    if not agents.exists() and not agents.is_symlink():
        return AgentProfileAudit((), ())
    if agents.is_symlink():
        return AgentProfileAudit(
            (),
            (
                _finding(
                    "agents", "agent-profile-symlink", "agent directory is a symlink"
                ),
            ),
        )
    if not agents.is_dir():
        return AgentProfileAudit(
            (),
            (
                _finding(
                    "agents",
                    "agent-profile-directory",
                    "agent profile root must be a directory",
                ),
            ),
        )

    candidates, findings = _candidate_paths(root, agents)
    pending: list[AgentProfile] = []
    for path in candidates:
        relative = _relative(root, path)
        try:
            source = path.read_text(encoding="utf-8")
            metadata, instructions = _frontmatter(source)
        except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
            findings.append(
                _finding(
                    relative, "agent-profile-frontmatter", str(error).splitlines()[0]
                )
            )
            continue

        profile_findings: list[AgentProfileFinding] = []
        name = metadata.get("name")
        profile_name = name if isinstance(name, str) and name == path.stem else None
        if profile_name is None:
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-name",
                    f"frontmatter name must equal filename {path.stem!r}",
                )
            )
        description = metadata.get("description")
        profile_description = (
            description.strip()
            if isinstance(description, str) and description.strip()
            else None
        )
        if profile_description is None:
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-description",
                    "description must be a non-empty string",
                )
            )
        portable_surface = f"{profile_description or ''}\n{instructions}"
        if path.parent.name == "project-wide" and NON_PORTABLE_PROJECT_REFERENCE.search(
            portable_surface
        ):
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-non-generic",
                    "project-wide profile contains a private, provider-local, "
                    "or cross-repository contract",
                )
            )
        if "model" in metadata:
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-model",
                    "provider-neutral agent profiles must not declare model",
                )
            )
        try:
            tools = _tools(metadata.get("tools"))
        except (TypeError, ValueError) as error:
            profile_findings.append(
                _finding(relative, "agent-profile-tools", str(error))
            )
            tools = ()
        if _INLINE_PROMPT_DEFENSE in instructions:
            profile_findings.append(
                _finding(
                    relative,
                    "agent-profile-inline-rule",
                    f"prompt defense must be composed from {_PROMPT_DEFENSE_RULE}",
                )
            )
        try:
            tags = _tag_values(metadata)
        except (TypeError, ValueError) as error:
            profile_findings.append(
                _finding(relative, "agent-profile-tags", str(error))
            )
            tags = ()
        else:
            profile_findings.extend(_tag_findings(relative, path.parent.name, tags))
        findings.extend(profile_findings)
        if profile_findings:
            continue
        assert profile_name is not None
        assert profile_description is not None
        activation = _one_tag(tags, "activation:")[0].removeprefix("activation:")
        mode = _one_tag(tags, "mode:")[0].removeprefix("mode:")
        role = _one_tag(tags, "role:")[0].removeprefix("role:")
        pending.append(
            AgentProfile(
                path=path,
                name=profile_name,
                description=profile_description,
                distribution=path.parent.name,
                tags=tags,
                rule_paths=(_PROMPT_DEFENSE_RULE,),
                tools=tools,
                activation=activation,
                mode=mode,
                role=role,
                detectors=_one_tag(tags, "detect:"),
                instructions=instructions,
            )
        )

    by_name: dict[str, list[AgentProfile]] = {}
    for profile in pending:
        by_name.setdefault(profile.name, []).append(profile)
    ambiguous = {name for name, profiles in by_name.items() if len(profiles) > 1}
    for name in sorted(ambiguous):
        for profile in by_name[name]:
            findings.append(
                _finding(
                    _relative(root, profile.path),
                    "agent-profile-ambiguous",
                    f"profile name {name!r} exists in more than one distribution",
                )
            )

    profiles = tuple(profile for profile in pending if profile.name not in ambiguous)
    if profiles:
        rule = root / _PROMPT_DEFENSE_RULE
        if rule.is_symlink() or not rule.is_file():
            findings.append(
                _finding(
                    _PROMPT_DEFENSE_RULE,
                    "agent-profile-rule-owner",
                    "prompt-defense rule owner must be a physical regular file",
                )
            )
            profiles = ()
    return AgentProfileAudit(
        profiles, tuple(sorted(findings, key=lambda item: (item.path, item.code)))
    )


def _render_frontmatter(metadata: dict[str, object], body: str) -> str:
    dumped = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).removesuffix("\n")
    return f"---\n{dumped}\n---\n\n{body}"


def _body(profile: AgentProfile, prompt_defense: str) -> str:
    if not prompt_defense.strip():
        raise AgentRenderError("prompt-defense composition source is empty")
    return f"{prompt_defense.rstrip()}\n\n{profile.instructions.lstrip()}"


def _unsupported(
    profile: AgentProfile,
    provider: AgentProvider,
    context: AgentContext,
    reason: str,
) -> UnsupportedAgent:
    return UnsupportedAgent(
        provider=provider,
        context=context,
        name=profile.name,
        reason=f"UNSUPPORTED: {reason}",
    )


_CLAUDE_TOOLS = {
    "filesystem:glob": ("Glob",),
    "filesystem:grep": ("Grep",),
    "filesystem:read": ("Read",),
    "filesystem:write": ("Edit", "Write"),
    "shell:execute": ("Bash",),
    "web:fetch": ("WebFetch",),
    "web:search": ("WebSearch",),
}
_COPILOT_TOOLS = {
    "filesystem:glob": ("search",),
    "filesystem:grep": ("search",),
    "filesystem:read": ("read",),
    "filesystem:write": ("edit",),
    "shell:execute": ("execute",),
    "web:fetch": ("web",),
    "web:search": ("web",),
}
_GEMINI_TOOLS = {
    "filesystem:glob": ("glob",),
    "filesystem:grep": ("grep_search",),
    "filesystem:read": ("read_file",),
    "filesystem:write": ("replace", "write_file"),
    "shell:execute": ("run_shell_command",),
    "web:fetch": ("web_fetch",),
    "web:search": ("google_web_search",),
}
_OPENCODE_TOOLS = {
    "filesystem:glob": ("glob",),
    "filesystem:grep": ("grep",),
    "filesystem:read": ("read",),
    "filesystem:write": ("edit",),
    "shell:execute": ("bash",),
    "web:fetch": ("webfetch",),
    "web:search": ("websearch",),
}
_ANTIGRAVITY_TOOLS = {
    "filesystem:glob": ("find_by_name",),
    "filesystem:grep": ("grep_search",),
    "filesystem:read": ("view_file",),
    "filesystem:write": ("replace_file_content", "write_to_file"),
    "shell:execute": ("run_command",),
    "web:fetch": ("read_url_content",),
    "web:search": ("search_web",),
}


def _mapped_tools(
    profile: AgentProfile,
    provider: AgentProvider,
    context: AgentContext,
    mapping: Mapping[str, tuple[str, ...]],
    *,
    mcp_style: str | None,
) -> tuple[str, ...] | UnsupportedAgent:
    rendered: list[str] = []
    for capability in profile.tools:
        native = mapping.get(capability)
        if native is not None:
            rendered.extend(native)
            continue
        mcp = _MCP_CAPABILITY.fullmatch(capability)
        if mcp is None:
            return _unsupported(
                profile,
                provider,
                context,
                f"{provider.value} cannot preserve canonical capability: {capability}",
            )
        if mcp_style is None:
            return _unsupported(
                profile,
                provider,
                context,
                f"{provider.value} MCP tool identity is not documented for agent "
                "allowlists",
            )
        rendered.append(mcp_style.format(server=mcp["server"], tool=mcp["tool"]))
    return tuple(dict.fromkeys(rendered))


def render_agent(
    profile: AgentProfile,
    provider: AgentProvider | str,
    context: AgentContext | str,
    *,
    prompt_defense: str,
) -> AgentRender:
    """Render one profile without emitting a model or weakening capabilities."""

    try:
        selected_provider = AgentProvider(provider)
    except ValueError as error:
        raise ValueError(f"unknown agent provider: {provider}") from error
    try:
        selected_context = AgentContext(context)
    except ValueError as error:
        raise ValueError(f"unknown agent context: {context}") from error

    if selected_provider is AgentProvider.CURSOR:
        return _unsupported(
            profile,
            selected_provider,
            selected_context,
            "Cursor custom agents have no documented capability allowlist",
        )
    if selected_provider is AgentProvider.CODEX:
        return _unsupported(
            profile,
            selected_provider,
            selected_context,
            "Codex custom agents have no documented capability allowlist",
        )

    body = _body(profile, prompt_defense)
    if selected_provider is AgentProvider.CLAUDE:
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _CLAUDE_TOOLS,
            mcp_style="mcp__{server}__{tool}",
        )
        if isinstance(mapped, UnsupportedAgent):
            return mapped
        metadata: dict[str, object] = {
            "name": profile.name,
            "description": profile.description,
        }
        if mapped:
            metadata["tools"] = list(mapped)
        destination = PurePosixPath(".claude", "agents", f"{profile.name}.md")
    elif selected_provider is AgentProvider.COPILOT:
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _COPILOT_TOOLS,
            mcp_style="{server}/{tool}",
        )
        if isinstance(mapped, UnsupportedAgent):
            return mapped
        metadata = {
            "name": profile.name,
            "description": profile.description,
            "tools": list(mapped),
        }
        destination = (
            PurePosixPath(".copilot", "agents", f"{profile.name}.md")
            if selected_context is AgentContext.PERSONAL
            else PurePosixPath(".github", "agents", f"{profile.name}.md")
        )
    elif selected_provider is AgentProvider.GEMINI:
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _GEMINI_TOOLS,
            mcp_style="mcp_{server}_{tool}",
        )
        if isinstance(mapped, UnsupportedAgent):
            return mapped
        metadata = {
            "name": profile.name,
            "description": profile.description,
            "kind": "local",
            "tools": list(mapped),
        }
        destination = PurePosixPath(".gemini", "agents", f"{profile.name}.md")
    elif selected_provider is AgentProvider.OPENCODE:
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _OPENCODE_TOOLS,
            mcp_style="{server}_{tool}",
        )
        if isinstance(mapped, UnsupportedAgent):
            return mapped
        permissions = {"*": "deny"}
        permissions.update(dict.fromkeys(mapped, "allow"))
        metadata = {
            "description": profile.description,
            "mode": "subagent",
            "permission": permissions,
        }
        destination = (
            PurePosixPath(".config", "opencode", "agents", f"{profile.name}.md")
            if selected_context is AgentContext.PERSONAL
            else PurePosixPath(".opencode", "agents", f"{profile.name}.md")
        )
    else:
        assert selected_provider is AgentProvider.ANTIGRAVITY
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _ANTIGRAVITY_TOOLS,
            mcp_style=None,
        )
        if isinstance(mapped, UnsupportedAgent):
            return mapped
        metadata = {
            "name": profile.name,
            "description": profile.description,
            "tools": list(mapped),
        }
        if selected_context is AgentContext.PERSONAL:
            destination = PurePosixPath(
                ".gemini", "config", "agents", profile.name, "agent.md"
            )
        else:
            destination = PurePosixPath(".agents", "agents", profile.name, "agent.md")
    return AgentArtifact(
        provider=selected_provider,
        context=selected_context,
        name=profile.name,
        destination=destination,
        content=_render_frontmatter(metadata, body),
    )


__all__ = (
    "AgentAdapterStatus",
    "AgentArtifact",
    "AgentContext",
    "AgentProfile",
    "AgentProfileAudit",
    "AgentProfileFinding",
    "AgentProvider",
    "AgentRender",
    "AgentRenderError",
    "UnsupportedAgent",
    "audit_agent_profiles",
    "render_agent",
)
