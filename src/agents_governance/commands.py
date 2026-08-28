"""Typed validation and provider-native rendering for canonical commands."""

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

from .atomic_io import discard_physical_file, stage_text
from .tokens import bpe_tokens

_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DESCRIPTION_LIMIT = 160
_TOP_LEVEL_FIELDS = frozenset({"name", "description", "argument-hint", "metadata"})
_METADATA_FIELDS = frozenset({"aihub.tags"})
_ARGUMENTS = "$ARGUMENTS"


class CommandRoute(StrEnum):
    """Supported canonical command distribution routes."""

    AGENT = "agent"
    PROJECT = "project"


class CommandIntent(StrEnum):
    """Approved command intents."""

    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    INSPECTION = "inspection"
    VERIFICATION = "verification"
    LANDING = "landing"
    GOVERNANCE = "governance"


class CommandRisk(StrEnum):
    """Primary command side-effect classification."""

    READ = "read"
    WRITE = "write"
    EXTERNAL = "external"


class CommandProvider(StrEnum):
    """Provider adapters with an explicit support contract."""

    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENCODE = "opencode"
    CURSOR = "cursor"
    COPILOT = "copilot"
    CODEX = "codex"
    ANTIGRAVITY = "antigravity"


class CommandAdapterStatus(StrEnum):
    """Typed adapter outcome without implicit fallback."""

    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class CommandFinding:
    """One blocking canonical-command defect."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class CommandSpec:
    """One fully validated provider-neutral command."""

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
        problem = _spec_problem(self)
        if problem is not None:
            raise ValueError(problem)

    @property
    def uses_arguments(self) -> bool:
        """Whether the complete source body consumes canonical arguments."""

        return _ARGUMENTS in self.body


@dataclass(frozen=True)
class CommandAudit:
    """Deterministically discovered commands and all blocking findings."""

    commands: tuple[CommandSpec, ...]
    findings: tuple[CommandFinding, ...]


@dataclass(frozen=True)
class CommandArtifact:
    """One complete provider-native command artifact."""

    provider: CommandProvider
    slug: str
    destination: PurePosixPath
    content: str
    manual_only: bool
    tokens: int
    max_tokens: int | None
    status: CommandAdapterStatus = field(
        default=CommandAdapterStatus.SUPPORTED, init=False
    )


@dataclass(frozen=True)
class UnsupportedCommand:
    """Explicit unsupported adapter result; never a fallback projection."""

    provider: CommandProvider
    slug: str
    reason: str
    status: CommandAdapterStatus = field(
        default=CommandAdapterStatus.UNSUPPORTED, init=False
    )


type CommandRender = CommandArtifact | UnsupportedCommand


class CommandRenderError(ValueError):
    """A supported adapter refused an unsafe or colliding command."""


@dataclass(frozen=True)
class CommandTokenBudget:
    """Caller-owned full-text counter and optional documented provider limit."""

    max_tokens: int | None
    counter: Callable[[str], int] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.max_tokens is not None and (
            not isinstance(self.max_tokens, int)
            or isinstance(self.max_tokens, bool)
            or self.max_tokens <= 0
        ):
            raise ValueError("command max_tokens must be a positive integer")
        if not callable(self.counter):
            raise TypeError("command token counter must be callable")

    def measure(self, content: str) -> int:
        """Measure the complete rendered command and reject invalid counters."""

        measured = self.counter(content)
        if not isinstance(measured, int) or isinstance(measured, bool) or measured < 0:
            raise CommandRenderError(
                "command token counter must return a non-negative integer"
            )
        return measured


def waza_bpe_counter(root: Path) -> Callable[[str], int]:
    """Build a full-text counter backed by the canonical Waza BPE owner."""

    authority = root.resolve()

    def count(content: str) -> int:
        candidate = stage_text(authority / "commands" / ".rendered-command.md", content)
        try:
            measured = bpe_tokens(candidate, authority)
        except (OSError, RuntimeError) as error:
            try:
                discard_physical_file(candidate)
            except (OSError, RuntimeError) as cleanup_error:
                error.add_note(f"token candidate cleanup failed: {cleanup_error}")
                raise error from cleanup_error
            raise
        discard_physical_file(candidate)
        return measured

    return count


class _FrontmatterError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


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


def _spec_problem(spec: CommandSpec) -> str | None:
    if not _SLUG.fullmatch(spec.name) or spec.path.stem != spec.name:
        return "command name must be a lowercase slug equal to the filename"
    if not _short_sentence(spec.description):
        return "command description must be one short sentence"
    if spec.argument_hint is not None and not _argument_hint_valid(spec.argument_hint):
        return "command argument-hint must be one short non-empty line"
    if not spec.body.strip():
        return "command body must be non-empty"
    if _ARGUMENTS in spec.body and spec.argument_hint is None:
        return "command argument-hint is required when the body uses $ARGUMENTS"
    if not isinstance(spec.route, CommandRoute):
        return "command route must be typed"
    if not isinstance(spec.risk, CommandRisk):
        return "command risk must be typed"
    if not spec.intents or not all(
        isinstance(intent, CommandIntent) for intent in spec.intents
    ):
        return "command intent must contain approved typed values"
    if tuple(sorted(spec.intents, key=lambda item: item.value)) != spec.intents:
        return "command intents must be sorted"
    expected = {
        f"route:{spec.route.value}",
        f"risk:{spec.risk.value}",
        *(f"intent:{intent.value}" for intent in spec.intents),
    }
    if len(spec.tags) != len(set(spec.tags)) or tuple(sorted(spec.tags)) != spec.tags:
        return "command tags must be unique and sorted"
    if set(spec.tags) != expected:
        return "command tags must contain only typed route, intent, and risk values"
    return None


def _duplicate_key(node: Node) -> str | None:
    if isinstance(node, MappingNode):
        seen: set[str] = set()
        for key_node, value_node in node.value:
            key = getattr(key_node, "value", "<non-scalar>")
            if key in seen:
                return str(key)
            seen.add(str(key))
            duplicate = _duplicate_key(value_node)
            if duplicate is not None:
                return duplicate
    elif isinstance(node, SequenceNode):
        for child in node.value:
            duplicate = _duplicate_key(child)
            if duplicate is not None:
                return duplicate
    return None


def _frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise _FrontmatterError("command-frontmatter", "missing YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise _FrontmatterError("command-frontmatter", "unterminated YAML frontmatter")
    source = text[4:marker]
    try:
        node = yaml.compose(source, Loader=yaml.SafeLoader)
        loaded = yaml.safe_load(source)
    except yaml.YAMLError as error:
        raise _FrontmatterError(
            "command-frontmatter", str(error).splitlines()[0]
        ) from error
    if not isinstance(node, MappingNode) or not isinstance(loaded, dict):
        raise _FrontmatterError("command-frontmatter", "frontmatter must be a mapping")
    duplicate = _duplicate_key(node)
    if duplicate is not None:
        raise _FrontmatterError(
            "command-frontmatter", f"frontmatter key is duplicated: {duplicate}"
        )
    raw = cast(dict[object, object], loaded)
    if not all(isinstance(key, str) for key in raw):
        raise _FrontmatterError(
            "command-frontmatter", "frontmatter keys must be strings"
        )
    body = text[marker + 5 :].removeprefix("\n")
    return cast(dict[str, object], raw), body


def _tags(
    relative: str, raw: object
) -> tuple[
    tuple[str, ...] | None,
    CommandRoute | None,
    tuple[CommandIntent, ...] | None,
    CommandRisk | None,
    list[CommandFinding],
]:
    findings: list[CommandFinding] = []
    if not isinstance(raw, str):
        return (
            None,
            None,
            None,
            None,
            [
                CommandFinding(
                    relative,
                    "command-tags",
                    "metadata.aihub.tags must be a JSON string",
                )
            ],
        )
    try:
        decoded: object = json.loads(raw)
    except json.JSONDecodeError as error:
        return (
            None,
            None,
            None,
            None,
            [CommandFinding(relative, "command-tags", f"invalid tag JSON: {error}")],
        )
    if not isinstance(decoded, list) or not all(
        isinstance(item, str) for item in decoded
    ):
        return (
            None,
            None,
            None,
            None,
            [
                CommandFinding(
                    relative,
                    "command-tags",
                    "metadata.aihub.tags must encode a JSON array of strings",
                )
            ],
        )
    tags = tuple(cast(list[str], decoded))
    if len(tags) != len(set(tags)) or tags != tuple(sorted(tags)):
        findings.append(
            CommandFinding(
                relative, "command-tags", "command tags must be unique and sorted"
            )
        )
    recognized = ("route:", "intent:", "risk:")
    if any(not tag.startswith(recognized) for tag in tags):
        findings.append(
            CommandFinding(
                relative,
                "command-tags",
                "command tags support only route, intent, and risk values",
            )
        )

    route_values = [
        tag.removeprefix("route:") for tag in tags if tag.startswith("route:")
    ]
    route: CommandRoute | None = None
    if len(route_values) != 1 or route_values[0] not in CommandRoute:
        findings.append(
            CommandFinding(
                relative,
                "command-route",
                "command requires exactly one route:agent or route:project",
            )
        )
    else:
        route = CommandRoute(route_values[0])

    risk_values = [tag.removeprefix("risk:") for tag in tags if tag.startswith("risk:")]
    risk: CommandRisk | None = None
    if len(risk_values) != 1 or risk_values[0] not in CommandRisk:
        findings.append(
            CommandFinding(
                relative,
                "command-risk",
                "command requires exactly one risk:read, risk:write, or risk:external",
            )
        )
    else:
        risk = CommandRisk(risk_values[0])

    intent_values = [
        tag.removeprefix("intent:") for tag in tags if tag.startswith("intent:")
    ]
    intents: tuple[CommandIntent, ...] | None = None
    if not intent_values or any(value not in CommandIntent for value in intent_values):
        findings.append(
            CommandFinding(
                relative,
                "command-intent",
                "command requires at least one approved intent",
            )
        )
    else:
        intents = tuple(CommandIntent(value) for value in intent_values)
    return tags, route, intents, risk, findings


def _load_command(
    root: Path, path: Path
) -> tuple[CommandSpec | None, list[CommandFinding]]:
    relative = _relative(root, path)
    try:
        payload, body = _frontmatter(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        return None, [CommandFinding(relative, "command-io", str(error))]
    except _FrontmatterError as error:
        return None, [CommandFinding(relative, error.code, str(error))]

    findings: list[CommandFinding] = []
    unknown = sorted(set(payload) - _TOP_LEVEL_FIELDS)
    if unknown:
        findings.append(
            CommandFinding(
                relative,
                "command-field",
                f"unknown command frontmatter fields: {', '.join(unknown)}",
            )
        )

    raw_name = payload.get("name")
    name = raw_name if isinstance(raw_name, str) else None
    if name != path.stem or name is None or not _SLUG.fullmatch(name):
        findings.append(
            CommandFinding(
                relative,
                "command-name",
                f"frontmatter name must equal lowercase filename slug {path.stem!r}",
            )
        )

    raw_description = payload.get("description")
    description = raw_description if isinstance(raw_description, str) else None
    if description is None or not _short_sentence(description):
        findings.append(
            CommandFinding(
                relative,
                "command-description",
                "description must be one non-empty sentence of at most 160 characters",
            )
        )

    raw_hint = payload.get("argument-hint")
    argument_hint = raw_hint if isinstance(raw_hint, str) else None
    if "argument-hint" in payload and (
        argument_hint is None or not _argument_hint_valid(argument_hint)
    ):
        findings.append(
            CommandFinding(
                relative,
                "command-argument-hint",
                "argument-hint must be one short non-empty line",
            )
        )
    if _ARGUMENTS in body and argument_hint is None:
        findings.append(
            CommandFinding(
                relative,
                "command-argument-hint",
                "argument-hint is required when the body uses $ARGUMENTS",
            )
        )
    if not body.strip():
        findings.append(
            CommandFinding(relative, "command-body", "command body must be non-empty")
        )

    raw_metadata = payload.get("metadata")
    metadata: dict[str, object] | None = None
    if isinstance(raw_metadata, dict) and all(
        isinstance(key, str) for key in raw_metadata
    ):
        metadata = cast(dict[str, object], raw_metadata)
    else:
        findings.append(
            CommandFinding(relative, "command-metadata", "metadata must be a mapping")
        )

    tags: tuple[str, ...] | None = None
    route: CommandRoute | None = None
    intents: tuple[CommandIntent, ...] | None = None
    risk: CommandRisk | None = None
    if metadata is not None:
        unknown_metadata = sorted(set(metadata) - _METADATA_FIELDS)
        if unknown_metadata:
            findings.append(
                CommandFinding(
                    relative,
                    "command-metadata",
                    f"unknown metadata fields: {', '.join(unknown_metadata)}",
                )
            )
        if "aihub.tags" not in metadata:
            findings.append(
                CommandFinding(
                    relative,
                    "command-tags",
                    "metadata.aihub.tags is required",
                )
            )
        else:
            tags, route, intents, risk, tag_findings = _tags(
                relative, metadata["aihub.tags"]
            )
            findings.extend(tag_findings)

    if findings:
        return None, findings
    assert name is not None
    assert description is not None
    assert tags is not None
    assert route is not None
    assert intents is not None
    assert risk is not None
    return (
        CommandSpec(
            path=path,
            name=name,
            description=description,
            argument_hint=argument_hint,
            tags=tags,
            route=route,
            intents=intents,
            risk=risk,
            body=body,
        ),
        [],
    )


def audit_command_specs(root: Path, skill_names: Iterable[str] = ()) -> CommandAudit:
    """Discover strict flat commands and reject invalid or colliding slugs."""

    command_root = root / "commands"
    if command_root.is_symlink():
        return CommandAudit(
            (),
            (
                CommandFinding(
                    "commands", "command-symlink", "command root must be physical"
                ),
            ),
        )
    if not command_root.exists():
        return CommandAudit(
            (),
            (
                CommandFinding(
                    "commands", "command-directory", "command root is missing"
                ),
            ),
        )
    if not command_root.is_dir():
        return CommandAudit(
            (),
            (
                CommandFinding(
                    "commands",
                    "command-directory",
                    "command root must be a directory",
                ),
            ),
        )

    collisions = frozenset(skill_names)
    commands: list[CommandSpec] = []
    findings: list[CommandFinding] = []
    try:
        entries = sorted(command_root.iterdir(), key=lambda item: item.name)
    except OSError as error:
        return CommandAudit((), (CommandFinding("commands", "command-io", str(error)),))
    for path in entries:
        relative = _relative(root, path)
        if path.is_symlink():
            findings.append(
                CommandFinding(
                    relative,
                    "command-symlink",
                    "command must be a physical regular file",
                )
            )
            continue
        try:
            metadata = path.lstat()
        except OSError as error:
            findings.append(CommandFinding(relative, "command-io", str(error)))
            continue
        if stat.S_ISDIR(metadata.st_mode) or path.suffix != ".md":
            findings.append(
                CommandFinding(
                    relative,
                    "command-layout",
                    "commands must use the flat commands/<slug>.md layout",
                )
            )
            continue
        if not stat.S_ISREG(metadata.st_mode):
            findings.append(
                CommandFinding(
                    relative,
                    "command-regular-file",
                    "command must be a physical regular file",
                )
            )
            continue
        if not _SLUG.fullmatch(path.stem):
            findings.append(
                CommandFinding(
                    relative,
                    "command-name",
                    "command filename must be a lowercase hyphenated slug",
                )
            )
            continue
        spec, file_findings = _load_command(root, path)
        findings.extend(file_findings)
        if spec is None:
            continue
        if spec.name in collisions:
            findings.append(
                CommandFinding(
                    relative,
                    "command-skill-collision",
                    f"command slug collides with canonical skill: {spec.name}",
                )
            )
            continue
        commands.append(spec)
    return CommandAudit(tuple(commands), tuple(findings))


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
    body = spec.body
    if "$(" in body or "${" in body:
        raise CommandRenderError(
            f"{provider.value}/{spec.name}: shell interpolation is forbidden"
        )
    if provider is CommandProvider.GEMINI and any(
        marker in body for marker in ("!{", "@{", "{{")
    ):
        raise CommandRenderError(
            f"{provider.value}/{spec.name}: provider interpolation is forbidden"
        )
    if provider is CommandProvider.OPENCODE and re.search(r"!\s*`", body):
        raise CommandRenderError(
            f"{provider.value}/{spec.name}: shell interpolation is forbidden"
        )


def _unsupported(
    spec: CommandSpec, provider: CommandProvider, reason: str
) -> UnsupportedCommand:
    return UnsupportedCommand(
        provider=provider,
        slug=spec.name,
        reason=f"UNSUPPORTED: {reason}",
    )


def render_command(
    spec: CommandSpec,
    provider: CommandProvider | str,
    *,
    token_budget: CommandTokenBudget | None = None,
    reserved_slugs: Iterable[str] = (),
) -> CommandRender:
    """Render one complete command or return explicit ``UNSUPPORTED``."""

    try:
        selected = CommandProvider(provider)
    except ValueError as error:
        raise ValueError(f"unknown command provider: {provider}") from error

    if selected is CommandProvider.CODEX:
        return _unsupported(spec, selected, "Codex has no canonical command adapter")
    if selected is CommandProvider.ANTIGRAVITY:
        return _unsupported(
            spec, selected, "Antigravity command projection remains disabled"
        )
    if selected is CommandProvider.CURSOR and spec.route is not CommandRoute.PROJECT:
        return _unsupported(spec, selected, "Cursor supports project commands only")
    if spec.name in frozenset(reserved_slugs):
        raise CommandRenderError(
            f"{selected.value}/{spec.name}: command slug is reserved by the provider"
        )

    _reject_interpolation(spec, selected)
    if selected in {CommandProvider.CLAUDE, CommandProvider.COPILOT}:
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
        assert selected is CommandProvider.CURSOR
        content = spec.body
        destination = PurePosixPath(".cursor", "commands", f"{spec.name}.md")
    if token_budget is None:
        raise CommandRenderError(
            f"{selected.value}/{spec.name}: provider token budget is required"
        )
    measured = token_budget.measure(content)
    if token_budget.max_tokens is not None and measured > token_budget.max_tokens:
        raise CommandRenderError(
            f"{selected.value}/{spec.name}: rendered command uses {measured} tokens; "
            f"provider limit is {token_budget.max_tokens}"
        )
    return CommandArtifact(
        provider=selected,
        slug=spec.name,
        destination=destination,
        content=content,
        manual_only=True,
        tokens=measured,
        max_tokens=token_budget.max_tokens,
    )


__all__ = (
    "CommandAdapterStatus",
    "CommandArtifact",
    "CommandAudit",
    "CommandFinding",
    "CommandIntent",
    "CommandProvider",
    "CommandRender",
    "CommandRenderError",
    "CommandRisk",
    "CommandRoute",
    "CommandSpec",
    "CommandTokenBudget",
    "UnsupportedCommand",
    "audit_command_specs",
    "render_command",
    "waza_bpe_counter",
)
