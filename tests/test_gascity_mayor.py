from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from source_loader import load_source_module

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills/domain/gascity/mayor/assets/scripts/create_beads_from_tasks.py"
)


def _module() -> Any:
    return load_source_module("create_beads_from_tasks", SCRIPT)


def _tasks(payload_yaml: str) -> str:
    return (
        "---\n"
        "plan_slug: example-slug\n"
        "phase: tasks\n"
        "status: draft\n"
        "---\n"
        "# Tasks\n\n"
        "## Bead Creation Payload\n\n"
        "```yaml\n"
        f"{payload_yaml}"
        "```\n"
    )


def test_payload_parses_block_schema_with_nested_convoys() -> None:
    module = _module()
    markdown = _tasks(
        "target_rig: backend\n"
        "labels:\n"
        "- web\n"
        "- api\n"
        "convoys:\n"
        "  - key: backend-convoy\n"
        "    title: Backend work\n"
        "    description: Implement the backend slice\n"
        "    target: gc.run-operator\n"
        "    metadata:\n"
        "      gc.model: primary\n"
        "    beads:\n"
        "      - key: task-1\n"
        "        title: Task one # pinned\n"
        "        type: feature\n"
        "        priority: P1\n"
        "        description: 'First: implement it'\n"
        "        acceptance_criteria:\n"
        "          - criterion one\n"
        "          - criterion two\n"
        "beads:\n"
        "  - key: standalone\n"
        "    title: Standalone bead\n"
        "    type: chore\n"
        "    description: A standalone item\n"
        "    dependencies:\n"
        "      - task-1\n"
    )

    plan = module.parse_plan(module.extract_payload(markdown))

    assert plan.target_rig == "backend"
    assert plan.labels == ["web", "api"]
    convoy = plan.convoys[0]
    assert convoy.key == "backend-convoy"
    assert convoy.metadata == {"opt_model": "primary"}
    assert convoy.bead_keys == ["task-1"]
    first = plan.runnables[0]
    assert first.title == "Task one"
    assert first.description == "First: implement it"
    assert first.acceptance_criteria == ["criterion one", "criterion two"]
    assert [runnable.key for runnable in plan.runnables] == ["task-1", "standalone"]
    assert ("standalone", "task-1") in module.expanded_dependency_edges(plan)


@pytest.mark.parametrize(
    "payload",
    [
        "dependencies: [task-1]\n",
        "target_rig: backend\ntarget_rig: duplicate\n",
        "key:\n\t- tabbed\n",
        "key: !!python/object:os.system\n",
    ],
)
def test_unsupported_payload_syntax_fails_loud(payload: str) -> None:
    module = _module()

    with pytest.raises(module.PlanError):
        module.extract_payload(_tasks(payload))


def test_front_matter_round_trips_quoted_values() -> None:
    module = _module()
    markdown = _tasks("target_rig: backend\n")
    updated = module.update_front_matter(
        markdown, {"status": "created", "updated_at": "2026-09-02T00:00:00Z"}
    )

    assert module.front_matter_status(updated) == "created"
    assert 'plan_slug: "example-slug"' in updated


def test_runner_gates_external_executables_and_dry_run_never_spawns(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _module()

    def explode(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("subprocess must not run in dry-run")

    monkeypatch.setattr(module.subprocess, "run", explode)

    runner = module.Runner(None, "backend", True)
    assert runner.run(["gc", "bd", "create", "--json", "x"]) == ""
    with pytest.raises(module.PlanError, match="not declared"):
        runner.run(["git", "push"])

    assert "gc bd create" in capsys.readouterr().out


def test_declared_external_executables_are_exactly_gc() -> None:
    module = _module()

    assert module.EXTERNAL_EXECUTABLES == frozenset({"gc"})
