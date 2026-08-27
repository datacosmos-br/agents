"""Validation of Waza runtime artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any


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


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    return []


def classify_preflight(path: Path, expected_model: str) -> PreflightResult:
    """Validate and classify one Waza schema 1.2 preflight artifact."""

    try:
        if path.stat().st_size == 0:
            raise ValueError("artifact is empty")
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return PreflightResult(PreflightExit.INVALID_ARTIFACT, str(error))
    if not isinstance(payload, dict) or payload.get("schemaVersion") != "1.2":
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
        for marker in ("quota_exceeded", "quota exceeded", "monthly quota", "http 402")
    ):
        return PreflightResult(
            PreflightExit.MODEL_UNAVAILABLE, "selected model has no available quota"
        )
    if any(
        marker in combined
        for marker in ("unauthorized", "invalid api key", "http 401", "status 401")
    ):
        return PreflightResult(
            PreflightExit.AUTH_INVALID, "provider authentication was rejected"
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
