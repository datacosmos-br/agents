"""Strict owner for the provider/context/surface projection matrix."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import cast

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
    """Complete immutable v6 projection contract."""

    version: int
    projection_manifest_version: int
    hook_manifest_version: int
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


_ROOT_FIELDS = frozenset({"manifest_versions", "providers", "version"})
_MANIFEST_VERSION_FIELDS = frozenset({"hooks", "projection"})
_CONTEXTS = frozenset(context.value for context in ProjectionContext)
_SURFACES = frozenset(surface.value for surface in ProjectionSurface)
_PROVIDERS = frozenset(provider.value for provider in AgentProvider)
_HOOK_EVENTS = frozenset(
    {"context_refresh", "prompt_submit", "session_start", "subagent_start"}
)


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{label} must be an object with string keys")
    return cast(dict[str, object], value)


def _exact_fields(
    value: dict[str, object], expected: frozenset[str], label: str
) -> None:
    actual = frozenset(value)
    if actual != expected:
        raise ValueError(
            f"{label} must equal {', '.join(sorted(expected))}; "
            f"got {', '.join(sorted(actual)) or 'none'}"
        )


def _validate_path(path: object, context: ProjectionContext, label: str) -> str:
    if not isinstance(path, str) or not path:
        raise TypeError(f"{label} path must be a non-empty string")
    if path.startswith(("~", "/home/", "/Users/")):
        raise ValueError(f"{label} path must not hardcode a user home")
    if context is ProjectionContext.PERSONAL:
        if not path.startswith("${HOME}/"):
            raise ValueError(f"{label} personal path must start with ${{HOME}}/")
        candidate = PurePosixPath(path.removeprefix("${HOME}/"))
        if candidate == PurePosixPath(".") or ".." in candidate.parts:
            raise ValueError(f"{label} personal path must remain below ${{HOME}}")
    else:
        candidate = PurePosixPath(path)
    if context is ProjectionContext.PROJECT and (
        candidate.is_absolute()
        or candidate == PurePosixPath(".")
        or ".." in candidate.parts
    ):
        raise ValueError(f"{label} project path must remain repository-relative")
    return path


def _cell(
    provider: AgentProvider,
    context: ProjectionContext,
    surface: ProjectionSurface,
    raw: object,
) -> ProjectionCell:
    label = f"projection cell {provider.value}/{context.value}/{surface.value}"
    value = _mapping(raw, label)
    if "status" not in value:
        raise ValueError(f"{label} status is required")
    raw_status = value["status"]
    if not isinstance(raw_status, str):
        raise TypeError(f"{label} status must be a string")
    status = ProjectionStatus(raw_status)
    if status is ProjectionStatus.UNSUPPORTED:
        _exact_fields(
            value, frozenset({"reason", "status"}), f"{label} UNSUPPORTED cell fields"
        )
        reason = value["reason"]
        if not isinstance(reason, str) or not reason.startswith("UNSUPPORTED: "):
            raise ValueError(
                f"{label} UNSUPPORTED reason must start with 'UNSUPPORTED: '"
            )
        return ProjectionCell(provider, context, surface, status, reason=reason)

    expected = {"path", "status"}
    if surface is ProjectionSurface.COMMANDS and "max_tokens" in value:
        expected.add("max_tokens")
    if surface is ProjectionSurface.HOOKS:
        expected.add("events")
    if surface is ProjectionSurface.RULES:
        expected.add("layout")
    _exact_fields(value, frozenset(expected), f"{label} SUPPORTED cell fields")
    path = _validate_path(value["path"], context, label)
    max_tokens = value.get("max_tokens")
    if max_tokens is not None and (
        not isinstance(max_tokens, int)
        or isinstance(max_tokens, bool)
        or max_tokens <= 0
    ):
        raise ValueError(f"{label} max_tokens must be a positive integer")
    events: MappingProxyType[str, HookEvent] | None = None
    layout: RuleLayout | None = None
    if surface is ProjectionSurface.HOOKS:
        raw_events = _mapping(value["events"], f"{label} events")
        _exact_fields(raw_events, _HOOK_EVENTS, f"{label} events")
        parsed_events: dict[str, HookEvent] = {}
        for logical_event in sorted(_HOOK_EVENTS):
            event_label = f"{label} events.{logical_event}"
            event = _mapping(raw_events[logical_event], event_label)
            raw_event_status = event.get("status")
            if not isinstance(raw_event_status, str):
                raise TypeError(f"{event_label} status must be a string")
            event_status = ProjectionStatus(raw_event_status)
            if event_status is ProjectionStatus.UNSUPPORTED:
                _exact_fields(
                    event,
                    frozenset({"reason", "status"}),
                    f"{event_label} UNSUPPORTED fields",
                )
                reason = event["reason"]
                if not isinstance(reason, str) or not reason.startswith(
                    "UNSUPPORTED: "
                ):
                    raise ValueError(
                        f"{event_label} UNSUPPORTED reason must start with "
                        "'UNSUPPORTED: '"
                    )
                parsed_events[logical_event] = HookEvent(
                    event_status, reason=reason
                )
                continue
            _exact_fields(
                event,
                frozenset({"clients", "coverage", "native", "status"}),
                f"{event_label} SUPPORTED fields",
            )
            native = event["native"]
            if (
                not isinstance(native, list)
                or not native
                or not all(
                    isinstance(item, str)
                    and item
                    and item == item.strip()
                    and not any(character.isspace() for character in item)
                    for item in native
                )
            ):
                raise TypeError(
                    f"{event_label} native must be a non-empty "
                    "array of native event names"
                )
            selected = tuple(cast(list[str], native))
            if len(selected) != len(set(selected)):
                raise ValueError(
                    f"{event_label} native must contain unique names"
                )
            raw_coverage = event["coverage"]
            if not isinstance(raw_coverage, str):
                raise TypeError(f"{event_label} coverage must be a string")
            coverage = HookCoverage(raw_coverage)
            raw_clients = event["clients"]
            if not isinstance(raw_clients, list) or not raw_clients or not all(
                isinstance(client, str) for client in raw_clients
            ):
                raise TypeError(
                    f"{event_label} clients must be a non-empty array of strings"
                )
            clients = tuple(HookClient(client) for client in raw_clients)
            if clients != tuple(sorted(set(clients), key=lambda item: item.value)):
                raise ValueError(f"{event_label} clients must be unique and sorted")
            parsed_events[logical_event] = HookEvent(
                event_status,
                selected,
                coverage,
                clients,
            )
        events = MappingProxyType(parsed_events)
    if surface is ProjectionSurface.RULES:
        raw_layout = value["layout"]
        if not isinstance(raw_layout, str):
            raise TypeError(f"{label} layout must be a string")
        layout = RuleLayout(raw_layout)
        if layout is RuleLayout.DOCUMENT and not path.endswith(".md"):
            raise ValueError(f"{label} document layout path must end with .md")
    return ProjectionCell(
        provider,
        context,
        surface,
        status,
        path=path,
        max_tokens=max_tokens,
        events=events,
        layout=layout,
    )


def load_projection_config(root: Path) -> ProjectionConfig:
    """Load the only accepted schema; legacy and partial matrices fail closed."""

    path = root / "config" / "projections.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("projection config must be a physical regular file")
    payload = json.loads(path.read_text(encoding="utf-8"))
    value = _mapping(payload, "projection config")
    _exact_fields(value, _ROOT_FIELDS, "projection config fields")
    if value["version"] != 6:
        raise ValueError("projection config must use version 6")
    manifest_versions = _mapping(
        value["manifest_versions"], "projection manifest versions"
    )
    _exact_fields(
        manifest_versions,
        _MANIFEST_VERSION_FIELDS,
        "projection manifest versions",
    )
    if manifest_versions["projection"] != 5:
        raise ValueError("projection directory manifest version must equal 5")
    if manifest_versions["hooks"] != 3:
        raise ValueError("projection hook manifest version must equal 3")

    providers = _mapping(value["providers"], "projection providers")
    _exact_fields(providers, _PROVIDERS, "projection providers")
    cells: dict[
        tuple[AgentProvider, ProjectionContext, ProjectionSurface], ProjectionCell
    ] = {}
    for provider in AgentProvider:
        contexts = _mapping(
            providers[provider.value], f"projection contexts for {provider.value}"
        )
        _exact_fields(contexts, _CONTEXTS, f"projection contexts for {provider.value}")
        for context in ProjectionContext:
            surfaces = _mapping(
                contexts[context.value],
                f"projection surfaces for {provider.value}/{context.value}",
            )
            _exact_fields(
                surfaces,
                _SURFACES,
                f"projection surfaces for {provider.value}/{context.value}",
            )
            for surface in ProjectionSurface:
                key = (provider, context, surface)
                cells[key] = _cell(provider, context, surface, surfaces[surface.value])
    return ProjectionConfig(6, 5, 3, MappingProxyType(cells))


__all__ = (
    "HookClient",
    "HookCoverage",
    "HookEvent",
    "ProjectionCell",
    "ProjectionConfig",
    "ProjectionContext",
    "ProjectionStatus",
    "ProjectionSurface",
    "RuleLayout",
    "load_projection_config",
)
