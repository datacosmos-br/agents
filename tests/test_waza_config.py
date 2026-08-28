from __future__ import annotations

import json
import stat
from collections.abc import Sequence
from pathlib import Path
from typing import cast

import pytest
import yaml

import agents_governance.waza as waza_module
from agents_governance.waza import (
    EvalRole,
    EvalSuiteSpec,
    default_model,
    load_eval_suite,
    require_model_projection,
    run_live_corpus,
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
                    "trials_per_task": 1,
                    "model": _MODEL,
                    "timeout_seconds": 60,
                    "parallel": False,
                    "max_attempts": 0,
                    "fail_fast": True,
                    "executor": "copilot-sdk",
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


def _preflight_suite(root: Path) -> EvalSuiteSpec:
    directory = root / "config" / "waza" / "preflight"
    tasks = directory / "tasks"
    tasks.mkdir(parents=True)
    (directory / "eval.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "preflight-eval",
                "skill": "waza-transport-preflight",
                "config": {
                    "trials_per_task": 1,
                    "model": _MODEL,
                    "timeout_seconds": 60,
                    "parallel": False,
                    "max_attempts": 0,
                    "fail_fast": True,
                    "executor": "copilot-sdk",
                    "required_skills": ["waza-transport-preflight"],
                    "skill_directories": ["skill"],
                },
                "graders": [
                    {
                        "type": "code",
                        "name": "sentinel-returned",
                        "config": {"prompt": "Require the exact sentinel."},
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
    (tasks / "tool-read.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "tool-read-001",
                "inputs": {
                    "prompt": "Read the exact sentinel.",
                    "files": [{"path": "sentinel.txt"}],
                },
                "expected": {"output_contains": ["exact-sentinel"]},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return waza_module._preflight_suite(root)


def _artifact(
    suite: EvalSuiteSpec,
    model: str = _MODEL,
    *,
    tool_call_count: int = 0,
) -> dict[str, object]:
    tasks: list[dict[str, object]] = []
    for task in suite.tasks:
        validations = {grader.name: {"passed": True} for grader in suite.graders}
        if task.output_contains:
            validations["_output_contains"] = {"passed": True}
        if task.output_not_contains:
            validations["_output_not_contains"] = {"passed": True}
        tasks.append(
            {
                "test_id": task.identifier,
                "status": "passed",
                "runs": [
                    {
                        "run_number": 1,
                        "attempts": 1,
                        "status": "passed",
                        "error_msg": "",
                        "validations": validations,
                        "final_output": "material output exact-sentinel",
                        "session_digest": {"tool_call_count": tool_call_count},
                    }
                ],
            }
        )
    return {
        "schemaVersion": "1.2",
        "skill": suite.skill,
        "config": {"model_id": model, "engine_type": suite.executor},
        "summary": {
            "total_tests": len(suite.tasks),
            "succeeded": len(suite.tasks),
            "failed": 0,
            "errors": 0,
            "skipped": 0,
        },
        "tasks": tasks,
    }


def _live_root(root: Path) -> tuple[EvalSuiteSpec, EvalSuiteSpec]:
    (root / "results").mkdir()
    preflight = _preflight_suite(root)
    suite = load_eval_suite(_suite(root))
    return preflight, suite


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


def test_live_corpus_runs_every_suite_and_publishes_one_complete_artifact(
    tmp_path: Path,
) -> None:
    preflight, suite = _live_root(tmp_path)
    expected = {preflight.path: preflight, suite.path: suite}
    observed: list[Path] = []

    def runner(command: Sequence[str], root: Path) -> None:
        assert command[:2] == ("/owner/bin/waza", "run")
        assert root == tmp_path
        selected = expected[Path(command[2])]
        observed.append(selected.path)
        output = Path(command[command.index("--output") + 1])
        output.write_text(
            json.dumps(
                _artifact(
                    selected,
                    tool_call_count=int(selected is preflight),
                )
            ),
            encoding="utf-8",
        )

    destination = run_live_corpus(
        tmp_path,
        _MODEL,
        (suite,),
        "/owner/bin/waza",
        runner=runner,
    )

    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert destination == tmp_path / "results" / "latest" / "results.json"
    assert observed == [preflight.path, suite.path]
    assert payload["model"] == _MODEL
    assert payload["suite_count"] == 2
    assert payload["task_count"] == 4
    assert len(payload["artifacts"]) == 2
    assert stat.S_IMODE(destination.stat().st_mode) == 0o600
    assert not tuple(destination.parent.glob("*.candidate"))
    assert not tuple((tmp_path / "results").glob(".waza-live-stage.*"))


def test_runner_failure_propagates_and_candidate_is_cleaned(tmp_path: Path) -> None:
    _preflight, suite = _live_root(tmp_path)

    def runner(_command: Sequence[str], _root: Path) -> None:
        raise OSError("transport exploded")

    with pytest.raises(OSError, match="transport exploded"):
        run_live_corpus(
            tmp_path,
            _MODEL,
            (suite,),
            "/owner/bin/waza",
            runner=runner,
        )

    assert not (tmp_path / "results" / "latest").exists()
    assert not tuple((tmp_path / "results").glob(".waza-live-stage.*"))


def test_invalid_artifact_propagates_and_is_not_published(tmp_path: Path) -> None:
    preflight, suite = _live_root(tmp_path)

    def runner(command: Sequence[str], _root: Path) -> None:
        output = Path(command[command.index("--output") + 1])
        artifact = _artifact(preflight, tool_call_count=1)
        task = cast(list[dict[str, object]], artifact["tasks"])[0]
        run = cast(list[dict[str, object]], task["runs"])[0]
        validations = cast(dict[str, object], run["validations"])
        del validations["sentinel-returned"]
        output.write_text(json.dumps(artifact), encoding="utf-8")

    with pytest.raises(ValueError, match="graders are incomplete"):
        run_live_corpus(
            tmp_path,
            _MODEL,
            (suite,),
            "/owner/bin/waza",
            runner=runner,
        )

    assert not (tmp_path / "results" / "latest").exists()


def test_publication_failure_propagates_and_preserves_destination(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    preflight, suite = _live_root(tmp_path)
    latest = tmp_path / "results" / "latest"
    latest.mkdir()
    destination = latest / "results.json"
    destination.write_text('{"original": true}\n', encoding="utf-8")
    by_path = {preflight.path: preflight, suite.path: suite}

    def runner(command: Sequence[str], _root: Path) -> None:
        selected = by_path[Path(command[2])]
        output = Path(command[command.index("--output") + 1])
        output.write_text(
            json.dumps(_artifact(selected, tool_call_count=int(selected is preflight))),
            encoding="utf-8",
        )

    def fail_replace(_source: str | Path, _destination: str | Path) -> None:
        raise OSError("publication exploded")

    monkeypatch.setattr(waza_module.os, "replace", fail_replace)

    with pytest.raises(OSError, match="publication exploded"):
        run_live_corpus(
            tmp_path,
            _MODEL,
            (suite,),
            "/owner/bin/waza",
            runner=runner,
        )

    assert destination.read_text(encoding="utf-8") == '{"original": true}\n'
    assert not tuple(destination.parent.glob("*.candidate"))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (("max_attempts", 1, "must equal 0"), ("fail_fast", False, "must be true")),
)
def test_eval_suite_rejects_retry_or_non_fail_fast_execution(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    directory = _suite(tmp_path)
    path = directory / "eval.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    payload["config"][field] = value
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_eval_suite(directory)


def test_repository_eval_specs_disable_waza_retry_and_enable_fail_fast() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = [root / "config" / "waza" / "preflight" / "eval.yaml"]
    paths.extend(sorted((root / "evals").glob("*/eval.yaml")))

    assert len(paths) == 1 + len(tuple((root / "skills").glob("*/*/SKILL.md")))
    for path in paths:
        config = yaml.safe_load(path.read_text(encoding="utf-8"))["config"]
        assert config["max_attempts"] == 0, path
        assert config["fail_fast"] is True, path


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
