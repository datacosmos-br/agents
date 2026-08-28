"""Provider-native, item-scoped rendering of canonical engineering rules."""

from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from typing import Never

import yaml

from .rules import RuleActivation, RuleSpec

_ALL_PATHS_GLOB = "**"
_MARKDOWN_LINK = re.compile(r"(!?)\[([^\]\n]+)\]\(([^)\n]+)\)")


class RuleProvider(StrEnum):
    """Providers with an explicitly classified rule-instruction surface."""

    CLAUDE = "claude"
    CURSOR = "cursor"
    COPILOT = "copilot"
    ANTIGRAVITY = "antigravity"
    GEMINI = "gemini"
    OPENCODE = "opencode"
    CODEX = "codex"


class RuleContext(StrEnum):
    """Supported projection contexts."""

    PERSONAL = "personal"
    PROJECT = "project"


@dataclass(frozen=True)
class RuleArtifact:
    """One complete provider-native physical rule artifact."""

    provider: RuleProvider
    context: RuleContext
    identity: str
    destination: PurePosixPath
    content: str

    def __post_init__(self) -> None:
        if self.destination.is_absolute() or any(
            part in {"", ".", ".."} for part in self.destination.parts
        ):
            raise ValueError(
                "rule artifact destination must be a relative physical path"
            )
        if not self.content.strip():
            raise ValueError("rule artifact content must be non-empty")


class RuleRenderError(ValueError):
    """A supported adapter refused a lossy or invalid rule rendering."""


def _frontmatter(metadata: dict[str, object], body: str) -> str:
    dumped = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).removesuffix("\n")
    return f"---\n{dumped}\n---\n\n{body}"


def _artifact(
    spec: RuleSpec,
    provider: RuleProvider,
    context: RuleContext,
    destination: PurePosixPath,
    content: str,
) -> RuleArtifact:
    return RuleArtifact(provider, context, spec.identity, destination, content)


def _physical_name(spec: RuleSpec, suffix: str) -> str:
    """Encode a recursive canonical identity as one collision-free filename."""

    return f"{spec.identity.replace('/', '--')}{suffix}"


def _render_body(spec: RuleSpec, suffix: str) -> str:
    """Rebase validated local rule links to independent projected siblings."""

    references = set(spec.references)
    if not references:
        return spec.body
    parent = PurePosixPath(spec.identity).parent

    def replace(match: re.Match[str]) -> str:
        raw_target = match.group(3).strip()
        if raw_target.startswith("<"):
            closing = raw_target.find(">", 1)
            target = raw_target[1:closing] if closing > 0 else raw_target
        else:
            target = raw_target.split(maxsplit=1)[0] if raw_target else raw_target
        if (
            not target
            or target.startswith(("#", "/", "~"))
            or ":" in target.split("/", 1)[0]
        ):
            return match.group(0)
        clean = target.split("#", 1)[0].split("?", 1)[0]
        canonical = PurePosixPath(posixpath.normpath((parent / clean).as_posix()))
        reference = f"rules/{canonical.as_posix()}"
        if reference not in references:
            return match.group(0)
        identity = canonical.with_suffix("").as_posix()
        destination = f"{identity.replace('/', '--')}{suffix}"
        return f"{match.group(1)}[{match.group(2)}]({destination})"

    return _MARKDOWN_LINK.sub(replace, spec.body)


def _unsupported(
    spec: RuleSpec,
    provider: RuleProvider,
    context: RuleContext,
    reason: str,
) -> Never:
    raise RuleRenderError(
        f"UNSUPPORTED: {provider.value}/{context.value}/{spec.identity}: {reason}"
    )


def _claude(
    spec: RuleSpec, provider: RuleProvider, context: RuleContext
) -> RuleArtifact:
    destination = PurePosixPath(".claude", "rules", _physical_name(spec, ".md"))
    body = _render_body(spec, ".md")
    content = (
        _frontmatter({"paths": list(spec.globs)}, body)
        if spec.activation is RuleActivation.PATH_SCOPED
        else body
    )
    return _artifact(spec, provider, context, destination, content)


def _cursor(
    spec: RuleSpec, provider: RuleProvider, context: RuleContext
) -> RuleArtifact:
    if context is RuleContext.PERSONAL:
        return _unsupported(
            spec,
            provider,
            context,
            "Cursor personal rules are settings-owned and have no file adapter",
        )
    metadata: dict[str, object] = {
        "description": spec.description or "",
        "globs": list(spec.globs),
        "alwaysApply": spec.activation is RuleActivation.ALWAYS,
    }
    return _artifact(
        spec,
        provider,
        context,
        PurePosixPath(".cursor", "rules", _physical_name(spec, ".mdc")),
        _frontmatter(metadata, _render_body(spec, ".mdc")),
    )


def _copilot(
    spec: RuleSpec, provider: RuleProvider, context: RuleContext
) -> RuleArtifact:
    if any("," in glob for glob in spec.globs):
        raise RuleRenderError(
            f"{provider.value}/{spec.identity}: applyTo cannot preserve a glob "
            "containing the provider's comma delimiter"
        )
    apply_to = ",".join(spec.globs) if spec.globs else _ALL_PATHS_GLOB
    base = (
        PurePosixPath(".copilot", "instructions")
        if context is RuleContext.PERSONAL
        else PurePosixPath(".github", "instructions")
    )
    return _artifact(
        spec,
        provider,
        context,
        base / _physical_name(spec, ".instructions.md"),
        _frontmatter({"applyTo": apply_to}, _render_body(spec, ".instructions.md")),
    )


def render_rule(
    spec: RuleSpec,
    provider: RuleProvider | str,
    context: RuleContext | str,
) -> RuleArtifact:
    """Render one complete native rule or raise immediately."""

    selected_provider = RuleProvider(provider)
    selected_context = RuleContext(context)

    if selected_provider is RuleProvider.CLAUDE:
        return _claude(spec, selected_provider, selected_context)
    if selected_provider is RuleProvider.CURSOR:
        return _cursor(spec, selected_provider, selected_context)
    if selected_provider is RuleProvider.COPILOT:
        return _copilot(spec, selected_provider, selected_context)
    if selected_provider is RuleProvider.ANTIGRAVITY:
        return _unsupported(
            spec,
            selected_provider,
            selected_context,
            "Antigravity has no documented complete physical rule schema",
        )
    if selected_provider is RuleProvider.CODEX:
        return _unsupported(
            spec,
            selected_provider,
            selected_context,
            "Codex .codex/rules is Starlark execution policy, not Markdown "
            "instructions; AGENTS.md needs a whole-file compiler",
        )
    aggregate = "GEMINI.md" if selected_provider is RuleProvider.GEMINI else "AGENTS.md"
    return _unsupported(
        spec,
        selected_provider,
        selected_context,
        f"{selected_provider.value} requires a whole-file {aggregate} compiler",
    )


__all__ = (
    "RuleArtifact",
    "RuleContext",
    "RuleProvider",
    "RuleRenderError",
    "render_rule",
)
