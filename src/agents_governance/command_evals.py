"""Strict, command-native semantic evaluation contracts."""

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
_SCENARIO_FIELDS = frozenset({"role", "prompt", "providers", "assertions"})
_ASSERTION_FIELDS = frozenset({"output_contains", "output_not_contains"})
_PROVIDER_ROLES = frozenset(
    {
        "supported-rendering",
        "unsupported-provider",
        "projection-fixed-point",
    }
)


class CommandEvalRole(StrEnum):
    """The seven independent behavior families required for every command."""

    HAPPY_PATH = "happy-path"
    AMBIGUOUS_INPUT = "ambiguous-input"
    SHOULD_NOT_RUN = "should-not-run"
    SUPPORTED_RENDERING = "supported-rendering"
    UNSUPPORTED_PROVIDER = "unsupported-provider"
    SAFETY_REJECTION = "safety-rejection"
    PROJECTION_FIXED_POINT = "projection-fixed-point"


@dataclass(frozen=True)
class CommandEvalFinding:
    """One blocking command-evaluation defect."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class CommandEvalScenario:
    """One material command behavior contract."""

    role: CommandEvalRole
    prompt: str
    providers: tuple[CommandProvider, ...]
    output_contains: tuple[str, ...]
    output_not_contains: tuple[str, ...]


@dataclass(frozen=True)
class CommandEvalSpec:
    """One complete seven-family command evaluation suite."""

    path: Path
    command: str
    scenarios: tuple[CommandEvalScenario, ...]


@dataclass(frozen=True)
class CommandEvalAudit:
    """All discovered command suites and blocking defects."""

    specs: tuple[CommandEvalSpec, ...]
    findings: tuple[CommandEvalFinding, ...]


class _EvalSourceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


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
    try:
        source = path.read_text(encoding="utf-8")
        node = yaml.compose(source, Loader=yaml.SafeLoader)
        loaded = yaml.safe_load(source)
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise _EvalSourceError(
            "command-eval-source", str(error).splitlines()[0]
        ) from error
    if not isinstance(node, MappingNode) or not isinstance(loaded, dict):
        raise _EvalSourceError("command-eval-schema", "eval source must be a mapping")
    duplicate = _duplicate_key(node)
    if duplicate is not None:
        raise _EvalSourceError(
            "command-eval-schema", f"eval key is duplicated: {duplicate}"
        )
    raw = cast(dict[object, object], loaded)
    if not all(isinstance(key, str) for key in raw):
        raise _EvalSourceError("command-eval-schema", "eval keys must be strings")
    return cast(dict[str, object], raw)


def _string_list(value: object) -> tuple[str, ...] | None:
    if (
        not isinstance(value, list)
        or not value
        or not all(
            isinstance(item, str) and item == item.strip() and bool(item)
            for item in value
        )
    ):
        return None
    items = tuple(cast(list[str], value))
    return items if len(items) == len(set(items)) else None


def _provider_contract(
    route: CommandRoute, role: CommandEvalRole
) -> tuple[CommandProvider, ...]:
    unsupported = {CommandProvider.ANTIGRAVITY, CommandProvider.CODEX}
    if route is CommandRoute.AGENT:
        unsupported.add(CommandProvider.CURSOR)
    selected = (
        unsupported
        if role is CommandEvalRole.UNSUPPORTED_PROVIDER
        else set(CommandProvider) - unsupported
    )
    return tuple(sorted(selected, key=lambda provider: provider.value))


def _scenario(
    relative: str,
    index: int,
    raw: object,
    route: CommandRoute,
) -> tuple[CommandEvalScenario | None, list[CommandEvalFinding]]:
    label = f"{relative}#scenario-{index + 1}"
    findings: list[CommandEvalFinding] = []
    if not isinstance(raw, dict) or not all(isinstance(key, str) for key in raw):
        return None, [
            CommandEvalFinding(
                label, "command-eval-schema", "scenario must be a mapping"
            )
        ]
    data = cast(dict[str, object], raw)
    unknown = sorted(set(data) - _SCENARIO_FIELDS)
    if unknown:
        findings.append(
            CommandEvalFinding(
                label,
                "command-eval-schema",
                f"unknown scenario fields: {', '.join(unknown)}",
            )
        )

    raw_role = data.get("role")
    try:
        role = CommandEvalRole(raw_role) if isinstance(raw_role, str) else None
    except ValueError:
        role = None
    if role is None:
        findings.append(
            CommandEvalFinding(
                label,
                "command-eval-role",
                f"unknown command evaluation role: {raw_role!r}",
            )
        )

    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip() or prompt != prompt.strip():
        findings.append(
            CommandEvalFinding(
                label,
                "command-eval-prompt",
                "scenario prompt must be non-empty and trimmed",
            )
        )

    assertions = data.get("assertions")
    contains: tuple[str, ...] | None = None
    excludes: tuple[str, ...] | None = None
    if isinstance(assertions, dict) and all(isinstance(key, str) for key in assertions):
        typed_assertions = cast(dict[str, object], assertions)
        if set(typed_assertions) == _ASSERTION_FIELDS:
            contains = _string_list(typed_assertions.get("output_contains"))
            excludes = _string_list(typed_assertions.get("output_not_contains"))
    if contains is None or excludes is None:
        findings.append(
            CommandEvalFinding(
                label,
                "command-eval-assertions",
                "assertions require non-empty unique output_contains and output_not_contains lists",
            )
        )

    providers: tuple[CommandProvider, ...] = ()
    raw_providers = data.get("providers")
    if role is not None and role.value in _PROVIDER_ROLES:
        values = _string_list(raw_providers)
        try:
            providers = (
                tuple(CommandProvider(value) for value in values)
                if values is not None
                else ()
            )
        except ValueError:
            providers = ()
        expected = _provider_contract(route, role)
        if providers != expected:
            findings.append(
                CommandEvalFinding(
                    label,
                    "command-eval-providers",
                    "providers must equal route-aware matrix: "
                    + ", ".join(provider.value for provider in expected),
                )
            )
    elif raw_providers is not None:
        findings.append(
            CommandEvalFinding(
                label,
                "command-eval-providers",
                "providers are allowed only on provider-matrix scenarios",
            )
        )

    if (
        findings
        or role is None
        or not isinstance(prompt, str)
        or contains is None
        or excludes is None
    ):
        return None, findings
    return (
        CommandEvalScenario(role, prompt, providers, contains, excludes),
        [],
    )


def _load_spec(
    root: Path, path: Path, command: CommandSpec
) -> tuple[CommandEvalSpec | None, list[CommandEvalFinding]]:
    relative = _relative(root, path)
    try:
        data = _mapping(path)
    except _EvalSourceError as error:
        return None, [CommandEvalFinding(relative, error.code, str(error))]
    findings: list[CommandEvalFinding] = []
    unknown = sorted(set(data) - _TOP_LEVEL_FIELDS)
    if unknown:
        findings.append(
            CommandEvalFinding(
                relative,
                "command-eval-schema",
                f"unknown eval fields: {', '.join(unknown)}",
            )
        )
    if data.get("command") != command.name:
        findings.append(
            CommandEvalFinding(
                relative,
                "command-eval-command",
                f"command must equal directory and source slug {command.name!r}",
            )
        )
    if data.get("schemaVersion") != "1.0":
        findings.append(
            CommandEvalFinding(
                relative,
                "command-eval-schema",
                "schemaVersion must be exact supported version '1.0'",
            )
        )
    raw_scenarios = data.get("scenarios")
    scenarios: list[CommandEvalScenario] = []
    observed_roles: list[CommandEvalRole] = []
    if not isinstance(raw_scenarios, list):
        findings.append(
            CommandEvalFinding(
                relative, "command-eval-schema", "scenarios must be an array"
            )
        )
    else:
        for index, raw in enumerate(raw_scenarios):
            if isinstance(raw, dict):
                raw_role = raw.get("role")
                if isinstance(raw_role, str) and raw_role in CommandEvalRole:
                    observed_roles.append(CommandEvalRole(raw_role))
            scenario, scenario_findings = _scenario(relative, index, raw, command.route)
            findings.extend(scenario_findings)
            if scenario is not None:
                scenarios.append(scenario)
    if tuple(observed_roles) != tuple(CommandEvalRole):
        findings.append(
            CommandEvalFinding(
                relative,
                "command-eval-coverage",
                "scenarios must contain each required role exactly once in canonical order",
            )
        )
    prompts = tuple(scenario.prompt for scenario in scenarios)
    if len(prompts) != len(set(prompts)):
        findings.append(
            CommandEvalFinding(
                relative, "command-eval-prompt", "scenario prompts must be unique"
            )
        )
    return (
        None if findings else CommandEvalSpec(path, command.name, tuple(scenarios)),
        findings,
    )


def audit_command_evals(
    root: Path, commands: tuple[CommandSpec, ...]
) -> CommandEvalAudit:
    """Discover strict command suites and require exact command coverage."""

    eval_root = root / "evals" / "commands"
    if eval_root.is_symlink() or not eval_root.is_dir():
        return CommandEvalAudit(
            (),
            (
                CommandEvalFinding(
                    _relative(root, eval_root),
                    "command-eval-directory",
                    "command eval root must be a physical directory",
                ),
            ),
        )
    by_name = {command.name: command for command in commands}
    findings: list[CommandEvalFinding] = []
    specs: list[CommandEvalSpec] = []
    seen: set[str] = set()
    try:
        entries = sorted(eval_root.iterdir(), key=lambda item: item.name)
    except OSError as error:
        return CommandEvalAudit(
            (),
            (
                CommandEvalFinding(
                    _relative(root, eval_root), "command-eval-source", str(error)
                ),
            ),
        )
    for directory in entries:
        relative = _relative(root, directory)
        try:
            metadata = directory.lstat()
        except OSError as error:
            findings.append(
                CommandEvalFinding(relative, "command-eval-source", str(error))
            )
            continue
        if (
            directory.is_symlink()
            or not stat.S_ISDIR(metadata.st_mode)
            or directory.name not in by_name
        ):
            findings.append(
                CommandEvalFinding(
                    relative,
                    "command-eval-layout",
                    "suite must be a physical directory for one canonical command",
                )
            )
            continue
        files = tuple(sorted(directory.iterdir(), key=lambda item: item.name))
        if len(files) != 1 or files[0].name != "eval.yaml" or files[0].is_symlink():
            findings.append(
                CommandEvalFinding(
                    relative,
                    "command-eval-layout",
                    "suite must contain only one physical eval.yaml",
                )
            )
            continue
        seen.add(directory.name)
        spec, spec_findings = _load_spec(root, files[0], by_name[directory.name])
        findings.extend(spec_findings)
        if spec is not None:
            specs.append(spec)
    for missing in sorted(set(by_name) - seen):
        findings.append(
            CommandEvalFinding(
                f"evals/commands/{missing}/eval.yaml",
                "command-eval-missing",
                f"missing command evaluation suite for {missing}",
            )
        )
    return CommandEvalAudit(tuple(specs), tuple(findings))


__all__ = (
    "CommandEvalAudit",
    "CommandEvalFinding",
    "CommandEvalRole",
    "CommandEvalScenario",
    "CommandEvalSpec",
    "audit_command_evals",
)
