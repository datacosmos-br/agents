"""Strict Waza specification, model, and complete live-corpus owners."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from functools import partial
from pathlib import Path
from typing import cast

import yaml

from .atomic_io import discard_physical_file, stage_text
from .cleanup import remove_physical, run_cleanup, run_with_cleanup


class EvalRole(StrEnum):
    HAPPY_PATH = "happy_path"
    FAIL_CLOSED = "fail_closed"
    SHOULD_NOT_TRIGGER = "should_not_trigger"


TASK_ROLES = {
    "basic-usage.yaml": EvalRole.HAPPY_PATH,
    "edge-case.yaml": EvalRole.FAIL_CLOSED,
    "should-not-trigger.yaml": EvalRole.SHOULD_NOT_TRIGGER,
}
_CONFIG_FIELDS = frozenset(
    {
        "executor",
        "fail_fast",
        "max_attempts",
        "model",
        "parallel",
        "required_skills",
        "skill_directories",
        "timeout_seconds",
        "trials_per_task",
    }
)


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
    model: str
    executor: str
    trials_per_task: int
    max_attempts: int
    fail_fast: bool
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


def _nonnegative_integer(
    mapping: dict[str, object], key: str, path: Path, field: str
) -> int:
    value = _required(mapping, key, path, field)
    if type(value) is not int or value < 0:
        raise TypeError(f"{path}: {field}.{key} must be a non-negative integer")
    return value


def _boolean(mapping: dict[str, object], key: str, path: Path, field: str) -> bool:
    value = _required(mapping, key, path, field)
    if type(value) is not bool:
        raise TypeError(f"{path}: {field}.{key} must be a boolean")
    return value


def _exact_fields(
    value: dict[str, object], expected: frozenset[str], path: Path, field: str
) -> None:
    if frozenset(value) != expected:
        raise ValueError(
            f"{path}: {field} fields must equal {', '.join(sorted(expected))}"
        )


def _load_mapping(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Waza source must be a physical file: {path}")
    return _mapping(yaml.safe_load(path.read_text(encoding="utf-8")), path, "document")


def _task(path: Path, role: EvalRole) -> EvalTaskSpec:
    payload = _load_mapping(path)
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
        role,
        _string(payload, "id", path, "document"),
        prompt,
        tuple(fixtures),
        _strings(expected, "output_contains", path, "expected"),
        _strings(expected, "output_not_contains", path, "expected"),
        tuple(outcomes),
    )


def _eval_suite(path: Path, tasks: tuple[tuple[Path, EvalRole], ...]) -> EvalSuiteSpec:
    payload = _load_mapping(path)
    settings = _mapping(_required(payload, "config", path, "document"), path, "config")
    _exact_fields(settings, _CONFIG_FIELDS, path, "config")
    trials = _integer(settings, "trials_per_task", path, "config")
    if trials != 1:
        raise ValueError(f"{path}: config.trials_per_task must equal 1")
    if _boolean(settings, "parallel", path, "config"):
        raise ValueError(f"{path}: config.parallel must be false")
    attempts = _nonnegative_integer(settings, "max_attempts", path, "config")
    if attempts != 0:
        raise ValueError(f"{path}: config.max_attempts must equal 0")
    fail_fast = _boolean(settings, "fail_fast", path, "config")
    if not fail_fast:
        raise ValueError(f"{path}: config.fail_fast must be true")
    executor = _string(settings, "executor", path, "config")
    if executor != "copilot-sdk":
        raise ValueError(f"{path}: config.executor must equal copilot-sdk")
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
    return EvalSuiteSpec(
        path,
        _string(payload, "skill", path, "document"),
        _strings(settings, "required_skills", path, "config"),
        _strings(settings, "skill_directories", path, "config"),
        _string(settings, "model", path, "config"),
        executor,
        trials,
        attempts,
        fail_fast,
        _integer(settings, "timeout_seconds", path, "config"),
        tuple(graders),
        tuple(_task(task_path, role) for task_path, role in tasks),
    )


def load_eval_suite(directory: Path) -> EvalSuiteSpec:
    """Load one complete suite or raise on the first schema defect."""

    path = directory / "eval.yaml"
    task_root = directory / "tasks"
    if task_root.is_symlink() or not task_root.is_dir():
        raise ValueError(f"Waza task root must be a physical directory: {task_root}")
    task_paths = tuple(sorted(task_root.glob("*.yaml")))
    if tuple(task.name for task in task_paths) != tuple(sorted(TASK_ROLES)):
        raise ValueError(
            f"{task_root}: task files must equal {tuple(sorted(TASK_ROLES))}"
        )
    return _eval_suite(
        path, tuple((task, TASK_ROLES[task.name]) for task in task_paths)
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


def _preflight_suite(root: Path) -> EvalSuiteSpec:
    directory = root / "config" / "waza" / "preflight"
    task_root = directory / "tasks"
    if task_root.is_symlink() or not task_root.is_dir():
        raise ValueError(f"Waza task root must be a physical directory: {task_root}")
    task_paths = tuple(sorted(task_root.glob("*.yaml")))
    if tuple(task.name for task in task_paths) != ("tool-read.yaml",):
        raise ValueError(f"{task_root}: preflight task files must equal tool-read.yaml")
    return _eval_suite(directory / "eval.yaml", ((task_paths[0], EvalRole.HAPPY_PATH),))


def _run_artifact(
    path: Path,
    model: str,
    suite: EvalSuiteSpec,
    *,
    require_tool_call: bool,
) -> dict[str, object]:
    payload = _json_object(path)
    if payload.get("schemaVersion") != "1.2":
        raise ValueError(f"{path}: schemaVersion must equal 1.2")
    if payload.get("skill") != suite.skill:
        raise ValueError(f"{path}: artifact skill does not match {suite.skill}")
    config = _mapping(_required(payload, "config", path, "artifact"), path, "config")
    if config.get("model_id") != model:
        raise ValueError(f"{path}: artifact model does not match {model}")
    if config.get("engine_type") != suite.executor:
        raise ValueError(f"{path}: artifact executor does not match {suite.executor}")
    summary = _mapping(_required(payload, "summary", path, "artifact"), path, "summary")
    raw_tasks = _required(payload, "tasks", path, "artifact")
    expected_count = len(suite.tasks)
    if not isinstance(raw_tasks, list) or len(raw_tasks) != expected_count:
        raise ValueError(f"{path}: artifact task inventory is incomplete")
    if (
        summary.get("total_tests") != expected_count
        or summary.get("succeeded") != expected_count
        or summary.get("failed") != 0
        or summary.get("errors") != 0
        or summary.get("skipped") != 0
    ):
        raise ValueError(f"{path}: artifact summary is not fully successful")
    expected_tasks = {task.identifier: task for task in suite.tasks}
    observed_tasks: dict[str, dict[str, object]] = {}
    for index, raw_task in enumerate(cast(list[object], raw_tasks)):
        task = _mapping(raw_task, path, f"tasks[{index}]")
        identifier = task.get("test_id")
        if not isinstance(identifier, str) or identifier not in expected_tasks:
            raise ValueError(f"{path}: artifact contains an unknown task")
        if identifier in observed_tasks:
            raise ValueError(
                f"{path}: artifact contains a duplicate task: {identifier}"
            )
        observed_tasks[identifier] = task
    if set(observed_tasks) != set(expected_tasks):
        raise ValueError(f"{path}: artifact task inventory differs from the suite")
    grader_names = {grader.name for grader in suite.graders}
    for identifier, expected_task in expected_tasks.items():
        task = observed_tasks[identifier]
        if task.get("status") not in {"passed", "succeeded"}:
            raise ValueError(f"{path}: task did not succeed: {identifier}")
        raw_runs = _required(task, "runs", path, f"task {identifier}")
        if not isinstance(raw_runs, list) or len(raw_runs) != suite.trials_per_task:
            raise ValueError(f"{path}: task run inventory differs: {identifier}")
        for run_index, raw_run in enumerate(cast(list[object], raw_runs)):
            label = f"task {identifier}.runs[{run_index}]"
            run = _mapping(raw_run, path, label)
            if (
                run.get("status") not in {"passed", "succeeded"}
                or run.get("error_msg")
                or run.get("attempts") != 1
            ):
                raise ValueError(f"{path}: task run did not succeed: {identifier}")
            validations = _mapping(
                _required(run, "validations", path, label),
                path,
                f"{label}.validations",
            )
            required_graders = set(grader_names)
            if expected_task.output_contains:
                required_graders.add("_output_contains")
            if expected_task.output_not_contains:
                required_graders.add("_output_not_contains")
            if not required_graders.issubset(validations):
                raise ValueError(f"{path}: task graders are incomplete: {identifier}")
            for name, raw_validation in validations.items():
                validation = _mapping(
                    raw_validation, path, f"{label}.validations.{name}"
                )
                if validation.get("passed") is not True:
                    raise ValueError(
                        f"{path}: task grader did not pass: {identifier}/{name}"
                    )
            output = _required(run, "final_output", path, label)
            if not isinstance(output, str) or not output.strip():
                raise ValueError(f"{path}: task final output is empty: {identifier}")
            digest = _mapping(
                _required(run, "session_digest", path, label),
                path,
                f"{label}.session_digest",
            )
            calls = _required(digest, "tool_call_count", path, "session_digest")
            if type(calls) is not int or calls < int(require_tool_call):
                raise ValueError(f"{path}: required tool call was not proven")
    return payload


def run_live_corpus(
    root: Path,
    model: str,
    suites: tuple[EvalSuiteSpec, ...],
    executable: str,
    *,
    runner: WazaRunner,
) -> Path:
    """Run preflight plus every live suite and publish one complete result set."""

    if not model or model != model.strip():
        raise ValueError("Waza live model must be non-empty and trimmed")
    if not executable or executable != executable.strip():
        raise ValueError("Waza executable must be non-empty and trimmed")
    if not suites:
        raise ValueError("Waza live corpus must contain at least one skill suite")
    preflight = _preflight_suite(root)
    all_suites = (preflight, *suites)
    identities = tuple((suite.path, suite.skill) for suite in all_suites)
    if len(identities) != len(set(identities)):
        raise ValueError("Waza live corpus contains duplicate suites")
    for suite in all_suites:
        if suite.model != model:
            raise ValueError(f"{suite.path}: suite model does not match {model}")

    repository = root.resolve(strict=True)
    results = repository / "results"
    if results.is_symlink() or not results.is_dir():
        raise ValueError(f"Waza results root must be a physical directory: {results}")
    latest = results / "latest"
    if latest.is_symlink() or (latest.exists() and not latest.is_dir()):
        raise ValueError(f"Waza latest result must be a physical directory: {latest}")
    destination = latest / "results.json"
    if destination.is_symlink() or (
        destination.exists() and not stat.S_ISREG(destination.lstat().st_mode)
    ):
        raise ValueError(f"Waza destination must be a physical file: {destination}")

    created_latest = not latest.exists()
    if created_latest:
        latest.mkdir(mode=0o700)
    stage = Path(tempfile.mkdtemp(prefix=".waza-live-stage.", dir=results))
    candidate: Path | None = None

    def cleanup() -> None:
        actions: list[Callable[[], None]] = []
        candidate_path = candidate
        if candidate_path is not None and (
            candidate_path.exists() or candidate_path.is_symlink()
        ):
            actions.append(partial(discard_physical_file, candidate_path))
        if stage.exists() or stage.is_symlink():
            actions.append(partial(remove_physical, stage))
        if created_latest and latest.exists():
            actions.append(latest.rmdir)
        run_cleanup(tuple(actions))

    def operation() -> Path:
        nonlocal candidate
        artifacts: list[dict[str, object]] = []
        for index, suite in enumerate(all_suites):
            output = stage / f"{index:03d}-{suite.skill}.json"
            runner(
                (
                    executable,
                    "run",
                    str(suite.path),
                    "--model",
                    model,
                    "--output",
                    str(output),
                ),
                repository,
            )
            artifacts.append(
                _run_artifact(
                    output,
                    model,
                    suite,
                    require_tool_call=suite is preflight,
                )
            )
        aggregate = {
            "schemaVersion": "1.0",
            "model": model,
            "suite_count": len(all_suites),
            "task_count": sum(len(suite.tasks) for suite in all_suites),
            "artifacts": artifacts,
        }
        candidate = stage_text(
            destination,
            json.dumps(aggregate, indent=2, sort_keys=True) + "\n",
            mode=0o600,
        )
        candidate.chmod(0o600)
        remove_physical(stage)
        os.replace(candidate, destination)
        candidate = None
        return destination

    return run_with_cleanup(operation, cleanup)


__all__ = (
    "EvalGraderSpec",
    "EvalRole",
    "EvalSuiteSpec",
    "EvalTaskSpec",
    "WazaRunner",
    "default_model",
    "load_eval_suite",
    "require_model_projection",
    "run_live_corpus",
)
