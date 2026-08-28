"""Injected-failure coverage for repository-owned bins and hooks."""

from __future__ import annotations

import io
import json
import os
import runpy
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _write_executable(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(0o700)


def _run_hook(
    name: str,
    payload: dict[str, object],
    *,
    cwd: Path,
    path: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/usr/bin/bash", str(ROOT / "hooks" / name)],
        input=json.dumps(payload),
        cwd=cwd,
        env={**os.environ, "PATH": path},
        text=True,
        capture_output=True,
        check=False,
    )


def _rust_project(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "project"
    source = project / "src"
    source.mkdir(parents=True)
    (project / "Cargo.toml").write_text("[workspace]\n", encoding="utf-8")
    edited = source / "lib.rs"
    edited.write_text("pub fn value() -> u8 { 1 }\n", encoding="utf-8")
    return project, edited


def test_post_edit_blocks_on_cargo_nonzero_without_keyword_error(
    tmp_path: Path,
) -> None:
    project, edited = _rust_project(tmp_path)
    tools = tmp_path / "tools"
    _write_executable(
        tools / "cargo",
        "#!/usr/bin/bash\nprintf 'linker unavailable\\n' >&2\nexit 42\n",
    )

    result = _run_hook(
        "post-edit-validate.sh",
        {"tool_name": "Edit", "tool_input": {"file_path": str(edited)}},
        cwd=project,
        path=f"{tools}:/usr/bin:/bin",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    decision = json.loads(result.stdout)
    assert decision["decision"] == "block"
    assert "cargo check" in decision["reason"]
    assert "failed (exit 42)" in decision["reason"]
    assert "exit 42" in decision["reason"]
    assert "linker unavailable" in decision["reason"]


def test_post_edit_blocks_when_required_validator_is_unavailable(
    tmp_path: Path,
) -> None:
    project, edited = _rust_project(tmp_path)

    result = _run_hook(
        "post-edit-validate.sh",
        {"tool_name": "Edit", "tool_input": {"file_path": str(edited)}},
        cwd=project,
        path="/usr/bin:/bin",
    )

    assert result.returncode == 0
    assert result.stderr == ""
    decision = json.loads(result.stdout)
    assert decision["decision"] == "block"
    assert "cargo is unavailable" in decision["reason"]


def test_post_edit_non_applicable_tool_is_a_silent_success(tmp_path: Path) -> None:
    result = _run_hook(
        "post-edit-validate.sh",
        {"tool_name": "Read", "tool_input": {}},
        cwd=tmp_path,
        path="/usr/bin:/bin",
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_recursive_stop_hook_is_an_intentional_silent_success(tmp_path: Path) -> None:
    result = _run_hook(
        "quality-gate.sh",
        {"stop_hook_active": True},
        cwd=tmp_path,
        path="/usr/bin:/bin",
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def _git_tool(path: Path, *, branch_status: int = 0, worktree_status: int = 0) -> None:
    _write_executable(
        path,
        f"""#!/usr/bin/bash
case "$*" in
  "rev-parse --is-inside-work-tree") printf 'true\\n' ;;
  "branch --show-current"|"rev-parse --abbrev-ref HEAD"|"symbolic-ref --quiet --short HEAD")
    if [[ {branch_status} -ne 0 ]]; then
      printf 'branch metadata unavailable\\n' >&2
      exit {branch_status}
    fi
    printf 'dev\\n'
    ;;
  "rev-parse --show-toplevel") printf '%s\\n' "$FAKE_REPOSITORY" ;;
  "status --porcelain=v1 --untracked-files=normal")
    if [[ {worktree_status} -ne 0 ]]; then
      printf 'worktree metadata unavailable\\n' >&2
      exit {worktree_status}
    fi
    ;;
  *) printf 'unexpected git invocation: %s\\n' "$*" >&2; exit 90 ;;
esac
""",
    )


def _run_session_hook(project: Path, tools: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["/usr/bin/bash", str(ROOT / "hooks" / "session-init.sh")],
        input="{}",
        cwd=project,
        env={
            **os.environ,
            "FAKE_REPOSITORY": str(project),
            "PATH": f"{tools}:/usr/bin:/bin",
        },
        text=True,
        capture_output=True,
        check=False,
    )


def test_session_init_preserves_branch_query_failure(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    tools = tmp_path / "tools"
    _git_tool(tools / "git", branch_status=42)

    result = _run_session_hook(project, tools)

    assert result.returncode == 42
    assert result.stdout == ""
    assert "branch metadata unavailable" in result.stderr


def test_session_init_never_reports_clean_after_status_failure(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    tools = tmp_path / "tools"
    _git_tool(tools / "git", worktree_status=43)

    result = _run_session_hook(project, tools)

    assert result.returncode == 43
    assert result.stdout == ""
    assert "worktree metadata unavailable" in result.stderr


def test_session_init_outside_repository_is_a_silent_success(tmp_path: Path) -> None:
    tools = tmp_path / "tools"
    _write_executable(
        tools / "git",
        "#!/usr/bin/bash\nprintf 'not a repository\\n' >&2\nexit 128\n",
    )

    result = _run_session_hook(tmp_path, tools)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def _keyring_namespace() -> dict[str, Any]:
    return runpy.run_module("agents_governance.keyring")


def test_headless_lookup_preserves_secret_tool_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = _keyring_namespace()
    lookup = namespace["lookup"]
    keyring_error = cast(type[Exception], namespace["KeyringError"])
    assert callable(lookup)
    lookup.__globals__["Secret"] = None
    lookup.__globals__["SECRET_SCHEMA"] = None
    monkeypatch.setenv("DBUS_SESSION_BUS_ADDRESS", "unix:path=/test")

    def fail_lookup(
        *_args: object, **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=["secret-tool"],
            returncode=9,
            stdout="",
            stderr="collection is locked",
        )

    monkeypatch.setattr(subprocess, "run", fail_lookup)

    with pytest.raises(
        keyring_error,
        match=r"secret-tool lookup failed \(exit 9\): collection is locked",
    ):
        lookup("test", "TOKEN")


def test_headless_lookup_preserves_explicit_missing_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    namespace = _keyring_namespace()
    lookup = namespace["lookup"]
    keyring_error = cast(type[Exception], namespace["KeyringError"])
    assert callable(lookup)
    lookup.__globals__["Secret"] = None
    lookup.__globals__["SECRET_SCHEMA"] = None
    monkeypatch.setenv("DBUS_SESSION_BUS_ADDRESS", "unix:path=/test")

    def missing(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=["secret-tool"], returncode=1, stdout="", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", missing)

    with pytest.raises(keyring_error, match="missing secret: TOKEN"):
        lookup("test", "TOKEN")


def test_store_preserves_secret_tool_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    namespace = _keyring_namespace()
    store = namespace["store"]
    keyring_error = cast(type[Exception], namespace["KeyringError"])
    assert callable(store)
    store.__globals__["profile_config"] = lambda _profile: {"variables": ["TOKEN"]}
    store.__globals__["EVENTS"] = tmp_path / "events.jsonl"
    monkeypatch.setattr(store.__globals__["sys"], "stdin", io.StringIO("value\n"))

    def fail_store(
        *_args: object, **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=["secret-tool"],
            returncode=7,
            stdout="",
            stderr="collection is locked",
        )

    monkeypatch.setattr(subprocess, "run", fail_store)

    with pytest.raises(
        keyring_error,
        match=r"secret-tool store failed \(exit 7\): collection is locked",
    ):
        store("test", "TOKEN", True)


def test_remove_exposes_nonzero_secret_tool_stderr(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    namespace = _keyring_namespace()
    remove = namespace["remove"]
    assert callable(remove)
    remove.__globals__["profile_config"] = lambda _profile: {
        "variables": ["TOKEN"],
        "aliases": {},
    }
    remove.__globals__["EVENTS"] = tmp_path / "events.jsonl"

    def fail_remove(
        *_args: object, **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=["secret-tool"],
            returncode=6,
            stdout="",
            stderr="collection is locked",
        )

    monkeypatch.setattr(subprocess, "run", fail_remove)

    assert remove("test", "TOKEN", True) == 6
    assert "secret-tool clear failed (exit 6): collection is locked" in (
        capsys.readouterr().err
    )


def test_exec_event_is_not_published_as_success_before_execvpe(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    namespace = _keyring_namespace()
    execute = namespace["execute"]
    assert callable(execute)
    execute.__globals__["profile_config"] = lambda _profile: {"variables": []}
    execute.__globals__["authorize_consumer"] = lambda *_args: None
    execute.__globals__["fetch_all"] = lambda *_args: {}
    execute.__globals__["manifest"] = dict
    execute.__globals__["EVENTS"] = tmp_path / "events.jsonl"

    def fail_execvpe(*_args: object, **_kwargs: object) -> None:
        raise FileNotFoundError("command is unavailable")

    monkeypatch.setattr(execute.__globals__["os"], "execvpe", fail_execvpe)

    with pytest.raises(FileNotFoundError, match="command is unavailable"):
        execute("test", "agent:test", ["missing-command"])

    events = [
        json.loads(line)
        for line in (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [item["result"] for item in events] == ["dispatch"]
