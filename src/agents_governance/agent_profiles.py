"""Strict provider-neutral agent-profile discovery and rendering."""

from __future__ import annotations

import json
import re
import stat
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Never, cast

import yaml

from .catalog import NON_PORTABLE_PROJECT_REFERENCE
from .frontmatter import parse_frontmatter

_DISTRIBUTIONS = frozenset({"agent-wide", "project-wide"})
_ACTIVATIONS = frozenset(
    {"activation:always", "activation:detected", "activation:opt-in"}
)
_MODES = frozenset(
    {"mode:debug", "mode:execute", "mode:operate", "mode:plan", "mode:review"}
)
_PROMPT_DEFENSE_RULE = "rules/security/prompt-defense.md"
_INLINE_PROMPT_DEFENSE = "## Prompt Defense Baseline"
_TOP_LEVEL_FIELDS = frozenset({"name", "description", "tools", "metadata", "model"})
_TOOL = re.compile(r"[A-Za-z0-9_.:-]+\Z")
_MCP_CAPABILITY = re.compile(
    r"mcp:(?P<server>[a-z0-9][a-z0-9-]*):(?P<tool>[A-Za-z0-9][A-Za-z0-9_.-]*)\Z"
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
    CLAUDE = "claude"
    CODEX = "codex"
    CURSOR = "cursor"
    COPILOT = "copilot"
    GEMINI = "gemini"
    OPENCODE = "opencode"
    ANTIGRAVITY = "antigravity"
    POOL = "pool"


class AgentContext(StrEnum):
    PERSONAL = "personal"
    PROJECT = "project"


@dataclass(frozen=True)
class AgentProfile:
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
    provider: AgentProvider
    context: AgentContext
    name: str
    destination: PurePosixPath
    content: str

    def __post_init__(self) -> None:
        if self.destination.is_absolute() or any(
            part in {"", ".", ".."} for part in self.destination.parts
        ):
            raise ValueError("agent destination must be a relative physical path")
        if not self.content.strip():
            raise ValueError("agent artifact content must be non-empty")


class AgentRenderError(ValueError):
    """The selected provider cannot preserve the complete agent contract."""


def _frontmatter(path: Path) -> tuple[dict[str, object], str]:
    metadata, instructions = parse_frontmatter(path)
    unknown = frozenset(metadata) - _TOP_LEVEL_FIELDS
    if unknown:
        raise ValueError(f"{path}: unknown agent fields: {', '.join(sorted(unknown))}")
    return metadata, instructions


def _tag_values(path: Path, metadata: dict[str, object]) -> tuple[str, ...]:
    if "metadata" not in metadata:
        raise ValueError(f"{path}: metadata is required")
    container = metadata["metadata"]
    if not isinstance(container, dict) or frozenset(container) != {"aihub.tags"}:
        raise ValueError(f"{path}: metadata fields must equal aihub.tags")
    raw = cast(dict[str, object], container)["aihub.tags"]
    if not isinstance(raw, str):
        raise TypeError(f"{path}: metadata.aihub.tags must be a JSON string")
    loaded = json.loads(raw)
    if not isinstance(loaded, list) or not all(
        isinstance(item, str) and item and not any(char.isspace() for char in item)
        for item in loaded
    ):
        raise TypeError(f"{path}: agent tags must encode non-empty strings")
    tags = tuple(cast(list[str], loaded))
    if len(tags) != len(set(tags)):
        raise ValueError(f"{path}: agent tags must be unique")
    if tags != tuple(sorted(tags)):
        raise ValueError(f"{path}: agent tags must be sorted")
    return tags


def _one_tag(
    path: Path,
    tags: tuple[str, ...],
    prefix: str,
    allowed: frozenset[str] | None = None,
) -> str:
    selected = tuple(tag for tag in tags if tag.startswith(prefix))
    if len(selected) != 1:
        raise ValueError(f"{path}: exactly one {prefix} tag is required")
    if allowed is not None and selected[0] not in allowed:
        raise ValueError(f"{path}: unsupported tag: {selected[0]}")
    if selected[0] == prefix:
        raise ValueError(f"{path}: empty {prefix} tag is forbidden")
    return selected[0]


def _validate_detector(path: Path, detector: str) -> None:
    parts = detector.split(":", 2)
    if (
        len(parts) != 3
        or parts[1] not in {"dependency", "extension", "marker"}
        or not parts[2]
    ):
        raise ValueError(f"{path}: unsupported detector tag: {detector}")
    value = parts[2]
    if parts[1] == "marker":
        marker = PurePosixPath(value)
        if marker.is_absolute() or marker == PurePosixPath(".") or ".." in marker.parts:
            raise ValueError(f"{path}: detector marker escapes project: {detector}")
    elif "/" in value or "\\" in value or any(char.isspace() for char in value):
        raise ValueError(f"{path}: invalid detector value: {detector}")


def _validate_tags(
    path: Path, distribution: str, tags: tuple[str, ...]
) -> tuple[str, str, str, tuple[str, ...]]:
    activation_tag = _one_tag(path, tags, "activation:", _ACTIVATIONS)
    mode_tag = _one_tag(path, tags, "mode:", _MODES)
    role_tag = _one_tag(path, tags, "role:")
    detectors = tuple(tag for tag in tags if tag.startswith("detect:"))
    if distribution == "agent-wide" and activation_tag != "activation:always":
        raise ValueError(f"{path}: agent-wide profiles require activation:always")
    if distribution == "project-wide" and activation_tag == "activation:always":
        raise ValueError(f"{path}: project-wide profiles forbid activation:always")
    if activation_tag == "activation:detected" and not detectors:
        raise ValueError(f"{path}: detected profiles require a detector")
    if activation_tag != "activation:detected" and detectors:
        raise ValueError(f"{path}: detectors require activation:detected")
    for detector in detectors:
        _validate_detector(path, detector)
    known = {activation_tag, mode_tag, role_tag, *detectors}
    if set(tags) != known:
        raise ValueError(f"{path}: unsupported agent tag")
    return (
        activation_tag.removeprefix("activation:"),
        mode_tag.removeprefix("mode:"),
        role_tag.removeprefix("role:"),
        detectors,
    )


def _tools(path: Path, raw: object) -> tuple[str, ...]:
    if raw is None:
        return ()
    if isinstance(raw, str):
        values = tuple(part.strip() for part in raw.split(","))
    elif isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        values = tuple(cast(list[str], raw))
    else:
        raise TypeError(f"{path}: tools must be a string or string array")
    if not values or any(
        value != value.strip() or _TOOL.fullmatch(value) is None for value in values
    ):
        raise ValueError(f"{path}: tools must be provider-neutral capability names")
    if len(values) != len(set(values)):
        raise ValueError(f"{path}: tools must be unique")
    for value in values:
        if (
            value not in _CANONICAL_CAPABILITIES
            and _MCP_CAPABILITY.fullmatch(value) is None
        ):
            raise ValueError(
                f"{path}: unsupported provider-neutral capability: {value}"
            )
    return values


def _candidate_paths(agents: Path) -> tuple[Path, ...]:
    entries = tuple(sorted(agents.iterdir(), key=lambda path: path.name))
    if {entry.name for entry in entries} != _DISTRIBUTIONS:
        raise ValueError("agents root must contain exactly agent-wide and project-wide")
    candidates: list[Path] = []
    for distribution in entries:
        if distribution.is_symlink() or not distribution.is_dir():
            raise ValueError(f"agent distribution must be physical: {distribution}")
        for path in sorted(distribution.iterdir(), key=lambda item: item.name):
            metadata = path.lstat()
            if (
                path.is_symlink()
                or not stat.S_ISREG(metadata.st_mode)
                or path.suffix != ".md"
            ):
                raise ValueError(
                    f"agent profile must be a flat physical Markdown file: {path}"
                )
            candidates.append(path)
    if not candidates:
        raise ValueError(f"agent profile inventory is empty: {agents}")
    return tuple(candidates)


def audit_agent_profiles(root: Path) -> tuple[AgentProfile, ...]:
    """Return every agent profile or raise on the first contract defect."""

    repository = root.resolve(strict=True)
    agents = repository / "agents"
    if agents.is_symlink() or not agents.is_dir():
        raise ValueError(f"agents root must be a physical directory: {agents}")
    rule = repository / _PROMPT_DEFENSE_RULE
    if rule.is_symlink() or not rule.is_file():
        raise ValueError(f"prompt-defense owner must be a physical file: {rule}")
    profiles: list[AgentProfile] = []
    names: set[str] = set()
    for path in _candidate_paths(agents):
        metadata, instructions = _frontmatter(path)
        if "name" not in metadata:
            raise ValueError(f"{path}: name is required")
        name = metadata["name"]
        if not isinstance(name, str) or name != path.stem:
            raise ValueError(f"{path}: name must equal filename {path.stem!r}")
        if name in names:
            raise ValueError(f"{path}: duplicate agent profile name: {name}")
        names.add(name)
        if "description" not in metadata:
            raise ValueError(f"{path}: description is required")
        description = metadata["description"]
        if (
            not isinstance(description, str)
            or not description
            or description != description.strip()
        ):
            raise ValueError(f"{path}: description must be non-empty and trimmed")
        if "model" in metadata:
            raise ValueError(f"{path}: provider-neutral agents must not declare model")
        distribution = path.parent.name
        if distribution == "project-wide" and NON_PORTABLE_PROJECT_REFERENCE.search(
            f"{description}\n{instructions}"
        ):
            raise ValueError(f"{path}: project-wide profile is not portable")
        if _INLINE_PROMPT_DEFENSE in instructions:
            raise ValueError(f"{path}: prompt defense must be composed from its owner")
        tags = _tag_values(path, metadata)
        activation, mode, role, detectors = _validate_tags(path, distribution, tags)
        raw_tools: object = None
        if "tools" in metadata:
            raw_tools = metadata["tools"]
        tools = _tools(path, raw_tools)
        profiles.append(
            AgentProfile(
                path,
                name,
                description,
                distribution,
                tags,
                (_PROMPT_DEFENSE_RULE,),
                tools,
                activation,
                mode,
                role,
                detectors,
                instructions,
            )
        )
    return tuple(profiles)


def _render_frontmatter(metadata: dict[str, object], body: str) -> str:
    dumped = yaml.safe_dump(
        metadata, allow_unicode=True, default_flow_style=False, sort_keys=False
    ).removesuffix("\n")
    return f"---\n{dumped}\n---\n\n{body}"


def _body(profile: AgentProfile, prompt_defense: str) -> str:
    if prompt_defense.lstrip().startswith("---"):
        raise AgentRenderError(
            "prompt-defense composition source must be body text, not frontmatter"
        )
    if not prompt_defense.strip():
        raise AgentRenderError("prompt-defense composition source is empty")
    return f"{prompt_defense.rstrip()}\n\n{profile.instructions.lstrip()}"


def _unsupported(
    profile: AgentProfile, provider: AgentProvider, context: AgentContext, reason: str
) -> Never:
    raise AgentRenderError(
        f"UNSUPPORTED: {provider.value}/{context.value}/{profile.name}: {reason}"
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
_COPILOT_TOOLS = {
    "filesystem:glob": ("search",),
    "filesystem:grep": ("search",),
    "filesystem:read": ("read",),
    "filesystem:write": ("edit",),
    "shell:execute": ("execute",),
    "web:fetch": ("web",),
    "web:search": ("web",),
}


def _mapped_tools(
    profile: AgentProfile,
    provider: AgentProvider,
    context: AgentContext,
    mapping: Mapping[str, tuple[str, ...]],
    mcp_style: str,
) -> tuple[str, ...]:
    rendered: list[str] = []
    for capability in profile.tools:
        if capability in mapping:
            rendered.extend(mapping[capability])
        else:
            mcp = _MCP_CAPABILITY.fullmatch(capability)
            if mcp is None:
                _unsupported(
                    profile, provider, context, f"unmapped capability {capability}"
                )
            rendered.append(mcp_style.format(server=mcp["server"], tool=mcp["tool"]))
    return tuple(dict.fromkeys(rendered))


def render_agent(
    profile: AgentProfile,
    provider: AgentProvider | str,
    context: AgentContext | str,
    *,
    prompt_defense: str,
) -> AgentArtifact:
    """Render one complete supported agent or raise immediately."""

    selected_provider = AgentProvider(provider)
    selected_context = AgentContext(context)
    if selected_provider in {
        AgentProvider.CURSOR,
        AgentProvider.CODEX,
        AgentProvider.ANTIGRAVITY,
        AgentProvider.POOL,
    }:
        _unsupported(
            profile,
            selected_provider,
            selected_context,
            "complete capability allowlist is not proven",
        )
    body = _body(profile, prompt_defense)
    if selected_provider is AgentProvider.CLAUDE:
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _CLAUDE_TOOLS,
            "mcp__{server}__{tool}",
        )
        metadata: dict[str, object] = {
            "name": profile.name,
            "description": profile.description,
        }
        metadata["tools"] = list(mapped)
        destination = PurePosixPath(".claude", "agents", f"{profile.name}.md")
    elif selected_provider is AgentProvider.COPILOT:
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _COPILOT_TOOLS,
            "{server}/{tool}",
        )
        metadata = {
            "name": profile.name,
            "description": profile.description,
            "target": "github-copilot",
            "tools": list(mapped),
        }
        destination = (
            PurePosixPath(".copilot", "agents", f"{profile.name}.agent.md")
            if selected_context is AgentContext.PERSONAL
            else PurePosixPath(".github", "agents", f"{profile.name}.agent.md")
        )
    elif selected_provider is AgentProvider.GEMINI:
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _GEMINI_TOOLS,
            "mcp_{server}_{tool}",
        )
        metadata = {
            "name": profile.name,
            "description": profile.description,
            "kind": "local",
            "tools": list(mapped),
        }
        destination = PurePosixPath(".gemini", "agents", f"{profile.name}.md")
    else:
        mapped = _mapped_tools(
            profile,
            selected_provider,
            selected_context,
            _OPENCODE_TOOLS,
            "{server}_{tool}",
        )
        permissions = {"*": "deny", **dict.fromkeys(mapped, "allow")}
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
    return AgentArtifact(
        selected_provider,
        selected_context,
        profile.name,
        destination,
        _render_frontmatter(metadata, body),
    )


__all__ = (
    "AgentArtifact",
    "AgentContext",
    "AgentProfile",
    "AgentProvider",
    "AgentRenderError",
    "audit_agent_profiles",
    "render_agent",
)
