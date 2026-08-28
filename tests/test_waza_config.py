from __future__ import annotations

import json
import os
from collections.abc import Sequence
from pathlib import Path

import pytest
import yaml

import agents_governance.waza as waza_module
from agents_governance.waza import (
    PreflightExit,
    apply,
    classify_preflight,
    default_model,
    findings,
    run_preflight,
)

_OWNER_MODEL = "owner-model"
_OTHER_MODEL = "other-model"
_QUOTA_MODEL = "quota-model"


def test_waza_model_projection_is_owned_and_convergent(tmp_path: Path) -> None:
    (tmp_path / ".waza.yaml").write_text(
        f"defaults:\n  model: {_OWNER_MODEL}\n", encoding="utf-8"
    )
    eval_path = tmp_path / "evals" / "example" / "eval.yaml"
    eval_path.parent.mkdir(parents=True)
    eval_path.write_text(
        "name: example\nconfig:\n  model: invalid-model\n  trials_per_task: 1\n",
        encoding="utf-8",
    )
    preflight_path = tmp_path / "config" / "waza" / "preflight" / "eval.yaml"
    preflight_path.parent.mkdir(parents=True)
    preflight_path.write_text(
        "name: preflight\nconfig:\n  model: invalid-model\n  trials_per_task: 1\n",
        encoding="utf-8",
    )

    assert default_model(tmp_path) == _OWNER_MODEL
    assert [(item.actual, item.expected) for item in findings(tmp_path)] == [
        ("invalid-model", _OWNER_MODEL),
        ("invalid-model", _OWNER_MODEL),
    ]
    assert len(apply(tmp_path)) == 2
    assert not findings(tmp_path)


def test_waza_model_owner_rejects_implicit_normalization(tmp_path: Path) -> None:
    (tmp_path / ".waza.yaml").write_text(
        'defaults:\n  model: " owner-model "\n', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="outer whitespace"):
        default_model(tmp_path)


def test_waza_projection_rolls_back_every_committed_file_on_replace_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / ".waza.yaml").write_text(
        f"defaults:\n  model: {_OWNER_MODEL}\n", encoding="utf-8"
    )
    originals: dict[Path, bytes] = {}
    for name in ("first", "second"):
        path = tmp_path / "evals" / name / "eval.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(
            "name: example\nconfig:\n  model: invalid-model\n",
            encoding="utf-8",
        )
        originals[path] = path.read_bytes()

    real_replace = os.replace
    commits = 0

    def fail_second_candidate(source: str | Path, destination: str | Path) -> None:
        nonlocal commits
        if str(source).endswith(".candidate"):
            commits += 1
            if commits == 2:
                raise OSError("injected replace failure")
        real_replace(source, destination)

    monkeypatch.setattr(waza_module.os, "replace", fail_second_candidate)

    with pytest.raises(OSError, match="injected replace failure"):
        apply(tmp_path)

    assert all(path.read_bytes() == original for path, original in originals.items())
    assert not list(tmp_path.rglob("*.candidate"))
    assert not list(tmp_path.rglob("*.rollback"))


def test_waza_projection_exposes_operation_and_rollback_failures(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / ".waza.yaml").write_text(
        f"defaults:\n  model: {_OWNER_MODEL}\n", encoding="utf-8"
    )
    for name in ("first", "second"):
        path = tmp_path / "evals" / name / "eval.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(
            "name: example\nconfig:\n  model: invalid-model\n",
            encoding="utf-8",
        )

    real_replace = os.replace
    replacements = 0

    def fail_operation_and_rollback(
        source: str | Path, destination: str | Path
    ) -> None:
        nonlocal replacements
        if str(source).endswith(".candidate"):
            replacements += 1
            if replacements == 2:
                raise OSError("injected operation failure")
            if replacements == 3:
                raise OSError("injected rollback failure")
        real_replace(source, destination)

    monkeypatch.setattr(waza_module.os, "replace", fail_operation_and_rollback)

    with pytest.raises(BaseExceptionGroup) as captured:
        apply(tmp_path)

    messages = [str(error) for error in captured.value.exceptions]
    assert any("injected operation failure" in message for message in messages)
    assert any("injected rollback failure" in message for message in messages)
    assert not list(tmp_path.rglob("*.candidate"))


def test_live_preflight_behavior_budget_is_below_executor_timeout() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = yaml.safe_load(
        (root / "config" / "waza" / "preflight" / "eval.yaml").read_text(
            encoding="utf-8"
        )
    )
    timeout_ms = payload["config"]["timeout_seconds"] * 1000
    behavior = next(
        grader for grader in payload["graders"] if grader["type"] == "behavior"
    )

    assert 0 < behavior["config"]["max_duration_ms"] < timeout_ms


def _result(
    *, model: str = _OWNER_MODEL, error: str = "", tool_calls: int = 1
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
            "skipped": 0,
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

    assert classify_preflight(artifact, _OWNER_MODEL).status == PreflightExit.AVAILABLE


def test_preflight_classifies_selected_model_quota(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(
        json.dumps(
            _result(
                model=_QUOTA_MODEL,
                error="HTTP 402 quota_exceeded: monthly quota",
            )
        ),
        encoding="utf-8",
    )

    assert (
        classify_preflight(artifact, _QUOTA_MODEL).status
        == PreflightExit.MODEL_UNAVAILABLE
    )


@pytest.mark.parametrize(
    ("error", "status"),
    [
        ("HTTP 429 rate_limit: too many requests", PreflightExit.MODEL_UNAVAILABLE),
        ("HTTP 403 forbidden", PreflightExit.AUTH_INVALID),
        ("request timeout: context deadline exceeded", PreflightExit.TRANSPORT_INVALID),
        (
            "503 auth_unavailable: no auth available",
            PreflightExit.MODEL_UNAVAILABLE,
        ),
    ],
)
def test_preflight_classifies_every_loud_transport_failure(
    tmp_path: Path, error: str, status: PreflightExit
) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(json.dumps(_result(error=error)), encoding="utf-8")

    assert classify_preflight(artifact, _OWNER_MODEL).status == status


def test_preflight_rejects_model_mismatch_before_error_classification(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(
        json.dumps(_result(error="HTTP 402 quota_exceeded")), encoding="utf-8"
    )

    assert (
        classify_preflight(artifact, _OTHER_MODEL).status
        == PreflightExit.INVALID_ARTIFACT
    )


def test_preflight_rejects_success_without_tool_use(tmp_path: Path) -> None:
    artifact = tmp_path / "result.json"
    artifact.write_text(json.dumps(_result(tool_calls=0)), encoding="utf-8")

    assert (
        classify_preflight(artifact, _OWNER_MODEL).status
        == PreflightExit.TRANSPORT_INVALID
    )


def _preflight_authority(root: Path) -> None:
    (root / ".waza.yaml").write_text(
        f"defaults:\n  model: {_OWNER_MODEL}\n", encoding="utf-8"
    )
    config = root / "config" / "waza" / "preflight" / "eval.yaml"
    config.parent.mkdir(parents=True)
    config.write_text("name: preflight\n", encoding="utf-8")


def _output_argument(command: Sequence[str]) -> Path:
    return Path(command[command.index("--output") + 1])


def test_run_preflight_uses_owner_model_and_atomically_publishes_fresh_output(
    tmp_path: Path,
) -> None:
    _preflight_authority(tmp_path)
    observed: list[tuple[str, ...]] = []

    def runner(command: Sequence[str], cwd: Path) -> int:
        assert cwd == tmp_path
        observed.append(tuple(command))
        _output_argument(command).write_text(json.dumps(_result()), encoding="utf-8")
        return 0

    result = run_preflight(tmp_path, runner=runner)

    assert result.status == PreflightExit.AVAILABLE
    assert observed[0][observed[0].index("--model") + 1] == _OWNER_MODEL
    published = tmp_path / "results" / "preflight" / "results.json"
    assert json.loads(published.read_text(encoding="utf-8"))["config"] == {
        "model_id": _OWNER_MODEL
    }
    assert not list(published.parent.glob(".results.json.*.candidate"))


def test_run_preflight_never_promotes_a_stale_candidate_after_runner_failure(
    tmp_path: Path,
) -> None:
    _preflight_authority(tmp_path)
    output_root = tmp_path / "results" / "preflight"
    output_root.mkdir(parents=True)
    stale = output_root / "results.json.candidate"
    stale.write_text(json.dumps(_result()), encoding="utf-8")

    result = run_preflight(tmp_path, runner=lambda _command, _cwd: 7)

    assert result.status == PreflightExit.INVALID_ARTIFACT
    assert "Waza exited 7" in result.message
    assert stale.is_file()
    assert not (output_root / "results.json").exists()
    assert not list(output_root.glob(".results.json.*.candidate"))


def test_run_preflight_reports_candidate_cleanup_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _preflight_authority(tmp_path)

    def runner(command: Sequence[str], _cwd: Path) -> int:
        _output_argument(command).write_text(json.dumps(_result()), encoding="utf-8")
        return 0

    def fail_cleanup(_path: Path) -> None:
        raise OSError("injected candidate cleanup failure")

    monkeypatch.setattr(waza_module, "discard_physical_file", fail_cleanup)

    result = run_preflight(tmp_path, runner=runner)

    assert result.status == PreflightExit.INVALID_ARTIFACT
    assert "AVAILABLE: live Waza transport is available" in result.message
    assert "injected candidate cleanup failure" in result.message
