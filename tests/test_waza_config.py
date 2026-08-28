from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

import pytest
import yaml

import agents_governance.waza as waza_module
from agents_governance.waza import (
    EvalRole,
    default_model,
    load_eval_suite,
    require_model_projection,
    run_preflight,
)

_MODEL = "owner-model"


def _eval(path: Path, model: str = _MODEL) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"name: example\nconfig:\n  model: {model}\n  timeout_seconds: 60\n",
        encoding="utf-8",
    )


def _model_authority(root: Path, model: str = _MODEL) -> None:
    (root / ".waza.yaml").write_text(f"defaults:\n  model: {model}\n", encoding="utf-8")
    _eval(root / "evals" / "example" / "eval.yaml", model)
    _eval(root / "config" / "waza" / "preflight" / "eval.yaml", model)


def _suite(root: Path) -> Path:
    directory = root / "evals" / "example"
    tasks = directory / "tasks"
    tasks.mkdir(parents=True)
    (directory / "eval.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "example-eval",
                "skill": "example",
                "config": {
                    "model": _MODEL,
                    "timeout_seconds": 60,
                    "required_skills": ["example"],
                    "skill_directories": ["../../skills/agent-wide/example"],
                },
                "graders": [
                    {
                        "type": "prompt",
                        "name": "example-contract",
                        "config": {"prompt": "Grade example material output."},
                    },
                    {
                        "type": "behavior",
                        "name": "bounded",
                        "config": {"max_duration_ms": 50_000},
                    },
                ],
                "tasks": ["tasks/*.yaml"],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    prompts = {
        "basic-usage.yaml": "Execute the material example.",
        "edge-case.yaml": "",
        "should-not-trigger.yaml": "Do unrelated work.",
    }
    for index, (name, prompt) in enumerate(prompts.items()):
        (tasks / name).write_text(
            yaml.safe_dump(
                {
                    "id": f"example-{index}",
                    "inputs": {"prompt": prompt},
                    "expected": {
                        "output_contains": ["material output"],
                        "output_not_contains": ["forbidden action"],
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
    return directory


def _artifact(model: str = _MODEL) -> dict[str, object]:
    return {
        "schemaVersion": "1.2",
        "config": {"model_id": model},
        "summary": {
            "total_tests": 1,
            "succeeded": 1,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
        },
        "tasks": [
            {
                "status": "passed",
                "runs": [
                    {
                        "status": "passed",
                        "error_msg": "",
                        "final_output": "AGENTS_WAZA_TOOL_SENTINEL_7C4E91",
                        "session_digest": {"tool_call_count": 1},
                    }
                ],
            }
        ],
    }


def _preflight_root(root: Path) -> None:
    _model_authority(root)
    (root / "results" / "preflight").mkdir(parents=True)


def test_model_projection_is_read_only_and_exact(tmp_path: Path) -> None:
    _model_authority(tmp_path)

    assert default_model(tmp_path) == _MODEL
    assert require_model_projection(tmp_path) == _MODEL

    path = tmp_path / "evals" / "example" / "eval.yaml"
    _eval(path, "other-model")
    with pytest.raises(ValueError, match="other-model.*owner-model"):
        require_model_projection(tmp_path)
    assert "other-model" in path.read_text(encoding="utf-8")


def test_model_owner_rejects_whitespace_and_missing_value(tmp_path: Path) -> None:
    (tmp_path / ".waza.yaml").write_text(
        'defaults:\n  model: " owner-model "\n', encoding="utf-8"
    )
    with pytest.raises(TypeError, match="trimmed"):
        default_model(tmp_path)

    (tmp_path / ".waza.yaml").write_text("defaults: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="model is required"):
        default_model(tmp_path)


def test_eval_suite_loads_exact_three_role_contract(tmp_path: Path) -> None:
    suite = load_eval_suite(_suite(tmp_path))

    assert suite.skill == "example"
    assert suite.timeout_seconds == 60
    assert tuple(task.role for task in suite.tasks) == (
        EvalRole.HAPPY_PATH,
        EvalRole.FAIL_CLOSED,
        EvalRole.SHOULD_NOT_TRIGGER,
    )


def test_eval_suite_rejects_unknown_task_inventory(tmp_path: Path) -> None:
    directory = _suite(tmp_path)
    (directory / "tasks" / "extra.yaml").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="task files must equal"):
        load_eval_suite(directory)


def test_live_preflight_publishes_only_fresh_valid_artifact(tmp_path: Path) -> None:
    _preflight_root(tmp_path)

    def runner(command: Sequence[str], root: Path) -> None:
        assert command[:2] == ("waza", "run")
        assert root == tmp_path
        output = Path(command[command.index("--output") + 1])
        output.write_text(json.dumps(_artifact()), encoding="utf-8")

    destination = run_preflight(tmp_path, _MODEL, runner=runner)

    assert destination == tmp_path / "results" / "preflight" / "results.json"
    assert json.loads(destination.read_text(encoding="utf-8")) == _artifact()
    assert not tuple(destination.parent.glob("*.candidate"))


def test_runner_failure_propagates_and_candidate_is_cleaned(tmp_path: Path) -> None:
    _preflight_root(tmp_path)

    def runner(_command: Sequence[str], _root: Path) -> None:
        raise OSError("transport exploded")

    with pytest.raises(OSError, match="transport exploded"):
        run_preflight(tmp_path, _MODEL, runner=runner)

    assert not (tmp_path / "results" / "preflight" / "results.json").exists()
    assert not tuple((tmp_path / "results" / "preflight").glob("*.candidate"))


def test_invalid_artifact_propagates_and_is_not_published(tmp_path: Path) -> None:
    _preflight_root(tmp_path)

    def runner(command: Sequence[str], _root: Path) -> None:
        output = Path(command[command.index("--output") + 1])
        output.write_text(json.dumps(_artifact("other-model")), encoding="utf-8")

    with pytest.raises(ValueError, match="artifact model"):
        run_preflight(tmp_path, _MODEL, runner=runner)

    assert not (tmp_path / "results" / "preflight" / "results.json").exists()


def test_publication_failure_propagates_and_preserves_destination(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _preflight_root(tmp_path)
    destination = tmp_path / "results" / "preflight" / "results.json"
    destination.write_text('{"original": true}\n', encoding="utf-8")

    def runner(command: Sequence[str], _root: Path) -> None:
        output = Path(command[command.index("--output") + 1])
        output.write_text(json.dumps(_artifact()), encoding="utf-8")

    def fail_replace(_source: str | Path, _destination: str | Path) -> None:
        raise OSError("publication exploded")

    monkeypatch.setattr(waza_module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="publication exploded"):
        run_preflight(tmp_path, _MODEL, runner=runner)

    assert destination.read_text(encoding="utf-8") == '{"original": true}\n'
    assert not tuple(destination.parent.glob("*.candidate"))


def test_live_preflight_behavior_budget_precedes_executor_timeout() -> None:
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


def test_waza_owner_contains_no_exception_catch_or_status_classifier() -> None:
    source = (
        Path(__file__).resolve().parents[1] / "src/agents_governance/waza.py"
    ).read_text(encoding="utf-8")

    assert "except " not in source
    assert "PreflightExit" not in source
    assert "classify" not in source
