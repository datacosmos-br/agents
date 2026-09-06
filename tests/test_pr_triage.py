from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    path = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "tool"
        / "pr-sheriff"
        / "scripts"
        / "pr_triage.py"
    )
    spec = importlib.util.spec_from_file_location("pr_triage_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_rest_inventory_uses_github_pagination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    calls: list[list[str]] = []

    def fake_gh(*arguments: str, input_text: str | None = None) -> str:
        calls.append(list(arguments))
        return json.dumps({"name": "check"}) + "\n"

    monkeypatch.setattr(module, "_gh", fake_gh)

    checks = module._checks("marlon-costa-dc", "agents", "head-sha")

    assert checks == [{"name": "check"}]
    assert calls == [
        [
            "api",
            "--paginate",
            "repos/marlon-costa-dc/agents/commits/head-sha/check-runs?per_page=100",
            "-q",
            ".check_runs[] | {name:.name,status:.status,conclusion:.conclusion}",
        ]
    ]


def test_terminal_non_success_conclusions_are_blocking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    checks = [
        {"name": "green", "status": "COMPLETED", "conclusion": "success"},
        {"name": "neutral", "status": "COMPLETED", "conclusion": "neutral"},
        {"name": "skipped", "status": "COMPLETED", "conclusion": "skipped"},
        {"name": "failed", "status": "COMPLETED", "conclusion": "failure"},
        {"name": "cancelled", "status": "COMPLETED", "conclusion": "cancelled"},
        {"name": "timed-out", "status": "COMPLETED", "conclusion": "timed_out"},
        {"name": "stale", "status": "COMPLETED", "conclusion": "stale"},
        {
            "name": "action-required",
            "status": "COMPLETED",
            "conclusion": "action_required",
        },
        {
            "name": "startup-failure",
            "status": "COMPLETED",
            "conclusion": "startup_failure",
        },
        {"name": "running", "status": "IN_PROGRESS", "conclusion": None},
    ]

    blocking = module._blocking_checks(checks)
    pending = module._pending_checks(checks)

    assert [check["name"] for check in blocking] == [
        "failed",
        "cancelled",
        "timed-out",
        "stale",
        "action-required",
        "startup-failure",
    ]
    assert [check["name"] for check in pending] == ["running"]
    assert module.checks_verdict(checks) == "failing"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (True, "mergeable"),
        (False, "conflicting"),
        (None, "unknown"),
        ("unexpected", "unknown"),
    ],
)
def test_mergeability_is_explicit_and_never_boolean_coerced(
    monkeypatch: pytest.MonkeyPatch, raw: object, expected: str
) -> None:
    module = _module(monkeypatch)

    assert module._mergeability({"mergeable": raw}) == expected


def test_sweep_uses_the_single_pull_mergeability_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    pulls = [
        {
            "number": 2,
            "title": "first dev",
            "base": {"ref": "dev"},
            "head": {"ref": "feature/one", "sha": "sha-2"},
            "draft": False,
        },
    ]

    def fake_paginated(path: str, query: str) -> list[dict[str, object]]:
        assert path == "repos/marlon-costa-dc/agents/pulls?state=open&per_page=100"
        assert query == ".[]"
        return pulls

    calls: list[list[str]] = []

    def fake_gh(*arguments: str, input_text: str | None = None) -> str:
        calls.append(list(arguments))
        assert arguments[0] == "api"
        assert arguments[1].startswith("repos/marlon-costa-dc/agents/pulls/")
        return json.dumps({"mergeable": None, "mergeable_state": "unknown"})

    monkeypatch.setattr(module, "_gh_paginated", fake_paginated)
    monkeypatch.setattr(module, "_gh", fake_gh)
    monkeypatch.setattr(
        module,
        "_checks",
        lambda owner, name, ref: [
            {"name": "ci", "status": "COMPLETED", "conclusion": "cancelled"}
        ],
    )
    monkeypatch.setattr(module, "review_threads", lambda *arguments: [])

    queue = module.cmd_sweep(("marlon-costa-dc/agents",), {"dev"})

    assert queue == [
        {
            "repository": "marlon-costa-dc/agents",
            "pr": 2,
            "title": "first dev",
            "base": "dev",
            "head_branch": "feature/one",
            "head_oid": "sha-2",
            "draft": False,
            "mergeability": "unknown",
            "mergeable_state": "unknown",
            "checks_verdict": "failing",
            "check_count": 1,
            "blocking_check_count": 1,
            "pending_check_count": 0,
            "unresolved_threads": 0,
        }
    ]
