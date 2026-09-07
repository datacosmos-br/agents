"""Strict provider-neutral command discovery."""

from __future__ import annotations

import json
import re
import stat
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import cast

from .approvals import APPROVAL_NAMESPACES, core_tags, resolve_approval_tags
from .frontmatter import parse_frontmatter

_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_DESCRIPTION_LIMIT = 160
_TOP_LEVEL_FIELDS = frozenset({"name", "description", "argument-hint", "metadata"})
_METADATA_FIELDS = frozenset({"aihub.tags"})
_ARGUMENTS = "$ARGUMENTS"


class CommandRoute(StrEnum):
    AGENT = "agent"
    PROJECT = "project"


@dataclass(frozen=True)
class CommandSpec:
    path: Path
    name: str
    description: str
    argument_hint: str | None
    tags: tuple[str, ...]
    route: CommandRoute
    body: str

    def __post_init__(self) -> None:
        _validate_spec(self)

    @property
    def uses_arguments(self) -> bool:
        return _ARGUMENTS in self.body


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
    expected = {f"route:{spec.route.value}"}
    if len(spec.tags) != len(set(spec.tags)) or tuple(sorted(spec.tags)) != spec.tags:
        raise ValueError("command tags must be unique and sorted")
    if set(core_tags(spec.tags)) != expected:
        raise ValueError(
            "command tags must contain only the typed route value and approval tags"
        )


def _tags(path: Path, raw: object) -> tuple[tuple[str, ...], CommandRoute]:
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
    if any(
        not tag.startswith("route:") and tag.split(":", 1)[0] not in APPROVAL_NAMESPACES
        for tag in tags
    ):
        raise ValueError(
            f"{path}: command tags support only route and approval namespaces"
        )
    route_values = tuple(
        tag.removeprefix("route:") for tag in tags if tag.startswith("route:")
    )
    if len(route_values) != 1:
        raise ValueError(f"{path}: command requires exactly one route")
    route = CommandRoute(route_values[0])
    return tags, route


def _load_command(path: Path) -> CommandSpec:
    payload, body = parse_frontmatter(path)
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
    tags, route = _tags(path, typed_metadata["aihub.tags"])
    return CommandSpec(path, name, description, argument_hint, tags, route, body)


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
        if (
            not _SLUG.fullmatch(rel.parent.name)
            or path.suffix != ".md"
            or _SLUG.fullmatch(path.stem) is None
        ):
            raise ValueError(
                f"command must use commands/<category>/<slug>.md layout: {path}"
            )
        spec = _load_command(path)
        resolve_approval_tags(root, spec.tags, path)
        if spec.name in collisions:
            raise ValueError(
                f"{path}: command slug collides with canonical skill: {spec.name}"
            )
        commands.append(spec)
    if not commands:
        raise ValueError(f"command inventory is empty: {command_root}")
    return tuple(commands)


__all__ = (
    "CommandRoute",
    "CommandSpec",
    "audit_command_specs",
)
