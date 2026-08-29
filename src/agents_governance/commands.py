"""Strict canonical-command validation and provider-native rendering."""

from __future__ import annotations

import json
import re
import stat
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import cast

import yaml
from yaml.nodes import MappingNode, Node, SequenceNode

from .tokens import bpe_content

_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_DESCRIPTION_LIMIT = 160
_TOP_LEVEL_FIELDS = frozenset({"name", "description", "argument-hint", "metadata"})
_METADATA_FIELDS = frozenset({"aihub.tags"})
_ARGUMENTS = "$ARGUMENTS"


class CommandRoute(StrEnum):
    AGENT = "agent"
    PROJECT = "project"


class CommandIntent(StrEnum):
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    INSPECTION = "inspection"
    VERIFICATION = "verification"
    LANDING = "landing"
    GOVERNANCE = "governance"


class CommandRisk(StrEnum):
    READ = "read"
    WRITE = "write"
    EXTERNAL = "external"


class CommandProvider(StrEnum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENCODE = "opencode"
    CURSOR = "cursor"
    COPILOT = "copilot"
    CODEX = "codex"
    ANTIGRAVITY = "antigravity"


@dataclass(frozen=True)
class CommandSpec:
    path: Path
    name: str
    description: str
    argument_hint: str | None
    tags: tuple[str, ...]
    route: CommandRoute
    intents: tuple[CommandIntent, ...]
    risk: CommandRisk
    body: str

    def __post_init__(self) -> None:
        _validate_spec(self)

    @property
    def uses_arguments(self) -> bool:
        return _ARGUMENTS in self.body


@dataclass(frozen=True)
class CommandArtifact:
    provider: CommandProvider
    slug: str
    destination: PurePosixPath
    content: str
    manual_only: bool
    tokens: int
    max_tokens: int | None


class CommandRenderError(ValueError):
    """A provider adapter rejected the requested complete command."""


@dataclass(frozen=True)
class CommandTokenBudget:
    max_tokens: int | None
    counter: Callable[[str], int] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.max_tokens is not None and (
            type(self.max_tokens) is not int or self.max_tokens <= 0
        ):
            raise ValueError("command max_tokens must be a positive integer")
        if not callable(self.counter):
            raise TypeError("command token counter must be callable")

    def measure(self, content: str) -> int:
        measured = self.counter(content)
        if type(measured) is not int or measured < 0:
            raise CommandRenderError(
                "command token counter must return a non-negative integer"
            )
        return measured


def waza_bpe_counter(root: Path) -> Callable[[str], int]:
    """Return the canonical in-memory full-text BPE counter."""

    authority = root.resolve(strict=True)

    def count(content: str) -> int:
        return bpe_content(content, authority)

    return count


def _short_sentence(value: str) -> bool:
    return (
        value == value.strip()
        and 0 < len(value) <= _DESCRIPTION_LIMIT
        and "\n" not in value
        and "\r" not in value
        and value[-1] in ".!?"
        and not any(mark in value[:-1] for mark in ".!?")
    )


def _argument_hint_valid(value: str) -> bool:
    return (
        value == value.strip()
        and bool(value)
        and len(value) <= _DESCRIPTION_LIMIT
        and "\n" not in value
        and "\r" not in value
    )


def _validate_spec(spec: CommandSpec) -> None:
    if _SLUG.fullmatch(spec.name) is None or spec.path.stem != spec.name:
        raise ValueError("command name must equal its lowercase filename slug")
    if not _short_sentence(spec.description):
        raise ValueError("command description must be one short sentence")
    if spec.argument_hint is not None and not _argument_hint_valid(spec.argument_hint):
        raise ValueError("command argument-hint must be one short non-empty line")
    if not spec.body.strip():
        raise ValueError("command body must be non-empty")
    if spec.uses_arguments and spec.argument_hint is None:
        raise ValueError("command argument-hint is required with $ARGUMENTS")
    if not isinstance(spec.route, CommandRoute):
        raise TypeError("command route must be typed")
    if not spec.intents or not all(
        isinstance(intent, CommandIntent) for intent in spec.intents
    ):
        raise TypeError("command intents must contain approved typed values")
    if tuple(sorted(spec.intents, key=lambda item: item.value)) != spec.intents:
        raise ValueError("command intents must be sorted")
    if not isinstance(spec.risk, CommandRisk):
        raise TypeError("command risk must be typed")
    expected = {
        f"route:{spec.route.value}",
        f"risk:{spec.risk.value}",
        *(f"intent:{intent.value}" for intent in spec.intents),
    }
    if len(spec.tags) != len(set(spec.tags)) or tuple(sorted(spec.tags)) != spec.tags:
        raise ValueError("command tags must be unique and sorted")
    if set(spec.tags) != expected:
        raise ValueError(
            "command tags must contain only typed route, intent, and risk values"
        )


def _duplicate_key(node: Node) -> str | None:
    if isinstance(node, MappingNode):
        seen: set[str] = set()
        for key_node, value_node in node.value:
            key = str(getattr(key_node, "value", "<non-scalar>"))
            if key in seen:
                return key
            seen.add(key)
            duplicate = _duplicate_key(value_node)
            if duplicate is not None:
                return duplicate
    elif isinstance(node, SequenceNode):
        for child in node.value:
            duplicate = _duplicate_key(child)
            if duplicate is not None:
                return duplicate
    return None


def _frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
    source = text[4:marker]
    node = yaml.compose(source, Loader=yaml.SafeLoader)
    loaded = yaml.safe_load(source)
    if not isinstance(node, MappingNode) or not isinstance(loaded, dict):
        raise TypeError(f"{path}: frontmatter must be a mapping")
    duplicate = _duplicate_key(node)
    if duplicate is not None:
        raise ValueError(f"{path}: frontmatter key is duplicated: {duplicate}")
    raw = cast(dict[object, object], loaded)
    if not all(isinstance(key, str) for key in raw):
        raise TypeError(f"{path}: frontmatter keys must be strings")
    return cast(dict[str, object], raw), text[marker + 5 :].removeprefix("\n")


def _tags(
    path: Path, raw: object
) -> tuple[tuple[str, ...], CommandRoute, tuple[CommandIntent, ...], CommandRisk]:
    if not isinstance(raw, str):
        raise TypeError(f"{path}: metadata.aihub.tags must be a JSON string")
    decoded = json.loads(raw)
    if not isinstance(decoded, list) or not all(
        isinstance(item, str) for item in decoded
    ):
        raise TypeError(f"{path}: command tags must encode an array of strings")
    tags = tuple(cast(list[str], decoded))
    if len(tags) != len(set(tags)) or tags != tuple(sorted(tags)):
        raise ValueError(f"{path}: command tags must be unique and sorted")
    if any(not tag.startswith(("route:", "intent:", "risk:")) for tag in tags):
        raise ValueError(f"{path}: command tags support only route, intent, and risk")
    route_values = tuple(
        tag.removeprefix("route:") for tag in tags if tag.startswith("route:")
    )
    if len(route_values) != 1:
        raise ValueError(f"{path}: command requires exactly one route")
    route = CommandRoute(route_values[0])
    risk_values = tuple(
        tag.removeprefix("risk:") for tag in tags if tag.startswith("risk:")
    )
    if len(risk_values) != 1:
        raise ValueError(f"{path}: command requires exactly one risk")
    risk = CommandRisk(risk_values[0])
    intent_values = tuple(
        tag.removeprefix("intent:") for tag in tags if tag.startswith("intent:")
    )
    if not intent_values:
        raise ValueError(f"{path}: command requires at least one intent")
    intents = tuple(CommandIntent(value) for value in intent_values)
    return tags, route, intents, risk


def _load_command(path: Path) -> CommandSpec:
    payload, body = _frontmatter(path)
    unknown = frozenset(payload) - _TOP_LEVEL_FIELDS
    if unknown:
        raise ValueError(
            f"{path}: unknown command frontmatter fields: {', '.join(sorted(unknown))}"
        )
    if "name" not in payload:
        raise ValueError(f"{path}: command name is required")
    name = payload["name"]
    if not isinstance(name, str) or name != path.stem or _SLUG.fullmatch(name) is None:
        raise ValueError(f"{path}: command name must equal lowercase filename slug")
    if "description" not in payload:
        raise ValueError(f"{path}: command description is required")
    description = payload["description"]
    if not isinstance(description, str) or not _short_sentence(description):
        raise ValueError(f"{path}: command description must be one short sentence")
    argument_hint: str | None = None
    if "argument-hint" in payload:
        raw_hint = payload["argument-hint"]
        if not isinstance(raw_hint, str) or not _argument_hint_valid(raw_hint):
            raise ValueError(f"{path}: command argument-hint must be one short line")
        argument_hint = raw_hint
    if _ARGUMENTS in body and argument_hint is None:
        raise ValueError(f"{path}: command argument-hint is required with $ARGUMENTS")
    if not body.strip():
        raise ValueError(f"{path}: command body must be non-empty")
    if "metadata" not in payload:
        raise ValueError(f"{path}: command metadata is required")
    metadata = payload["metadata"]
    if not isinstance(metadata, dict) or not all(
        isinstance(key, str) for key in metadata
    ):
        raise TypeError(f"{path}: command metadata must be a mapping")
    typed_metadata = cast(dict[str, object], metadata)
    if frozenset(typed_metadata) != _METADATA_FIELDS:
        raise ValueError(f"{path}: command metadata fields must equal aihub.tags")
    tags, route, intents, risk = _tags(path, typed_metadata["aihub.tags"])
    return CommandSpec(
        path, name, description, argument_hint, tags, route, intents, risk, body
    )


def audit_command_specs(
    root: Path, skill_names: Iterable[str] = ()
) -> tuple[CommandSpec, ...]:
    """Return all commands or raise on the first source/layout/collision defect."""

    command_root = root / "commands"
    if command_root.is_symlink() or not command_root.is_dir():
        raise ValueError(f"command root must be a physical directory: {command_root}")
    collisions = frozenset(skill_names)
    commands: list[CommandSpec] = []
    for path in sorted(command_root.rglob("*.md"), key=lambda item: item.name):
        metadata = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"command must be a physical regular file: {path}")
        rel = path.relative_to(command_root)
        if not _SLUG.fullmatch(rel.parent.name) or path.suffix != ".md" or _SLUG.fullmatch(path.stem) is None:
            raise ValueError(f"command must use commands/<category>/<slug>.md layout: {path}")
        spec = _load_command(path)
        if spec.name in collisions:
            raise ValueError(
                f"{path}: command slug collides with canonical skill: {spec.name}"
            )
        commands.append(spec)
    if not commands:
        raise ValueError(f"command inventory is empty: {command_root}")
    return tuple(commands)


def _quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _claude_markdown(spec: CommandSpec) -> str:
    header = ["---", f"description: {_quoted(spec.description)}"]
    if spec.argument_hint is not None:
        header.append(f"argument-hint: {_quoted(spec.argument_hint)}")
    header.extend(("disable-model-invocation: true", "---", ""))
    return "\n".join((*header, spec.body))


def _opencode_markdown(spec: CommandSpec) -> str:
    return "\n".join(
        ("---", f"description: {_quoted(spec.description)}", "---", "", spec.body)
    )


def _reject_interpolation(spec: CommandSpec, provider: CommandProvider) -> None:
    if "$(" in spec.body or "${" in spec.body:
        raise CommandRenderError(
            f"{provider.value}/{spec.name}: shell interpolation is forbidden"
        )
    if provider is CommandProvider.GEMINI and any(
        marker in spec.body for marker in ("!{", "@{", "{{")
    ):
        raise CommandRenderError(
            f"{provider.value}/{spec.name}: provider interpolation is forbidden"
        )
    if provider is CommandProvider.OPENCODE and re.search(r"!\s*`", spec.body):
        raise CommandRenderError(
            f"{provider.value}/{spec.name}: shell interpolation is forbidden"
        )


def render_command(
    spec: CommandSpec,
    provider: CommandProvider | str,
    *,
    token_budget: CommandTokenBudget | None = None,
    reserved_slugs: Iterable[str] = (),
) -> CommandArtifact:
    """Render one complete supported command or raise immediately."""

    selected = CommandProvider(provider)
    if selected is CommandProvider.CODEX:
        raise CommandRenderError("UNSUPPORTED: Codex has no canonical command adapter")
    if selected is CommandProvider.ANTIGRAVITY:
        raise CommandRenderError("UNSUPPORTED: Antigravity has no command contract")
    if selected is CommandProvider.COPILOT:
        raise CommandRenderError(
            "UNSUPPORTED: Copilot has no provider-owned command contract"
        )
    if selected is CommandProvider.CURSOR and spec.route is not CommandRoute.PROJECT:
        raise CommandRenderError("UNSUPPORTED: Cursor supports project commands only")
    if spec.name in frozenset(reserved_slugs):
        raise CommandRenderError(
            f"{selected.value}/{spec.name}: command slug is reserved by the provider"
        )
    if token_budget is None:
        raise CommandRenderError(
            f"{selected.value}/{spec.name}: provider token budget is required"
        )

    _reject_interpolation(spec, selected)
    if selected is CommandProvider.CLAUDE:
        content = _claude_markdown(spec)
        destination = PurePosixPath(".claude", "commands", f"{spec.name}.md")
    elif selected is CommandProvider.GEMINI:
        prompt = spec.body.replace(_ARGUMENTS, "{{args}}")
        content = (
            f"description = {_quoted(spec.description)}\nprompt = {_quoted(prompt)}\n"
        )
        destination = PurePosixPath(".gemini", "commands", f"{spec.name}.toml")
    elif selected is CommandProvider.OPENCODE:
        content = _opencode_markdown(spec)
        destination = PurePosixPath(f"{spec.name}.md")
    else:
        content = spec.body
        destination = PurePosixPath(".cursor", "commands", f"{spec.name}.md")
    measured = token_budget.measure(content)
    if token_budget.max_tokens is not None and measured > token_budget.max_tokens:
        raise CommandRenderError(
            f"{selected.value}/{spec.name}: rendered command uses {measured} tokens; "
            f"provider limit is {token_budget.max_tokens}"
        )
    return CommandArtifact(
        selected,
        spec.name,
        destination,
        content,
        True,
        measured,
        token_budget.max_tokens,
    )


__all__ = (
    "CommandArtifact",
    "CommandIntent",
    "CommandProvider",
    "CommandRenderError",
    "CommandRisk",
    "CommandRoute",
    "CommandSpec",
    "CommandTokenBudget",
    "audit_command_specs",
    "render_command",
    "waza_bpe_counter",
)
