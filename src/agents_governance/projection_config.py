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


class ProjectionStatus(StrEnum):
    """Closed support classification for every matrix cell."""

    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


class RuleLayout(StrEnum):
    """Native storage shape for synchronized rule instructions."""

    DIRECTORY = "directory"
    DOCUMENT = "document"


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
    layout: RuleLayout | None = None


@dataclass(frozen=True)
class ProjectionConfig:
    """Complete immutable v7 projection contract."""

    version: int
    projection_manifest_version: int
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
_MANIFEST_VERSION_FIELDS = frozenset({"projection"})
_CONTEXTS = frozenset(context.value for context in ProjectionContext)
_SURFACES = frozenset(surface.value for surface in ProjectionSurface)
_PROVIDERS = frozenset(provider.value for provider in AgentProvider)


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
    layout: RuleLayout | None = None
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
    if value["version"] != 7:
        raise ValueError("projection config must use version 7")
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
    return ProjectionConfig(7, 5, MappingProxyType(cells))


__all__ = (
    "ProjectionCell",
    "ProjectionConfig",
    "ProjectionContext",
    "ProjectionStatus",
    "ProjectionSurface",
    "RuleLayout",
    "load_projection_config",
)
