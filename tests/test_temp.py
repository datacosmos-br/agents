import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from agents_governance.temp import (
    MARKER,
    TempPolicy,
    create_run,
    findings,
    gc,
    global_findings,
    managed_env,
    managed_temp,
    repository_findings,
    resolve_repo,
    run_command,
)


@pytest.fixture(autouse=True)
def local_storage_manifest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    config = tmp_path / "config" / "environment.d"
    config.mkdir(parents=True, exist_ok=True)
    (config / "storage.toml").write_text(
        "version = 1\n"
        "[policy]\n"
        f'global_temp = "{tmp_path / "ephemeral"}"\n'
        "global_temp_max_bytes = 1073741824\n"
        "repositories = []\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    return config


def git_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    return path


def test_audit_detects_residue_and_preserves_unknown(tmp_path: Path) -> None:
    (tmp_path / "beads-checkpoint").mkdir()
    (tmp_path / "agents-waza-check.test.log").write_text("evidence", encoding="utf-8")
    (tmp_path / "unrelated").mkdir()

    items = findings(tmp_path)

    assert [(item.path.name, item.kind) for item in items] == [
        ("agents-waza-check.test.log", "residue"),
        ("beads-checkpoint", "residue"),
    ]


def test_audit_detects_database_and_classifies_small_lock_as_ephemeral(
    tmp_path: Path,
) -> None:
    (tmp_path / "state.db").write_text("database", encoding="utf-8")
    (tmp_path / "tool.lock").touch()

    items = findings(tmp_path)

    assert [(item.path.name, item.kind) for item in items] == [
        ("state.db", "prohibited"),
        ("tool.lock", "ephemeral"),
    ]


def test_repository_audit_detects_unexpanded_home_directory(tmp_path: Path) -> None:
    literal_home = tmp_path / "$HOME"
    literal_home.mkdir()

    items = repository_findings(tmp_path)

    assert [(item.path, item.kind) for item in items] == [(literal_home, "residue")]


def test_repository_audit_rejects_legacy_archives(tmp_path: Path) -> None:
    archive = tmp_path / ".skills-archive"
    archive.mkdir()

    items = repository_findings(tmp_path)

    assert [(item.path, item.kind) for item in items] == [(archive, "residue")]


def test_managed_temp_uses_machine_authorized_physical_directory(
    tmp_path: Path,
) -> None:
    repo = git_repo(tmp_path / "repo")

    destination = managed_temp(repo)

    assert destination == tmp_path / "ephemeral"
    assert destination.is_dir()
    assert not destination.is_symlink()
    assert destination.stat().st_mode & 0o777 == 0o700


def test_repo_under_system_temp_is_refused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setattr("agents_governance.temp.SYSTEM_TEMP", tmp_path)

    with pytest.raises(RuntimeError, match="repositories under /tmp"):
        resolve_repo(repo)


def test_managed_env_isolates_build_dirs_and_shares_dependency_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    scratch, lock = create_run(repo)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    environment = managed_env(repo, scratch)
    lock.close()

    assert Path(environment["TMPDIR"]).is_relative_to(scratch)
    assert Path(environment["GOTMPDIR"]).is_relative_to(scratch)
    assert Path(environment["GOCACHE"]).is_relative_to(scratch)
    assert environment["GOMODCACHE"] == str(tmp_path / "cache" / "go-mod")


def test_run_records_real_child_exit_and_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    report = run_command(
        ["sh", "-c", 'test "$TMPDIR" != "$GOTMPDIR" && printf data > "$TMPDIR/proof"'],
        repo,
        TempPolicy(poll_seconds=0.01),
    )

    assert report.exit_code == 0
    assert report.scratch_retained is False
    assert not Path(report.scratch).exists()
    evidence = list((tmp_path / "state" / "agents" / "temp" / "reports").glob("*.json"))
    assert json.loads(evidence[0].read_text(encoding="utf-8"))["exit_code"] == 0


def test_run_stops_only_owned_process_group_at_limit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    report = run_command(
        ["sh", "-c", 'head -c 4096 /dev/zero > "$TMPDIR/growth"; sleep 10'],
        repo,
        TempPolicy(warning_bytes=1024, failure_bytes=2048, poll_seconds=0.01),
    )

    assert report.stopped_for_limit is True
    assert report.scratch_retained is True
    assert report.exit_code != 0
    assert report.peak_bytes >= 4096


def test_run_terminates_owned_process_group_when_wrapper_is_terminated(
    tmp_path: Path,
) -> None:
    repo = git_repo(tmp_path / "repo")
    child_pid = tmp_path / "child.pid"
    script = (
        "from pathlib import Path; from agents_governance.temp import run_command; "
        f"raise SystemExit(run_command(['sh','-c','echo $$ > {child_pid}; sleep 30'], Path({str(repo)!r})).exit_code)"
    )
    wrapper = subprocess.Popen([sys.executable, "-c", script])
    for _ in range(100):
        if child_pid.is_file():
            break
        time.sleep(0.02)
    assert child_pid.is_file()
    pid = int(child_pid.read_text(encoding="utf-8"))

    wrapper.terminate()
    assert wrapper.wait(timeout=10) == 128 + 15
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


def test_repeated_signal_cannot_interrupt_owned_group_cleanup(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "repo")
    child_pid = tmp_path / "child.pid"
    script = (
        "from pathlib import Path; from agents_governance.temp import run_command; "
        f"raise SystemExit(run_command(['sh','-c','echo $$ > {child_pid}; trap \\\"\\\" TERM; sleep 30'], Path({str(repo)!r})).exit_code)"
    )
    wrapper = subprocess.Popen([sys.executable, "-c", script])
    for _ in range(100):
        if child_pid.is_file():
            break
        time.sleep(0.02)
    assert child_pid.is_file()
    pid = int(child_pid.read_text(encoding="utf-8"))

    wrapper.send_signal(signal.SIGTERM)
    time.sleep(0.1)
    wrapper.send_signal(signal.SIGTERM)

    assert wrapper.wait(timeout=10) == 128 + int(signal.SIGTERM)
    with pytest.raises(ProcessLookupError):
        os.kill(pid, 0)


def test_gc_preserves_young_unknown_symlink_database_and_locked_runs(
    tmp_path: Path,
) -> None:
    repo = git_repo(tmp_path / "repo")
    policy = TempPolicy(orphan_age_seconds=10)
    old = time.time() - 20

    young, young_lock = create_run(repo)
    unknown, unknown_lock = create_run(repo)
    (unknown / "surprise").write_text("keep", encoding="utf-8")
    symlink, symlink_lock = create_run(repo)
    (symlink / "tmp" / "link").symlink_to(tmp_path)
    database, database_lock = create_run(repo)
    (database / "tmp" / "state.db").write_text("keep", encoding="utf-8")
    active, active_lock = create_run(repo)
    for run in (unknown, symlink, database, active):
        os.utime(run / MARKER, (old, old))
    unknown_lock.close()
    symlink_lock.close()
    database_lock.close()

    eligible, blocked = gc(repo, apply=True, policy=policy)

    assert eligible == []
    assert {item.kind for item in blocked} == {
        "young",
        "unknown",
        "protected",
        "active",
    }
    assert all(path.exists() for path in (young, unknown, symlink, database, active))
    young_lock.close()
    active_lock.close()


def test_gc_removes_only_old_marked_owned_run(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "repo")
    run, lock = create_run(repo)
    lock.close()
    old = time.time() - 20
    os.utime(run / MARKER, (old, old))

    eligible, blocked = gc(repo, apply=True, policy=TempPolicy(orphan_age_seconds=10))

    assert eligible == [run]
    assert blocked == []
    assert not run.exists()


def test_global_audit_uses_only_machine_local_registered_roots(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    config = tmp_path / "config" / "environment.d"
    config.mkdir(parents=True, exist_ok=True)
    (config / "storage.toml").write_text(
        "version = 1\n"
        "[policy]\n"
        f'global_temp = "{tmp_path / "ephemeral"}"\n'
        "global_temp_max_bytes = 16\n"
        "[[repositories]]\n"
        f'path = "{repo}"\n',
        encoding="utf-8",
    )
    ephemeral = tmp_path / "ephemeral"
    ephemeral.mkdir()
    (ephemeral / "growth").write_bytes(b"x" * 17)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setattr("agents_governance.temp.SYSTEM_TEMP", tmp_path / "system-tmp")

    items = global_findings()

    assert [(item.path, item.kind) for item in items] == [(ephemeral, "prohibited")]
