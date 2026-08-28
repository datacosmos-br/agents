"""Strict command-native semantic evaluation contracts."""

from __future__ import annotations

import stat
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import cast

import yaml
from yaml.nodes import MappingNode, Node, SequenceNode

from .commands import CommandProvider, CommandRoute, CommandSpec

_TOP_LEVEL_FIELDS = frozenset({"command", "schemaVersion", "scenarios"})
_ASSERTION_FIELDS = frozenset({"output_contains", "output_not_contains"})
_PROVIDER_ROLES = frozenset(
    {"supported-rendering", "unsupported-provider", "projection-fixed-point"}
)


class CommandEvalRole(StrEnum):
    HAPPY_PATH = "happy-path"
    AMBIGUOUS_INPUT = "ambiguous-input"
    SHOULD_NOT_RUN = "should-not-run"
    SUPPORTED_RENDERING = "supported-rendering"
    UNSUPPORTED_PROVIDER = "unsupported-provider"
    SAFETY_REJECTION = "safety-rejection"
    PROJECTION_FIXED_POINT = "projection-fixed-point"


@dataclass(frozen=True)
class CommandEvalScenario:
    role: CommandEvalRole
    prompt: str
    providers: tuple[CommandProvider, ...]
    output_contains: tuple[str, ...]
    output_not_contains: tuple[str, ...]


@dataclass(frozen=True)
class CommandEvalSpec:
    path: Path
    command: str
    scenarios: tuple[CommandEvalScenario, ...]


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


def _mapping(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    node = yaml.compose(source, Loader=yaml.SafeLoader)
    loaded = yaml.safe_load(source)
    if not isinstance(node, MappingNode) or not isinstance(loaded, dict):
        raise TypeError(f"{path}: eval source must be a mapping")
    duplicate = _duplicate_key(node)
    if duplicate is not None:
        raise ValueError(f"{path}: eval key is duplicated: {duplicate}")
    raw = cast(dict[object, object], loaded)
    if not all(isinstance(key, str) for key in raw):
        raise TypeError(f"{path}: eval keys must be strings")
    return cast(dict[str, object], raw)


def _string_list(path: Path, value: object, field: str) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or not value
        or not all(
            isinstance(item, str) and item == item.strip() and bool(item)
            for item in value
        )
    ):
        raise TypeError(f"{path}: {field} must be a non-empty trimmed string array")
    items = tuple(cast(list[str], value))
    if len(items) != len(set(items)):
        raise ValueError(f"{path}: {field} values must be unique")
    return items


def _provider_contract(
    route: CommandRoute, role: CommandEvalRole
) -> tuple[CommandProvider, ...]:
    unsupported = {
        CommandProvider.ANTIGRAVITY,
        CommandProvider.CODEX,
        CommandProvider.COPILOT,
    }
    if route is CommandRoute.AGENT:
        unsupported.add(CommandProvider.CURSOR)
    selected = (
        unsupported
        if role is CommandEvalRole.UNSUPPORTED_PROVIDER
        else set(CommandProvider) - unsupported
    )
    return tuple(sorted(selected, key=lambda provider: provider.value))


def _scenario(
    path: Path, index: int, raw: object, route: CommandRoute
) -> CommandEvalScenario:
    label = f"{path}#scenario-{index + 1}"
    if not isinstance(raw, dict) or not all(isinstance(key, str) for key in raw):
        raise TypeError(f"{label}: scenario must be a mapping")
    data = cast(dict[str, object], raw)
    if "role" not in data:
        raise ValueError(f"{label}: role is required")
    raw_role = data["role"]
    if not isinstance(raw_role, str):
        raise TypeError(f"{label}: role must be a string")
    role = CommandEvalRole(raw_role)
    expected_fields = {"role", "prompt", "assertions"}
    if role.value in _PROVIDER_ROLES:
        expected_fields.add("providers")
    if frozenset(data) != frozenset(expected_fields):
        raise ValueError(
            f"{label}: scenario fields must equal {', '.join(sorted(expected_fields))}"
        )
    prompt = data["prompt"]
    if not isinstance(prompt, str) or not prompt or prompt != prompt.strip():
        raise ValueError(f"{label}: prompt must be non-empty and trimmed")
    assertions = data["assertions"]
    if not isinstance(assertions, dict) or not all(
        isinstance(key, str) for key in assertions
    ):
        raise TypeError(f"{label}: assertions must be a mapping")
    typed_assertions = cast(dict[str, object], assertions)
    if frozenset(typed_assertions) != _ASSERTION_FIELDS:
        raise ValueError(f"{label}: assertions fields are incomplete")
    contains = _string_list(
        path, typed_assertions["output_contains"], "output_contains"
    )
    excludes = _string_list(
        path, typed_assertions["output_not_contains"], "output_not_contains"
    )
    providers: tuple[CommandProvider, ...] = ()
    if role.value in _PROVIDER_ROLES:
        values = _string_list(path, data["providers"], "providers")
        providers = tuple(CommandProvider(value) for value in values)
        expected = _provider_contract(route, role)
        if providers != expected:
            raise ValueError(
                f"{label}: providers must equal "
                + ", ".join(provider.value for provider in expected)
            )
    return CommandEvalScenario(role, prompt, providers, contains, excludes)


def _load_spec(path: Path, command: CommandSpec) -> CommandEvalSpec:
    data = _mapping(path)
    if frozenset(data) != _TOP_LEVEL_FIELDS:
        raise ValueError(
            f"{path}: eval fields must equal command, scenarios, schemaVersion"
        )
    if data["command"] != command.name:
        raise ValueError(f"{path}: command must equal {command.name!r}")
    if data["schemaVersion"] != "1.0":
        raise ValueError(f"{path}: schemaVersion must equal '1.0'")
    raw_scenarios = data["scenarios"]
    if not isinstance(raw_scenarios, list):
        raise TypeError(f"{path}: scenarios must be an array")
    scenarios = tuple(
        _scenario(path, index, raw, command.route)
        for index, raw in enumerate(raw_scenarios)
    )
    if tuple(scenario.role for scenario in scenarios) != tuple(CommandEvalRole):
        raise ValueError(
            f"{path}: scenarios must contain each role once in canonical order"
        )
    prompts = tuple(scenario.prompt for scenario in scenarios)
    if len(prompts) != len(set(prompts)):
        raise ValueError(f"{path}: scenario prompts must be unique")
    return CommandEvalSpec(path, command.name, scenarios)


def audit_command_evals(
    root: Path, commands: tuple[CommandSpec, ...]
) -> tuple[CommandEvalSpec, ...]:
    """Return exact command-suite coverage or raise on the first defect."""

    eval_root = root / "evals" / "commands"
    if eval_root.is_symlink() or not eval_root.is_dir():
        raise ValueError(f"command eval root must be a physical directory: {eval_root}")
    by_name = {command.name: command for command in commands}
    if len(by_name) != len(commands):
        raise ValueError("command input contains duplicate names")
    entries = tuple(sorted(eval_root.iterdir(), key=lambda item: item.name))
    if {entry.name for entry in entries} != set(by_name):
        raise ValueError(
            "command eval directories must exactly equal command inventory"
        )
    specs: list[CommandEvalSpec] = []
    for directory in entries:
        metadata = directory.lstat()
        if directory.is_symlink() or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"command eval suite must be physical: {directory}")
        files = tuple(sorted(directory.iterdir(), key=lambda item: item.name))
        if len(files) != 1 or files[0].name != "eval.yaml":
            raise ValueError(
                f"command eval suite must contain only eval.yaml: {directory}"
            )
        path = files[0]
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"command eval source must be physical: {path}")
        specs.append(_load_spec(path, by_name[directory.name]))
    return tuple(specs)


__all__ = (
    "CommandEvalRole",
    "CommandEvalScenario",
    "CommandEvalSpec",
    "audit_command_evals",
)
