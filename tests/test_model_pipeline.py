from __future__ import annotations

import json
from pathlib import Path

import yaml

from agents_governance.model_pipeline import apply, findings, resolve
from agents_governance.waza import PreflightExit, classify_preflight


def _fixture(root: Path, model: str = "wrong-model") -> None:
    (root / "config").mkdir()
    (root / "config" / "model-pipeline.json").write_text(
        '{"version": 1, "pipeline": "ai-hub-primary"}\n', encoding="utf-8"
    )
    (root / ".waza.yaml").write_text(f"defaults:\n  model: {model}\n", encoding="utf-8")
    preflight = root / "config" / "waza" / "preflight" / "eval.yaml"
    preflight.parent.mkdir(parents=True)
    preflight.write_text(f"config:\n  model: {model}\n", encoding="utf-8")
    eval_path = root / "evals" / "example" / "eval.yaml"
    eval_path.parent.mkdir(parents=True)
    eval_path.write_text(f"config:\n  model: {model}\n", encoding="utf-8")
    agents = root / "agents"
    agents.mkdir()
    (agents / "example.md").write_text(
        f"---\nname: example\nmodel: {model}\n---\n", encoding="utf-8"
    )
    (agents / "manifest.json").write_text(
        json.dumps({"agents": {"example": {"model": model}}}), encoding="utf-8"
    )


def test_model_pipeline_projection_is_owned_and_convergent(tmp_path: Path) -> None:
    _fixture(tmp_path)

    assert resolve(tmp_path) == "ai-hub-primary"
    assert len(findings(tmp_path)) == 5
    assert len(apply(tmp_path)) == 5
    assert not findings(tmp_path)
    assert (
        yaml.safe_load((tmp_path / ".waza.yaml").read_text())["defaults"]["model"]
        == "ai-hub-primary"
    )


def test_model_pipeline_rejects_any_other_contract(tmp_path: Path) -> None:
    _fixture(tmp_path)
    (tmp_path / "config" / "model-pipeline.json").write_text(
        '{"version": 1, "pipeline": "wrong-model"}\n', encoding="utf-8"
    )

    try:
        resolve(tmp_path)
    except ValueError as error:
        assert "ai-hub-primary" in str(error)
    else:
        raise AssertionError("noncanonical pipeline was accepted")


def _result(
    *, model: str = "ai-hub-primary", error: str = "", tool_calls: int = 1
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


def test_preflight_accepts_only_pipeline_tool_using_success(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(json.dumps(_result()), encoding="utf-8")
    assert (
        classify_preflight(artifact, "ai-hub-primary").status == PreflightExit.AVAILABLE
    )


def test_preflight_keeps_quota_failure_red(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(
        json.dumps(_result(error="HTTP 402 quota_exceeded: monthly quota")),
        encoding="utf-8",
    )
    assert (
        classify_preflight(artifact, "ai-hub-primary").status
        == PreflightExit.MODEL_UNAVAILABLE
    )


def test_preflight_rejects_concrete_model_and_missing_tool(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(json.dumps(_result(model="wrong-model")), encoding="utf-8")
    assert (
        classify_preflight(artifact, "ai-hub-primary").status
        == PreflightExit.INVALID_ARTIFACT
    )
    artifact.write_text(json.dumps(_result(tool_calls=0)), encoding="utf-8")
    assert (
        classify_preflight(artifact, "ai-hub-primary").status
        == PreflightExit.TRANSPORT_INVALID
    )
