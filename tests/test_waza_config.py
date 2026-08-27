from __future__ import annotations

import json
from pathlib import Path

from agents_governance.waza import (
    PreflightExit,
    apply,
    classify_preflight,
    default_model,
    findings,
)


def test_waza_model_projection_is_owned_and_convergent(tmp_path: Path) -> None:
    (tmp_path / ".waza.yaml").write_text(
        "defaults:\n  model: gpt-5.4\n", encoding="utf-8"
    )
    eval_path = tmp_path / "evals" / "example" / "eval.yaml"
    eval_path.parent.mkdir(parents=True)
    eval_path.write_text(
        "name: example\nconfig:\n  model: claude-sonnet-4.6\n  trials_per_task: 1\n",
        encoding="utf-8",
    )

    assert default_model(tmp_path) == "gpt-5.4"
    assert [(item.actual, item.expected) for item in findings(tmp_path)] == [
        ("claude-sonnet-4.6", "gpt-5.4")
    ]
    assert len(apply(tmp_path)) == 1
    assert not findings(tmp_path)


def _result(
    *, model: str = "gpt-5.4", error: str = "", tool_calls: int = 1
) -> dict[str, object]:
    passed = not error
    return {
        "schemaVersion": "1.2",
        "config": {"model_id": model},
        "summary": {
            "total_tests": 1,
            "succeeded": int(passed),
            "failed": int(not passed),
            "errors": 0,
        },
        "tasks": [
            {
                "status": "passed" if passed else "failed",
                "runs": [
                    {
                        "status": "passed" if passed else "error",
                        "error_msg": error,
                        "final_output": "AGENTS_WAZA_TOOL_SENTINEL_7C4E91"
                        if passed
                        else "",
                        "session_digest": {"tool_call_count": tool_calls},
                    }
                ],
            }
        ],
    }


def test_preflight_accepts_only_a_real_tool_using_success(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(json.dumps(_result()), encoding="utf-8")

    assert classify_preflight(artifact, "gpt-5.4").status == PreflightExit.AVAILABLE


def test_preflight_classifies_selected_model_quota(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(
        json.dumps(
            _result(
                model="claude-sonnet-4.6",
                error="HTTP 402 quota_exceeded: monthly quota",
            )
        ),
        encoding="utf-8",
    )

    assert (
        classify_preflight(artifact, "claude-sonnet-4.6").status
        == PreflightExit.MODEL_UNAVAILABLE
    )


def test_preflight_rejects_model_mismatch_before_error_classification(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(
        json.dumps(_result(error="HTTP 402 quota_exceeded")), encoding="utf-8"
    )

    assert (
        classify_preflight(artifact, "claude-sonnet-4.6").status
        == PreflightExit.INVALID_ARTIFACT
    )


def test_preflight_rejects_success_without_tool_use(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(json.dumps(_result(tool_calls=0)), encoding="utf-8")

    assert (
        classify_preflight(artifact, "gpt-5.4").status
        == PreflightExit.TRANSPORT_INVALID
    )
