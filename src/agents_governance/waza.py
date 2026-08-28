"""Canonical Waza model configuration and eval-spec projection."""

from __future__ import annotations

import json
import math
import os
import stat
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Any, cast

import yaml

from .atomic_io import discard_physical_file, stage_text
from .temp import run_command


@dataclass(frozen=True)
class WazaConfigFinding:
    """One eval specification that diverges from the project model owner."""

    path: Path
    actual: str | None
    expected: str


class EvalRole(StrEnum):
    """Required semantic role of one Waza task."""

    HAPPY_PATH = "happy_path"
    FAIL_CLOSED = "fail_closed"
    SHOULD_NOT_TRIGGER = "should_not_trigger"


TASK_ROLES: dict[str, EvalRole] = {
    "basic-usage.yaml": EvalRole.HAPPY_PATH,
    "edge-case.yaml": EvalRole.FAIL_CLOSED,
    "should-not-trigger.yaml": EvalRole.SHOULD_NOT_TRIGGER,
}


@dataclass(frozen=True)
class EvalGraderSpec:
    """Typed subset of a grader needed by the deterministic gate."""

    kind: str | None
    name: str | None
    prompt: str | None
    max_duration_ms: int | None


@dataclass(frozen=True)
class EvalTaskSpec:
    """Typed task contract consumed by deterministic validation."""

    path: Path
    role: EvalRole | None
    identifier: str | None
    prompt: str | None
    fixture_paths: tuple[str, ...]
    output_contains: tuple[str, ...]
    output_not_contains: tuple[str, ...]
    outcomes: tuple[str, ...]


@dataclass(frozen=True)
class EvalSuiteSpec:
    """Typed suite contract consumed by deterministic validation."""

    path: Path
    skill: str | None
    required_skills: tuple[str, ...]
    skill_directories: tuple[str, ...]
    timeout_seconds: int | None
    graders: tuple[EvalGraderSpec, ...]
    tasks: tuple[EvalTaskSpec, ...]


class EvalSpecError(ValueError):
    """A Waza specification cannot be parsed without guessing."""

    def __init__(self, path: Path, message: str) -> None:
        super().__init__(message)
        self.path = path


def _mapping(value: Any, path: Path, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvalSpecError(path, f"{field} must be a mapping")
    return cast(dict[str, Any], value)


def _optional_strings(value: Any, path: Path, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise EvalSpecError(path, f"{field} must be a list of strings")
    return tuple(cast(list[str], value))


def _load_mapping(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise EvalSpecError(path, str(error)) from error
    return _mapping(payload, path, "document")


def _load_task(path: Path) -> EvalTaskSpec:
    payload = _load_mapping(path)
    inputs = _mapping(payload.get("inputs"), path, "inputs")
    expected = _mapping(payload.get("expected"), path, "expected")
    raw_files = inputs.get("files", [])
    if not isinstance(raw_files, list):
        raise EvalSpecError(path, "inputs.files must be a list")
    fixture_paths: list[str] = []
    for index, raw_file in enumerate(raw_files):
        file_spec = _mapping(raw_file, path, f"inputs.files[{index}]")
        fixture_path = file_spec.get("path")
        if not isinstance(fixture_path, str) or not fixture_path.strip():
            raise EvalSpecError(path, f"inputs.files[{index}].path must be a string")
        fixture_paths.append(fixture_path)
    raw_outcomes = expected.get("outcomes", [])
    if not isinstance(raw_outcomes, list):
        raise EvalSpecError(path, "expected.outcomes must be a list")
    outcomes: list[str] = []
    for index, raw_outcome in enumerate(raw_outcomes):
        outcome = _mapping(raw_outcome, path, f"expected.outcomes[{index}]")
        outcome_type = outcome.get("type")
        if not isinstance(outcome_type, str) or not outcome_type.strip():
            raise EvalSpecError(
                path, f"expected.outcomes[{index}].type must be a string"
            )
        outcomes.append(outcome_type)
    identifier = payload.get("id")
    prompt = inputs.get("prompt")
    return EvalTaskSpec(
        path=path,
        role=TASK_ROLES.get(path.name),
        identifier=identifier if isinstance(identifier, str) else None,
        prompt=prompt if isinstance(prompt, str) else None,
        fixture_paths=tuple(fixture_paths),
        output_contains=_optional_strings(
            expected.get("output_contains"), path, "expected.output_contains"
        ),
        output_not_contains=_optional_strings(
            expected.get("output_not_contains"), path, "expected.output_not_contains"
        ),
        outcomes=tuple(outcomes),
    )


def load_eval_suite(directory: Path) -> EvalSuiteSpec:
    """Load one suite into immutable typed models without accepting weak defaults."""

    path = directory / "eval.yaml"
    payload = _load_mapping(path)
    settings = _mapping(payload.get("config"), path, "config")
    raw_graders = payload.get("graders")
    if not isinstance(raw_graders, list):
        raise EvalSpecError(path, "graders must be a list")
    graders: list[EvalGraderSpec] = []
    for index, raw_grader in enumerate(raw_graders):
        grader = _mapping(raw_grader, path, f"graders[{index}]")
        grader_config = _mapping(
            grader.get("config", {}), path, f"graders[{index}].config"
        )
        kind = grader.get("type")
        grader_name = grader.get("name")
        prompt = grader_config.get("prompt")
        max_duration = grader_config.get("max_duration_ms")
        graders.append(
            EvalGraderSpec(
                kind=kind if isinstance(kind, str) else None,
                name=grader_name if isinstance(grader_name, str) else None,
                prompt=prompt if isinstance(prompt, str) else None,
                max_duration_ms=(
                    max_duration
                    if isinstance(max_duration, int)
                    and not isinstance(max_duration, bool)
                    else None
                ),
            )
        )
    timeout = settings.get("timeout_seconds")
    skill = payload.get("skill")
    return EvalSuiteSpec(
        path=path,
        skill=skill if isinstance(skill, str) else None,
        required_skills=_optional_strings(
            settings.get("required_skills"), path, "config.required_skills"
        ),
        skill_directories=_optional_strings(
            settings.get("skill_directories"), path, "config.skill_directories"
        ),
        timeout_seconds=(
            timeout
            if isinstance(timeout, int) and not isinstance(timeout, bool)
            else None
        ),
        graders=tuple(graders),
        tasks=tuple(
            _load_task(task) for task in sorted((directory / "tasks").glob("*.yaml"))
        ),
    )


class PreflightExit(IntEnum):
    """Stable exit contract for the live Waza transport gate."""

    AVAILABLE = 0
    MODEL_UNAVAILABLE = 20
    AUTH_INVALID = 21
    TRANSPORT_INVALID = 22
    EVAL_FAILED = 23
    INVALID_ARTIFACT = 24


@dataclass(frozen=True)
class PreflightResult:
    """Classified live Waza result."""

    status: PreflightExit
    message: str


WazaRunner = Callable[[Sequence[str], Path], int]


class WazaArtifactError(ValueError):
    """A Waza artifact cannot prove the operation's success contract."""


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def _require_regular_file(path: Path, purpose: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise WazaArtifactError(f"{purpose} is unavailable: {path}: {error}") from error
    if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise WazaArtifactError(f"{purpose} must be a regular physical file: {path}")
    if metadata.st_size == 0:
        raise WazaArtifactError(f"{purpose} is empty: {path}")


def _load_json_artifact(path: Path, purpose: str) -> dict[str, Any]:
    _require_regular_file(path, purpose)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise WazaArtifactError(f"invalid {purpose} {path}: {error}") from error
    if not isinstance(payload, dict):
        raise WazaArtifactError(f"{purpose} must be a JSON object: {path}")
    return cast(dict[str, Any], payload)


def validate_model_catalog(root: Path, path: Path) -> str:
    """Require the live OpenAI-compatible catalog to expose only the owner model."""

    expected = default_model(root)
    payload = _load_json_artifact(path, "Waza model catalog")
    data = payload.get("data")
    if not isinstance(data, list):
        raise WazaArtifactError("Waza model catalog data must be a list")
    identifiers: list[str] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise WazaArtifactError(
                f"Waza model catalog data[{index}] must be an object"
            )
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise WazaArtifactError(
                f"Waza model catalog data[{index}].id must be a non-empty string"
            )
        identifiers.append(identifier)
    if identifiers != [expected]:
        rendered = ", ".join(identifiers) if identifiers else "none"
        raise WazaArtifactError(
            f"Waza model catalog must expose only owner model {expected!r}; got {rendered}"
        )
    return expected


def validate_artifact(root: Path, path: Path) -> str:
    """Validate one fresh quality or run artifact against the owner contract."""

    payload = _load_json_artifact(path, "Waza artifact")
    dimensions = payload.get("dimensions")
    if isinstance(dimensions, list) and dimensions:
        names: list[str] = []
        for item in dimensions:
            if not isinstance(item, dict):
                raise WazaArtifactError(
                    "quality artifact contains an invalid dimension"
                )
            name = item.get("name")
            score = item.get("score")
            if not isinstance(name, str) or not name.strip():
                raise WazaArtifactError(
                    "quality artifact contains an unnamed dimension"
                )
            if (
                not isinstance(score, (int, float))
                or isinstance(score, bool)
                or not math.isfinite(score)
                or not 1 <= score <= 5
            ):
                raise WazaArtifactError("quality artifact contains an invalid score")
            names.append(name)
        if len(names) != len(set(names)):
            raise WazaArtifactError("quality artifact contains duplicate dimensions")
        overall_score = payload.get("overall_score")
        if (
            not isinstance(overall_score, (int, float))
            or isinstance(overall_score, bool)
            or not math.isfinite(overall_score)
            or not 1 <= overall_score <= 5
        ):
            raise WazaArtifactError(
                "quality artifact contains an invalid overall score"
            )
        summary = payload.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise WazaArtifactError("quality artifact contains no summary")
        return "quality"
    if payload.get("schemaVersion") != "1.2":
        raise WazaArtifactError("artifact is neither scored quality nor schema 1.2")
    config = payload.get("config")
    summary = payload.get("summary")
    tasks = payload.get("tasks")
    expected_model = default_model(root)
    if not isinstance(config, dict) or config.get("model_id") != expected_model:
        raise WazaArtifactError("run artifact model does not match the project owner")
    if not isinstance(summary, dict) or not isinstance(tasks, list):
        raise WazaArtifactError("run artifact summary or tasks are missing")
    total = summary.get("total_tests")
    if (
        not isinstance(total, int)
        or isinstance(total, bool)
        or total <= 0
        or len(tasks) != total
        or summary.get("succeeded") != total
        or summary.get("failed") != 0
        or summary.get("errors") != 0
        or summary.get("skipped") != 0
    ):
        raise WazaArtifactError("run artifact does not prove every task succeeded")
    for task in tasks:
        if not isinstance(task, dict) or task.get("status") not in {
            "passed",
            "succeeded",
        }:
            raise WazaArtifactError("run artifact contains a non-success task")
        runs = task.get("runs")
        if not isinstance(runs, list) or not runs:
            raise WazaArtifactError("run artifact task has no executions")
        if not all(
            isinstance(run, dict)
            and run.get("status") in {"passed", "succeeded"}
            and not run.get("error_msg")
            for run in runs
        ):
            raise WazaArtifactError("run artifact contains a non-success execution")
    return "run"


def _assert_publication_path(root: Path, path: Path) -> None:
    absolute_root = root.absolute()
    absolute_path = path.absolute()
    try:
        relative = absolute_path.relative_to(absolute_root)
    except ValueError as error:
        raise WazaArtifactError(
            f"Waza artifact publication must remain under {absolute_root}: {path}"
        ) from error
    current = absolute_root
    if current.is_symlink():
        raise WazaArtifactError(f"Waza publication root must not be a symlink: {root}")
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise WazaArtifactError(
                f"Waza artifact publication path contains a symlink: {current}"
            )


def _publish_candidate(root: Path, candidate: Path, destination: Path) -> None:
    _assert_publication_path(root, candidate)
    _assert_publication_path(root, destination)
    if candidate.parent.absolute() != destination.parent.absolute():
        raise WazaArtifactError(
            "Waza candidate and destination must share one publication directory"
        )
    if not destination.parent.is_dir():
        raise WazaArtifactError(
            f"Waza artifact publication directory is missing: {destination.parent}"
        )
    if destination.exists():
        metadata = destination.lstat()
        if not stat.S_ISREG(metadata.st_mode):
            raise WazaArtifactError(
                f"Waza artifact destination must be a regular file: {destination}"
            )
    try:
        os.replace(candidate, destination)
    except OSError as error:
        raise WazaArtifactError(
            f"Waza artifact publication failed: {candidate} -> {destination}: {error}"
        ) from error


def publish_artifact(root: Path, candidate: Path, destination: Path) -> str:
    """Atomically publish a validated destination-local Waza candidate."""

    artifact_kind = validate_artifact(root, candidate)
    _publish_candidate(root, candidate, destination)
    return artifact_kind


def classify_preflight(path: Path, expected_model: str) -> PreflightResult:
    """Validate and classify one Waza schema 1.2 preflight artifact."""

    try:
        payload = _load_json_artifact(path, "Waza preflight artifact")
    except WazaArtifactError as error:
        return PreflightResult(PreflightExit.INVALID_ARTIFACT, str(error))
    if payload.get("schemaVersion") != "1.2":
        return PreflightResult(
            PreflightExit.INVALID_ARTIFACT, "schemaVersion must be 1.2"
        )
    config = payload.get("config")
    summary = payload.get("summary")
    tasks = payload.get("tasks")
    if (
        not isinstance(config, dict)
        or config.get("model_id") != expected_model
        or not isinstance(summary, dict)
        or summary.get("total_tests") != 1
        or not isinstance(tasks, list)
        or len(tasks) != 1
        or not isinstance(tasks[0], dict)
    ):
        return PreflightResult(
            PreflightExit.INVALID_ARTIFACT,
            "model, summary, or task shape does not match the preflight contract",
        )
    combined = "\n".join(_strings(payload)).casefold()
    if any(
        marker in combined
        for marker in (
            "auth_unavailable",
            "http 402",
            "http 429",
            "monthly quota",
            "no auth available",
            "quota exceeded",
            "quota_exceeded",
            "rate limit",
            "rate_limit",
            "status 402",
            "status 429",
            "too many requests",
        )
    ):
        return PreflightResult(
            PreflightExit.MODEL_UNAVAILABLE,
            "selected model is unavailable because quota, rate limit, or provider auth is unavailable",
        )
    if any(
        marker in combined
        for marker in (
            "forbidden",
            "http 401",
            "http 403",
            "invalid api key",
            "status 401",
            "status 403",
            "unauthorized",
        )
    ):
        return PreflightResult(
            PreflightExit.AUTH_INVALID, "provider authentication was rejected"
        )
    if any(
        marker in combined
        for marker in (
            "context deadline exceeded",
            "deadline exceeded",
            "request timeout",
            "timed out",
            "timeout",
        )
    ):
        return PreflightResult(
            PreflightExit.TRANSPORT_INVALID, "provider transport timed out"
        )
    task = tasks[0]
    runs = task.get("runs")
    if not isinstance(runs, list) or len(runs) != 1 or not isinstance(runs[0], dict):
        return PreflightResult(PreflightExit.INVALID_ARTIFACT, "run is missing")
    run = runs[0]
    digest = run.get("session_digest")
    final_output = run.get("final_output")
    if run.get("status") == "error" or run.get("error_msg"):
        return PreflightResult(
            PreflightExit.TRANSPORT_INVALID,
            str(run.get("error_msg") or "provider transport failed"),
        )
    if (
        summary.get("succeeded") != 1
        or summary.get("failed") != 0
        or summary.get("errors") != 0
        or summary.get("skipped") != 0
        or task.get("status") not in {"passed", "succeeded"}
        or run.get("status") not in {"passed", "succeeded"}
    ):
        return PreflightResult(
            PreflightExit.EVAL_FAILED, "preflight assertion or grader failed"
        )
    if (
        not isinstance(digest, dict)
        or not isinstance(digest.get("tool_call_count"), int)
        or digest["tool_call_count"] < 1
        or not isinstance(final_output, str)
        or not final_output.strip()
    ):
        return PreflightResult(
            PreflightExit.TRANSPORT_INVALID,
            "run did not prove a tool call and non-empty final output",
        )
    return PreflightResult(PreflightExit.AVAILABLE, "live Waza transport is available")


def _run_waza(command: Sequence[str], root: Path) -> int:
    return run_command(command, root).exit_code


def run_preflight(root: Path, *, runner: WazaRunner = _run_waza) -> PreflightResult:
    """Run one fresh owner-model preflight and publish only verified output."""

    model = default_model(root)
    results_root = root / "results"
    output_root = results_root / "preflight"
    for directory in (results_root, output_root):
        if directory.is_symlink():
            return PreflightResult(
                PreflightExit.INVALID_ARTIFACT,
                f"preflight output directory must not be a symlink: {directory}",
            )
        try:
            directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        except OSError as error:
            return PreflightResult(PreflightExit.INVALID_ARTIFACT, str(error))
    destination = output_root / "results.json"
    try:
        candidate = stage_text(destination, "", mode=0o600)
    except (OSError, RuntimeError) as error:
        return PreflightResult(
            PreflightExit.INVALID_ARTIFACT,
            f"preflight candidate creation failed: {error}",
        )
    command = (
        "waza",
        "run",
        str(root / "config" / "waza" / "preflight" / "eval.yaml"),
        "--model",
        model,
        "--output",
        str(candidate),
    )
    result: PreflightResult | None = None
    cleanup_error: OSError | RuntimeError | None = None
    try:
        try:
            exit_code = runner(command, root)
        except (OSError, RuntimeError, ValueError) as error:
            result = PreflightResult(
                PreflightExit.TRANSPORT_INVALID,
                f"Waza preflight could not start: {error}",
            )
        else:
            result = classify_preflight(candidate, model)
            if exit_code != 0:
                result = (
                    PreflightResult(
                        PreflightExit.TRANSPORT_INVALID,
                        f"Waza exited {exit_code} despite a successful-looking artifact",
                    )
                    if result.status == PreflightExit.AVAILABLE
                    else PreflightResult(
                        result.status,
                        f"Waza exited {exit_code}: {result.message}",
                    )
                )
            elif result.status == PreflightExit.AVAILABLE:
                try:
                    _publish_candidate(root, candidate, destination)
                except WazaArtifactError as error:
                    result = PreflightResult(
                        PreflightExit.INVALID_ARTIFACT,
                        str(error),
                    )
    finally:
        active_error = sys.exception()
        try:
            discard_physical_file(candidate)
        except (OSError, RuntimeError) as error:
            if active_error is not None:
                raise BaseExceptionGroup(
                    "Waza preflight and candidate cleanup both failed",
                    [active_error, error],
                )
            cleanup_error = error
    if result is None:
        raise RuntimeError("Waza preflight completed without a classified result")
    if cleanup_error is not None:
        return PreflightResult(
            PreflightExit.INVALID_ARTIFACT,
            f"{result.status.name}: {result.message}; "
            f"preflight candidate cleanup failed: {cleanup_error}",
        )
    return result


def default_model(root: Path) -> str:
    """Return the configured project model, refusing implicit Waza defaults."""

    path = root / ".waza.yaml"
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise ValueError(f"{path}: model owner cannot be loaded: {error}") from error
    defaults = payload.get("defaults") if isinstance(payload, dict) else None
    model = defaults.get("model") if isinstance(defaults, dict) else None
    if not isinstance(model, str) or not model:
        raise ValueError(f"{path}: defaults.model is required")
    if model != model.strip():
        raise ValueError(f"{path}: defaults.model must not contain outer whitespace")
    return model


def _eval_paths(root: Path) -> tuple[Path, ...]:
    """Return every materialized Waza eval owned by the project model."""

    paths = sorted((root / "evals").glob("*/eval.yaml"))
    preflight = root / "config" / "waza" / "preflight" / "eval.yaml"
    if preflight.is_file():
        paths.append(preflight)
    return tuple(paths)


def findings(root: Path) -> list[WazaConfigFinding]:
    """Return every eval whose materialized model differs from the SSOT."""

    expected = default_model(root)
    result: list[WazaConfigFinding] = []
    for path in _eval_paths(root):
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as error:
            raise ValueError(f"{path}: eval cannot be loaded: {error}") from error
        config = payload.get("config") if isinstance(payload, dict) else None
        actual = config.get("model") if isinstance(config, dict) else None
        if actual != expected:
            result.append(
                WazaConfigFinding(
                    path=path,
                    actual=actual if isinstance(actual, str) else None,
                    expected=expected,
                )
            )
    return result


def apply(root: Path) -> list[WazaConfigFinding]:
    """Materialize the SSOT model through staged atomic replacements."""

    changes = findings(root)
    staged: list[tuple[Path, Path]] = []
    originals: dict[Path, tuple[str, int]] = {}
    committed: list[Path] = []
    completed = False
    try:
        for change in changes:
            if change.path.is_symlink() or change.path.parent.is_symlink():
                raise ValueError(f"{change.path}: eval path must not be a symlink")
            original = change.path.read_text(encoding="utf-8")
            mode = change.path.stat().st_mode & 0o777
            try:
                payload = yaml.safe_load(original)
            except yaml.YAMLError as error:
                raise ValueError(
                    f"{change.path}: eval cannot be loaded: {error}"
                ) from error
            if not isinstance(payload, dict):
                raise TypeError(f"{change.path}: eval must be a mapping")
            config = payload.get("config")
            if not isinstance(config, dict):
                raise TypeError(f"{change.path}: config must be a mapping")
            config["model"] = change.expected
            rendered = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
            candidate = stage_text(
                change.path,
                rendered,
                mode=mode,
            )
            originals[change.path] = (original, mode)
            staged.append((candidate, change.path))
        for candidate, destination in staged:
            os.replace(candidate, destination)
            committed.append(destination)
        completed = True
    finally:
        operation_error = sys.exception()
        recovery_errors: list[Exception] = []
        if not completed:
            for destination in reversed(committed):
                original, mode = originals[destination]
                rollback: Path | None = None
                try:
                    rollback = stage_text(destination, original, mode=mode)
                    os.replace(rollback, destination)
                except (OSError, RuntimeError) as rollback_error:
                    recovery_errors.append(rollback_error)
                finally:
                    if rollback is not None:
                        try:
                            discard_physical_file(rollback)
                        except (OSError, RuntimeError) as cleanup_error:
                            recovery_errors.append(cleanup_error)
        for candidate, _destination in staged:
            try:
                discard_physical_file(candidate)
            except (OSError, RuntimeError) as cleanup_error:
                recovery_errors.append(cleanup_error)
        if recovery_errors:
            primary = operation_error or RuntimeError(
                "Waza projection recovery ran without an operation failure"
            )
            raise BaseExceptionGroup(
                "Waza projection and recovery both failed",
                [primary, *recovery_errors],
            )
    return changes
