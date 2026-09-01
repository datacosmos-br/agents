from __future__ import annotations

import json
import sys
from pathlib import Path
from types import ModuleType

import pytest
from source_loader import load_source_module


def _module(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    path = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "tool"
        / "pr-sheriff"
        / "scripts"
        / "pr_triage.py"
    )
    module = load_source_module("pr_triage_under_test", path)
    sys.modules[module.__name__] = module
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

    checks = module._checks("datacosmos-br", "agents", "head-sha")

    assert checks == [{"name": "check"}]
    assert calls == [
        [
            "api",
            "--paginate",
            "repos/datacosmos-br/agents/commits/head-sha/check-runs?per_page=100",
            "-q",
            ".check_runs[] | {name:.name,status:.status,conclusion:.conclusion}",
        ]
    ]


def test_gh_propagates_child_exit_code_and_stderr(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _module(monkeypatch)
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *_args, **_kwargs: module.subprocess.CompletedProcess(
            args=("gh", "api"), returncode=7, stdout="", stderr="provider failed\n"
        ),
    )

    with pytest.raises(SystemExit) as raised:
        module._gh("api", "repos/owner/repo")

    assert raised.value.code == 7
    assert capsys.readouterr().err == "provider failed\n"


def test_public_repository_does_not_select_private_access_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    monkeypatch.setattr(
        module,
        "_gh",
        lambda *_args, **_kwargs: json.dumps(
            {"private": False, "permissions": {"push": True}}
        ),
    )
    monkeypatch.setattr(
        module,
        "_external",
        lambda *_args: pytest.fail("dormant private access capability was probed"),
    )

    result = module.managed_private_access("datacosmos-br/public", "push", None)

    assert result["access_preflight"] == "not_selected"


def test_managed_private_access_requires_account_alias_and_exact_permission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    monkeypatch.setattr(
        module,
        "_gh",
        lambda *_args, **_kwargs: json.dumps(
            {"private": True, "permissions": {"pull": True, "push": True}}
        ),
    )

    with pytest.raises(ValueError, match="declared SSH host alias"):
        module.managed_private_access(
            "datacosmos-br/agents",
            "push",
            "git@github.com:datacosmos-br/agents.git",
        )
    with pytest.raises(PermissionError, match="admin"):
        module.managed_private_access(
            "datacosmos-br/agents",
            "admin",
            "git@github-dc:datacosmos-br/agents.git",
        )


def test_managed_private_access_proves_gh_and_exact_ssh_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(
        module,
        "_gh",
        lambda *_args, **_kwargs: json.dumps(
            {"private": True, "permissions": {"push": True}}
        ),
    )

    def record_external(*args: str) -> str:
        calls.append(args)
        return "proved"

    monkeypatch.setattr(module, "_external", record_external)

    result = module.managed_private_access(
        "marlon-costa-dc/private", "push", "git@github-dc:marlon-costa-dc/private.git"
    )

    assert result == {
        "repository": "marlon-costa-dc/private",
        "private_managed": True,
        "effect": "push",
        "access_preflight": "passed",
        "permission": "push",
        "ssh_host_alias": "github-dc",
    }
    assert calls == [
        ("gh", "auth", "status", "--active", "--hostname", "github.com"),
        ("git", "ls-remote", "git@github-dc:marlon-costa-dc/private.git", "HEAD"),
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
        assert path == "repos/datacosmos-br/agents/pulls?state=open&per_page=100"
        assert query == ".[]"
        return pulls

    calls: list[list[str]] = []

    def fake_gh(*arguments: str, input_text: str | None = None) -> str:
        calls.append(list(arguments))
        assert arguments[0] == "api"
        assert arguments[1].startswith("repos/datacosmos-br/agents/pulls/")
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

    queue = module.cmd_sweep(("datacosmos-br/agents",), {"dev"})

    assert queue == [
        {
            "repository": "datacosmos-br/agents",
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


def test_landing_gate_reports_every_blocker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    inventory = {
        "base": "dev",
        "head_oid": "head-sha",
        "state": "open",
        "draft": False,
        "mergeability": "mergeable",
        "mergeable_state": "unstable",
        "checks_verdict": "passed",
        "unresolved_threads": [{"thread_id": "thread-1"}],
    }

    assert module.landing_blockers(inventory, "dev", "head-sha") == [
        "mergeable_state is unstable",
        "1 review thread(s) unresolved",
    ]


def test_landing_gate_accepts_only_clean_completed_inventory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    inventory = {
        "base": "dev",
        "head_oid": "head-sha",
        "state": "open",
        "draft": False,
        "mergeability": "mergeable",
        "mergeable_state": "clean",
        "checks_verdict": "passed",
        "unresolved_threads": [],
    }

    assert module.landing_blockers(inventory, "dev", "head-sha") == []


def test_landing_gate_binds_authorized_base_and_head(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module(monkeypatch)
    inventory = {
        "base": "main",
        "head_oid": "changed-head",
        "state": "open",
        "draft": False,
        "mergeability": "mergeable",
        "mergeable_state": "clean",
        "checks_verdict": "passed",
        "unresolved_threads": [],
    }

    assert module.landing_blockers(inventory, "dev", "authorized-head") == [
        "base is main, expected authorized base dev",
        "head_oid is changed-head, expected authorized head authorized-head",
    ]


def test_gate_command_exits_nonzero_after_printing_blockers(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _module(monkeypatch)
    inventory = {
        "base": "dev",
        "head_oid": "head-sha",
        "state": "open",
        "draft": False,
        "mergeability": "mergeable",
        "mergeable_state": "clean",
        "checks_verdict": "pending",
        "unresolved_threads": [],
    }
    monkeypatch.setattr(module, "cmd_locate", lambda repository, number: inventory)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pr_triage.py",
            "gate",
            "owner/repo",
            "25",
            "--base",
            "dev",
            "--head",
            "head-sha",
        ],
    )

    with pytest.raises(SystemExit) as raised:
        module.main()

    assert raised.value.code == 1
    output = json.loads(capsys.readouterr().out)
    assert output["landing_verdict"] == "blocked"
    assert output["landing_blockers"] == ["checks_verdict is pending"]


def test_gate_command_returns_normally_for_clean_inventory(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = _module(monkeypatch)
    inventory = {
        "base": "dev",
        "head_oid": "head-sha",
        "state": "open",
        "draft": False,
        "mergeability": "mergeable",
        "mergeable_state": "clean",
        "checks_verdict": "passed",
        "unresolved_threads": [],
    }
    monkeypatch.setattr(module, "cmd_locate", lambda repository, number: inventory)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pr_triage.py",
            "gate",
            "owner/repo",
            "25",
            "--base",
            "dev",
            "--head",
            "head-sha",
        ],
    )

    assert module.main() is None
    output = json.loads(capsys.readouterr().out)
    assert output["landing_verdict"] == "passed"
    assert output["landing_blockers"] == []
