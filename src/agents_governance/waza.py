"""Strict Waza specification, model, and live-preflight owners."""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import cast

import yaml

from .atomic_io import discard_physical_file, stage_text
from .cleanup import run_with_cleanup


class EvalRole(StrEnum):
    HAPPY_PATH = "happy_path"
    FAIL_CLOSED = "fail_closed"
    SHOULD_NOT_TRIGGER = "should_not_trigger"


TASK_ROLES = {
    "basic-usage.yaml": EvalRole.HAPPY_PATH,
    "edge-case.yaml": EvalRole.FAIL_CLOSED,
    "should-not-trigger.yaml": EvalRole.SHOULD_NOT_TRIGGER,
}


@dataclass(frozen=True)
class EvalGraderSpec:
    kind: str
    name: str
    prompt: str | None
    max_duration_ms: int | None


@dataclass(frozen=True)
class EvalTaskSpec:
    path: Path
    role: EvalRole
    identifier: str
    prompt: str
    fixture_paths: tuple[str, ...]
    output_contains: tuple[str, ...]
    output_not_contains: tuple[str, ...]
    outcomes: tuple[str, ...]


@dataclass(frozen=True)
class EvalSuiteSpec:
    path: Path
    skill: str
    required_skills: tuple[str, ...]
    skill_directories: tuple[str, ...]
    timeout_seconds: int
    graders: tuple[EvalGraderSpec, ...]
    tasks: tuple[EvalTaskSpec, ...]


WazaRunner = Callable[[Sequence[str], Path], None]


def _mapping(value: object, path: Path, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{path}: {field} must be a mapping")
    raw = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in raw):
        raise TypeError(f"{path}: {field} keys must be strings")
    return cast(dict[str, object], raw)


def _required(mapping: dict[str, object], key: str, path: Path, field: str) -> object:
    if key not in mapping:
        raise ValueError(f"{path}: {field}.{key} is required")
    return mapping[key]


def _string(mapping: dict[str, object], key: str, path: Path, field: str) -> str:
    value = _required(mapping, key, path, field)
    if not isinstance(value, str) or value != value.strip() or not value:
        raise TypeError(f"{path}: {field}.{key} must be a non-empty trimmed string")
    return value


def _strings(
    mapping: dict[str, object], key: str, path: Path, field: str
) -> tuple[str, ...]:
    if key not in mapping:
        return ()
    value = mapping[key]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"{path}: {field}.{key} must be a string array")
    return tuple(cast(list[str], value))


def _integer(mapping: dict[str, object], key: str, path: Path, field: str) -> int:
    value = _required(mapping, key, path, field)
    if type(value) is not int or value <= 0:
        raise TypeError(f"{path}: {field}.{key} must be a positive integer")
    return value


def _load_mapping(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Waza source must be a physical file: {path}")
    return _mapping(yaml.safe_load(path.read_text(encoding="utf-8")), path, "document")


def _task(path: Path) -> EvalTaskSpec:
    payload = _load_mapping(path)
    if path.name not in TASK_ROLES:
        raise ValueError(f"{path}: unsupported task role filename")
    inputs = _mapping(_required(payload, "inputs", path, "document"), path, "inputs")
    expected = _mapping(
        _required(payload, "expected", path, "document"), path, "expected"
    )
    raw_files: object = []
    if "files" in inputs:
        raw_files = inputs["files"]
    if not isinstance(raw_files, list):
        raise TypeError(f"{path}: inputs.files must be an array")
    fixtures: list[str] = []
    for index, raw_file in enumerate(cast(list[object], raw_files)):
        file_spec = _mapping(raw_file, path, f"inputs.files[{index}]")
        fixtures.append(_string(file_spec, "path", path, f"inputs.files[{index}]"))
    raw_outcomes: object = []
    if "outcomes" in expected:
        raw_outcomes = expected["outcomes"]
    if not isinstance(raw_outcomes, list):
        raise TypeError(f"{path}: expected.outcomes must be an array")
    outcomes: list[str] = []
    for index, raw_outcome in enumerate(cast(list[object], raw_outcomes)):
        outcome = _mapping(raw_outcome, path, f"expected.outcomes[{index}]")
        outcomes.append(_string(outcome, "type", path, f"expected.outcomes[{index}]"))
    prompt = _required(inputs, "prompt", path, "inputs")
    if not isinstance(prompt, str):
        raise TypeError(f"{path}: inputs.prompt must be a string")
    return EvalTaskSpec(
        path,
        TASK_ROLES[path.name],
        _string(payload, "id", path, "document"),
        prompt,
        tuple(fixtures),
        _strings(expected, "output_contains", path, "expected"),
        _strings(expected, "output_not_contains", path, "expected"),
        tuple(outcomes),
    )


def load_eval_suite(directory: Path) -> EvalSuiteSpec:
    """Load one complete suite or raise on the first schema defect."""

    path = directory / "eval.yaml"
    payload = _load_mapping(path)
    settings = _mapping(_required(payload, "config", path, "document"), path, "config")
    declared_tasks = _required(payload, "tasks", path, "document")
    if declared_tasks != ["tasks/*.yaml"]:
        raise ValueError(f"{path}: tasks must equal ['tasks/*.yaml']")
    raw_graders = _required(payload, "graders", path, "document")
    if not isinstance(raw_graders, list) or not raw_graders:
        raise TypeError(f"{path}: graders must be a non-empty array")
    graders: list[EvalGraderSpec] = []
    for index, raw_grader in enumerate(cast(list[object], raw_graders)):
        field = f"graders[{index}]"
        grader = _mapping(raw_grader, path, field)
        config = _mapping(
            _required(grader, "config", path, field), path, f"{field}.config"
        )
        prompt: str | None = None
        if "prompt" in config:
            prompt = _string(config, "prompt", path, f"{field}.config")
        duration: int | None = None
        if "max_duration_ms" in config:
            duration = _integer(config, "max_duration_ms", path, f"{field}.config")
        graders.append(
            EvalGraderSpec(
                _string(grader, "type", path, field),
                _string(grader, "name", path, field),
                prompt,
                duration,
            )
        )
    task_root = directory / "tasks"
    if task_root.is_symlink() or not task_root.is_dir():
        raise ValueError(f"Waza task root must be a physical directory: {task_root}")
    task_paths = tuple(sorted(task_root.glob("*.yaml")))
    if tuple(path.name for path in task_paths) != tuple(sorted(TASK_ROLES)):
        raise ValueError(
            f"{task_root}: task files must equal {tuple(sorted(TASK_ROLES))}"
        )
    return EvalSuiteSpec(
        path,
        _string(payload, "skill", path, "document"),
        _strings(settings, "required_skills", path, "config"),
        _strings(settings, "skill_directories", path, "config"),
        _integer(settings, "timeout_seconds", path, "config"),
        tuple(graders),
        tuple(_task(task_path) for task_path in task_paths),
    )


def default_model(root: Path) -> str:
    """Return the exact project-owned model without an implicit default."""

    path = root / ".waza.yaml"
    payload = _load_mapping(path)
    defaults = _mapping(
        _required(payload, "defaults", path, "document"), path, "defaults"
    )
    return _string(defaults, "model", path, "defaults")


def require_model_projection(root: Path) -> str:
    """Require every materialized eval to use the exact project model."""

    expected = default_model(root)
    eval_root = root / "evals"
    if eval_root.is_symlink() or not eval_root.is_dir():
        raise ValueError(f"Waza eval root must be a physical directory: {eval_root}")
    paths = sorted(eval_root.glob("*/eval.yaml"))
    preflight = root / "config" / "waza" / "preflight" / "eval.yaml"
    if preflight.is_symlink() or not preflight.is_file():
        raise ValueError(f"Waza preflight must be a physical file: {preflight}")
    paths.append(preflight)
    if not paths:
        raise ValueError(f"Waza eval inventory is empty: {eval_root}")
    for path in paths:
        payload = _load_mapping(path)
        config = _mapping(
            _required(payload, "config", path, "document"), path, "config"
        )
        actual = _string(config, "model", path, "config")
        if actual != expected:
            raise ValueError(f"{path}: model {actual!r} != project owner {expected!r}")
    return expected


def _json_object(path: Path) -> dict[str, object]:
    if path.is_symlink() or not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError(f"Waza artifact must be a physical file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _mapping(payload, path, "artifact")


def _run_artifact(path: Path, model: str) -> None:
    payload = _json_object(path)
    if payload.get("schemaVersion") != "1.2":
        raise ValueError(f"{path}: schemaVersion must equal 1.2")
    config = _mapping(_required(payload, "config", path, "artifact"), path, "config")
    if config.get("model_id") != model:
        raise ValueError(f"{path}: artifact model does not match {model}")
    summary = _mapping(_required(payload, "summary", path, "artifact"), path, "summary")
    tasks = _required(payload, "tasks", path, "artifact")
    if not isinstance(tasks, list) or len(tasks) != 1:
        raise ValueError(f"{path}: preflight must contain exactly one task")
    if (
        summary.get("total_tests") != 1
        or summary.get("succeeded") != 1
        or summary.get("failed") != 0
        or summary.get("errors") != 0
        or summary.get("skipped") != 0
    ):
        raise ValueError(f"{path}: preflight summary is not fully successful")
    task = _mapping(tasks[0], path, "tasks[0]")
    if task.get("status") not in {"passed", "succeeded"}:
        raise ValueError(f"{path}: preflight task did not succeed")
    runs = _required(task, "runs", path, "tasks[0]")
    if not isinstance(runs, list) or len(runs) != 1:
        raise ValueError(f"{path}: preflight task must contain one run")
    run = _mapping(runs[0], path, "tasks[0].runs[0]")
    if run.get("status") not in {"passed", "succeeded"} or run.get("error_msg"):
        raise ValueError(f"{path}: preflight run did not succeed")
    digest = _mapping(
        _required(run, "session_digest", path, "tasks[0].runs[0]"),
        path,
        "tasks[0].runs[0].session_digest",
    )
    calls = _required(digest, "tool_call_count", path, "session_digest")
    if type(calls) is not int or calls < 1:
        raise ValueError(f"{path}: preflight did not prove a tool call")
    output = _required(run, "final_output", path, "tasks[0].runs[0]")
    if not isinstance(output, str) or not output.strip():
        raise ValueError(f"{path}: preflight final output is empty")


def _publication(root: Path, destination: Path) -> None:
    repository = root.resolve(strict=True)
    destination.absolute().relative_to(repository)
    current = repository
    for part in destination.absolute().relative_to(repository).parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"Waza publication path contains symlink: {current}")
    if not destination.parent.is_dir():
        raise ValueError(f"Waza publication parent is missing: {destination.parent}")
    if destination.exists() and not stat.S_ISREG(destination.lstat().st_mode):
        raise ValueError(f"Waza destination must be a regular file: {destination}")


def run_preflight(root: Path, *, runner: WazaRunner) -> Path:
    """Run and atomically publish one fresh, completely valid live artifact."""

    model = require_model_projection(root)
    eval_path = root / "config" / "waza" / "preflight" / "eval.yaml"
    destination = root / "results" / "preflight" / "results.json"
    _publication(root, destination)
    candidate = stage_text(destination, "", mode=0o600)

    def operation() -> Path:
        runner(
            (
                "waza",
                "run",
                str(eval_path),
                "--model",
                model,
                "--output",
                str(candidate),
            ),
            root,
        )
        _run_artifact(candidate, model)
        os.replace(candidate, destination)
        return destination

    return run_with_cleanup(operation, lambda: discard_physical_file(candidate))


__all__ = (
    "EvalGraderSpec",
    "EvalRole",
    "EvalSuiteSpec",
    "EvalTaskSpec",
    "WazaRunner",
    "default_model",
    "load_eval_suite",
    "require_model_projection",
    "run_preflight",
)
