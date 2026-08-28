import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

import agents_governance.temp as temp_module
from agents_governance.temp import (
    MARKER,
    RunReport,
    TempPolicy,
    _write_report,
    create_run,
    findings,
    gc,
    global_findings,
    managed_env,
    managed_temp,
    repository_findings,
    resolve_repo,
    run_command,
    storage_manifest,
)


def storage_manifest_text(
    shell_temp: Path,
    *,
    repositories: tuple[Path, ...] = (),
    policy: dict[str, int | float] | None = None,
) -> str:
    values: dict[str, int | float] = {
        "shell_temp_max_bytes": 1 << 30,
        "report_max_bytes": 10 << 20,
        "warning_bytes": 1 << 30,
        "failure_bytes": 5 << 30,
        "orphan_age_days": 7,
        "poll_seconds": 0.01,
        "termination_grace_seconds": 0.1,
    }
    if policy is not None:
        values.update(policy)
    lines = ["version = 2"]
    if repositories:
        for repository in repositories:
            lines.extend(("[[repositories]]", f'path = "{repository}"'))
    else:
        lines.append("repositories = []")
    lines.extend(("", "[policy]", f'shell_temp = "{shell_temp}"'))
    lines.extend(f"{name} = {value}" for name, value in values.items())
    return "\n".join(lines) + "\n"


def temp_policy(**overrides: float) -> TempPolicy:
    values: dict[str, float] = {
        "warning_bytes": 1 << 30,
        "failure_bytes": 5 << 30,
        "orphan_age_seconds": 7 * 24 * 60 * 60,
        "poll_seconds": 0.01,
        "termination_grace_seconds": 0.1,
    }
    values.update(overrides)
    return TempPolicy(
        warning_bytes=int(values["warning_bytes"]),
        failure_bytes=int(values["failure_bytes"]),
        orphan_age_seconds=int(values["orphan_age_seconds"]),
        poll_seconds=float(values["poll_seconds"]),
        termination_grace_seconds=float(values["termination_grace_seconds"]),
    )


@pytest.fixture(autouse=True)
def local_storage_manifest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    config = tmp_path / "config" / "environment.d"
    config.mkdir(parents=True, exist_ok=True)
    (config / "storage.toml").write_text(
        storage_manifest_text(tmp_path / "shell-tmp"), encoding="utf-8"
    )
    manifest = config / "storage.toml"
    monkeypatch.setenv("AGENTS_STORAGE_CONFIG", str(manifest))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return manifest


def test_storage_manifest_requires_explicit_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AGENTS_STORAGE_CONFIG")

    with pytest.raises(RuntimeError, match="AGENTS_STORAGE_CONFIG is required"):
        storage_manifest()


def test_storage_manifest_rejects_relative_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENTS_STORAGE_CONFIG", "config/storage.toml")

    with pytest.raises(RuntimeError, match="must be an absolute path"):
        storage_manifest()


def test_storage_manifest_is_typed_and_owns_every_operational_threshold(
    local_storage_manifest: Path,
) -> None:
    manifest = storage_manifest()

    assert manifest.version == 2
    assert manifest.repositories == ()
    assert manifest.policy.shell_temp_max_bytes == 1 << 30
    assert manifest.policy.report_max_bytes == 10 << 20
    assert manifest.policy.temp == temp_policy()
    assert local_storage_manifest.is_file()


def test_storage_manifest_rejects_repository_list_nested_under_policy(
    local_storage_manifest: Path,
) -> None:
    malformed = storage_manifest_text(local_storage_manifest.parent / "shell").replace(
        "repositories = []\n\n[policy]\n", "[policy]\n"
    )
    local_storage_manifest.write_text(
        malformed + "repositories = []\n", encoding="utf-8"
    )

    with pytest.raises(RuntimeError, match="storage schema mismatch"):
        storage_manifest()


@pytest.mark.parametrize(
    ("old", "new", "message"),
    (
        ("version = 2", "version = 1", "storage.version"),
        ("report_max_bytes = 10485760", "report_max_bytes = true", "positive integer"),
        ("orphan_age_days = 7", "orphan_age_days = 6", "at least 7"),
        ("warning_bytes = 1073741824", "warning_bytes = 5368709120", "lower than"),
        ("poll_seconds = 0.01", "poll_seconds = 1.0", "must not exceed"),
    ),
)
def test_storage_manifest_rejects_invalid_types_and_thresholds(
    local_storage_manifest: Path,
    old: str,
    new: str,
    message: str,
) -> None:
    rendered = local_storage_manifest.read_text(encoding="utf-8")
    local_storage_manifest.write_text(rendered.replace(old, new), encoding="utf-8")

    with pytest.raises(RuntimeError, match=message):
        storage_manifest()


def test_storage_manifest_rejects_missing_and_extra_policy_keys(
    local_storage_manifest: Path,
) -> None:
    rendered = local_storage_manifest.read_text(encoding="utf-8")
    local_storage_manifest.write_text(
        rendered.replace("report_max_bytes = 10485760\n", "") + "unknown = 1\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="storage.policy schema mismatch"):
        storage_manifest()


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


def test_audit_fails_when_the_requested_temp_root_is_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        findings(missing)


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


def test_managed_temp_uses_repository_owned_physical_directory(
    tmp_path: Path,
) -> None:
    repo = git_repo(tmp_path / "repo")

    destination = managed_temp(repo)

    assert destination == repo / ".test-tmp"
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
    assert Path(environment["CARGO_TARGET_DIR"]).is_relative_to(scratch)
    assert environment["GOMODCACHE"] == str(tmp_path / "cache" / "go-mod")


@pytest.mark.parametrize(
    ("name", "value"),
    (("HOME", "$HOME"), ("HOME", "relative-home"), ("XDG_CACHE_HOME", ".cache")),
)
def test_managed_env_rejects_unexpanded_or_relative_storage_roots_before_writes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    name: str,
    value: str,
) -> None:
    repo = git_repo(tmp_path / "repo")
    scratch, lock = create_run(repo)
    monkeypatch.setenv(name, value)

    with pytest.raises(RuntimeError, match=f"{name} must be an expanded absolute path"):
        managed_env(repo, scratch)

    lock.close()
    assert not (repo / "$HOME").exists()


def test_create_run_failure_removes_the_partial_owned_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    original_mkdir = temp_module._mkdir

    def fail_known_directory(path: Path) -> Path:
        if path.name == "node":
            raise OSError("injected run setup failure")
        return original_mkdir(path)

    monkeypatch.setattr(temp_module, "_mkdir", fail_known_directory)

    with pytest.raises(OSError, match="injected run setup failure"):
        create_run(repo)

    assert list((repo / ".test-tmp").glob("run.*")) == []


def test_run_records_real_child_exit_and_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    report = run_command(
        ["sh", "-c", 'test "$TMPDIR" != "$GOTMPDIR" && printf data > "$TMPDIR/proof"'],
        repo,
        temp_policy(),
    )

    assert report.exit_code == 0
    assert report.scratch_retained is False
    assert not Path(report.scratch).exists()
    evidence = list((tmp_path / "state" / "agents" / "temp" / "reports").glob("*.json"))
    assert json.loads(evidence[0].read_text(encoding="utf-8"))["exit_code"] == 0


def test_run_without_test_override_enforces_the_manifest_policy(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    local_storage_manifest: Path,
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    local_storage_manifest.write_text(
        storage_manifest_text(
            tmp_path / "shell-tmp",
            policy={"warning_bytes": 1024, "failure_bytes": 2048},
        ),
        encoding="utf-8",
    )

    report = run_command(
        ["sh", "-c", 'head -c 4096 /dev/zero > "$TMPDIR/growth"; sleep 10'],
        repo,
    )

    assert report.warning_bytes == 1024
    assert report.failure_bytes == 2048
    assert report.stopped_for_limit is True
    assert report.exit_code != 0
    assert report.scratch_retained is True


def test_exhausted_report_capacity_stops_before_child_and_preserves_evidence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    local_storage_manifest: Path,
) -> None:
    repo = git_repo(tmp_path / "repo")
    state = tmp_path / "state"
    reports = state / "agents" / "temp" / "reports"
    reports.mkdir(parents=True)
    evidence = reports / "operator-evidence.txt"
    evidence.write_text("preserve", encoding="utf-8")
    proof = tmp_path / "child-started"
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    local_storage_manifest.write_text(
        storage_manifest_text(tmp_path / "shell-tmp", policy={"report_max_bytes": 1}),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="report store capacity exhausted"):
        run_command(["touch", str(proof)], repo)

    assert evidence.read_text(encoding="utf-8") == "preserve"
    assert not proof.exists()
    assert not (repo / ".test-tmp").exists()


def test_report_payload_over_capacity_retains_current_scratch_evidence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    local_storage_manifest: Path,
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    local_storage_manifest.write_text(
        storage_manifest_text(tmp_path / "shell-tmp", policy={"report_max_bytes": 1}),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="report store capacity exceeded"):
        run_command(["true"], repo)

    retained = list((repo / ".test-tmp").glob("run.*"))
    assert len(retained) == 1
    assert (retained[0] / MARKER).is_file()


def test_report_failure_publishes_neither_success_marker_nor_partial_tsv(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    report = RunReport(
        command=("true",),
        repo=str(tmp_path),
        scratch=str(tmp_path / "scratch"),
        started_at="2026-01-01T00:00:00+00:00",
        finished_at="2026-01-01T00:00:01+00:00",
        exit_code=0,
        peak_bytes=0,
        warning_bytes=1,
        failure_bytes=2,
        stopped_for_limit=False,
        scratch_retained=False,
    )
    original_replace = Path.replace

    def fail_json_commit(source: Path, destination: Path) -> Path:
        if source.name.endswith(".candidate") and destination.suffix == ".json":
            raise OSError("injected JSON commit failure")
        return original_replace(source, destination)

    monkeypatch.setattr(Path, "replace", fail_json_commit)

    with pytest.raises(OSError, match="injected JSON commit failure"):
        _write_report(report)

    reports = tmp_path / "state" / "agents" / "temp" / "reports"
    assert list(reports.glob("*.json")) == []
    assert list(reports.glob("*.tsv")) == []
    assert len(list(reports.glob("*.candidate"))) == 2


def test_spawn_failure_removes_the_unstarted_owned_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    missing = tmp_path / "missing-executable"

    with pytest.raises(FileNotFoundError):
        run_command([str(missing)], repo, temp_policy())

    assert list((repo / ".test-tmp").glob("run.*")) == []


def test_monitor_failure_terminates_the_owned_process_group_and_preserves_cause(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    child_pid = tmp_path / "child.pid"
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    def fail_size_probe(_path: Path) -> int:
        deadline = time.monotonic() + 5
        while not child_pid.is_file() and time.monotonic() < deadline:
            time.sleep(0.01)
        raise PermissionError("injected size probe failure")

    monkeypatch.setattr(temp_module, "_tree_size", fail_size_probe)
    owned_pid: int | None = None
    try:
        with pytest.raises(PermissionError, match="injected size probe failure"):
            run_command(
                ["sh", "-c", f"echo $$ > {child_pid}; sleep 30"],
                repo,
                temp_policy(),
            )
        assert child_pid.is_file()
        owned_pid = int(child_pid.read_text(encoding="utf-8"))
        with pytest.raises(ProcessLookupError):
            os.kill(owned_pid, 0)
    finally:
        if owned_pid is not None:
            try:
                os.killpg(owned_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_successful_run_retains_scratch_containing_symlink(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    report = run_command(
        ["sh", "-c", 'ln -s "$HOME" "$TMPDIR/link"'],
        repo,
        temp_policy(),
    )

    assert report.exit_code == 70
    assert report.scratch_retained is True
    assert Path(report.scratch, "link").is_symlink()
    Path(report.scratch, "link").unlink()


def test_run_stops_only_owned_process_group_at_limit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))

    external = subprocess.Popen(["sleep", "30"])
    try:
        report = run_command(
            ["sh", "-c", 'head -c 4096 /dev/zero > "$TMPDIR/growth"; sleep 10'],
            repo,
            temp_policy(warning_bytes=1024, failure_bytes=2048),
        )

        assert external.poll() is None
    finally:
        external.terminate()
        external.wait(timeout=5)

    assert report.stopped_for_limit is True
    assert report.scratch_retained is True
    assert report.exit_code != 0
    assert report.peak_bytes >= 4096


@pytest.mark.parametrize(
    "signum", (signal.SIGINT, signal.SIGTERM), ids=("sigint", "sigterm")
)
def test_run_terminates_owned_process_group_when_wrapper_is_signaled(
    signum: signal.Signals,
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

    wrapper.send_signal(signum)
    assert wrapper.wait(timeout=10) == 128 + int(signum)
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


def test_termination_reaps_descendant_after_group_leader_exits(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "repo")
    leader_pid = tmp_path / "leader.pid"
    child_pid = tmp_path / "child.pid"
    descendant_script = (
        "import os, signal, time; from pathlib import Path; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        f"Path({str(child_pid)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    leader_script = (
        "import os, subprocess, sys, time; from pathlib import Path; "
        f"Path({str(leader_pid)!r}).write_text(str(os.getpid())); "
        f"subprocess.Popen([sys.executable, '-c', {descendant_script!r}]); "
        "time.sleep(30)"
    )
    script = (
        "from pathlib import Path; "
        "from agents_governance.temp import TempPolicy, run_command; "
        f"raise SystemExit(run_command([{sys.executable!r},'-c',{leader_script!r}], "
        f"Path({str(repo)!r}), TempPolicy(warning_bytes={1 << 30}, "
        f"failure_bytes={5 << 30}, orphan_age_seconds={7 * 24 * 60 * 60}, "
        "poll_seconds=0.01, termination_grace_seconds=0.1)).exit_code)"
    )
    external = subprocess.Popen(["sleep", "30"])
    wrapper = subprocess.Popen([sys.executable, "-c", script])
    owned_group: int | None = None
    try:
        for _ in range(100):
            if leader_pid.is_file() and child_pid.is_file():
                break
            time.sleep(0.02)
        assert leader_pid.is_file()
        assert child_pid.is_file()
        owned_group = int(leader_pid.read_text(encoding="utf-8"))
        descendant = int(child_pid.read_text(encoding="utf-8"))

        wrapper.send_signal(signal.SIGTERM)

        assert wrapper.wait(timeout=10) == 128 + int(signal.SIGTERM)
        with pytest.raises(ProcessLookupError):
            os.kill(descendant, 0)
        assert external.poll() is None
    finally:
        if wrapper.poll() is None:
            wrapper.kill()
            wrapper.wait(timeout=5)
        if owned_group is not None:
            try:
                os.killpg(owned_group, signal.SIGKILL)
            except ProcessLookupError:
                pass
        external.terminate()
        external.wait(timeout=5)


def test_monitor_cancellation_terminates_entire_owned_process_group(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    leader_pid = tmp_path / "leader.pid"
    child_pid = tmp_path / "child.pid"
    descendant_script = (
        "import os, signal, time; from pathlib import Path; "
        "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
        f"Path({str(child_pid)!r}).write_text(str(os.getpid())); time.sleep(30)"
    )
    leader_script = (
        "import os, subprocess, sys, time; from pathlib import Path; "
        f"Path({str(leader_pid)!r}).write_text(str(os.getpid())); "
        f"subprocess.Popen([sys.executable, '-c', {descendant_script!r}]); "
        "time.sleep(30)"
    )

    def cancel_when_group_is_running(_path: Path) -> int:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if leader_pid.is_file() and child_pid.is_file():
                raise asyncio.CancelledError
            time.sleep(0.01)
        pytest.fail("owned process group did not start before cancellation")

    monkeypatch.setattr(temp_module, "_tree_size", cancel_when_group_is_running)
    external = subprocess.Popen(["sleep", "30"])
    owned_group: int | None = None
    try:
        with pytest.raises(asyncio.CancelledError):
            run_command(
                [sys.executable, "-c", leader_script],
                repo,
                temp_policy(),
            )

        assert leader_pid.is_file()
        assert child_pid.is_file()
        owned_group = int(leader_pid.read_text(encoding="utf-8"))
        descendant = int(child_pid.read_text(encoding="utf-8"))
        with pytest.raises(ProcessLookupError):
            os.kill(owned_group, 0)
        with pytest.raises(ProcessLookupError):
            os.kill(descendant, 0)
        assert external.poll() is None
    finally:
        if owned_group is None and leader_pid.is_file():
            owned_group = int(leader_pid.read_text(encoding="utf-8"))
        if owned_group is not None:
            try:
                os.killpg(owned_group, signal.SIGKILL)
            except ProcessLookupError:
                pass
        external.terminate()
        external.wait(timeout=5)


def test_gc_preserves_young_unknown_symlink_database_and_locked_runs(
    tmp_path: Path,
) -> None:
    repo = git_repo(tmp_path / "repo")
    policy = temp_policy(orphan_age_seconds=10)
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
    (symlink / "tmp" / "link").unlink()
    young_lock.close()
    active_lock.close()


def test_gc_removes_only_old_marked_owned_run(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "repo")
    run, lock = create_run(repo)
    lock.close()
    old = time.time() - 20
    os.utime(run / MARKER, (old, old))

    eligible, blocked = gc(repo, apply=True, policy=temp_policy(orphan_age_seconds=10))

    assert eligible == [run]
    assert blocked == []
    assert not run.exists()


def test_gc_without_test_override_enforces_manifest_orphan_retention(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    run, lock = create_run(repo)
    lock.close()
    now = time.time()
    six_days_old = now - 6 * 24 * 60 * 60
    os.utime(run / MARKER, (six_days_old, six_days_old))

    eligible, blocked = gc(repo, apply=True, now=now)

    assert eligible == []
    assert [(item.path, item.kind) for item in blocked] == [(run, "young")]
    assert run.is_dir()

    eight_days_old = now - 8 * 24 * 60 * 60
    os.utime(run / MARKER, (eight_days_old, eight_days_old))
    eligible, blocked = gc(repo, apply=True, now=now)

    assert eligible == [run]
    assert blocked == []
    assert not run.exists()


def test_gc_fails_closed_on_malformed_report_and_preserves_owned_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    state = tmp_path / "state"
    reports = state / "agents" / "temp" / "reports"
    reports.mkdir(parents=True)
    (reports / "broken.json").write_text("{", encoding="utf-8")
    (reports / "broken.tsv").write_text("broken\n", encoding="utf-8")
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    run, lock = create_run(repo)
    lock.close()
    old = time.time() - 8 * 24 * 60 * 60
    os.utime(run / MARKER, (old, old))

    with pytest.raises(RuntimeError, match="invalid run report"):
        gc(repo, apply=True)

    assert run.is_dir()


def test_gc_fails_closed_on_report_projection_drift_and_preserves_owned_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    state = tmp_path / "state"
    monkeypatch.setenv("XDG_STATE_HOME", str(state))
    run, lock = create_run(repo)
    lock.close()
    old = time.time() - 8 * 24 * 60 * 60
    os.utime(run / MARKER, (old, old))
    _write_report(
        RunReport(
            command=("true",),
            repo=str(repo),
            scratch=str(run),
            started_at="2026-01-01T00:00:00+00:00",
            finished_at="2026-01-01T00:00:01+00:00",
            exit_code=0,
            peak_bytes=0,
            warning_bytes=1,
            failure_bytes=2,
            stopped_for_limit=False,
            scratch_retained=True,
        )
    )
    tsv = next((state / "agents" / "temp" / "reports").glob("*.tsv"))
    tsv.write_text("drift\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="JSON/TSV drift"):
        gc(repo, apply=True)

    assert run.is_dir()


def test_gc_reports_marker_owned_by_a_different_repository(tmp_path: Path) -> None:
    repo = git_repo(tmp_path / "repo")
    run, lock = create_run(repo)
    lock.close()
    marker = run / MARKER
    payload = json.loads(marker.read_text(encoding="utf-8"))
    payload["repo"] = str(tmp_path / "different-repository")
    marker.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    eligible, blocked = gc(repo, apply=True)

    assert eligible == []
    assert [(finding.kind, finding.message) for finding in blocked] == [
        ("unknown", "preserve: marker repository does not match scratch owner")
    ]
    assert run.is_dir()


def test_global_audit_uses_only_machine_local_registered_roots(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = git_repo(tmp_path / "repo")
    config = tmp_path / "config" / "environment.d"
    config.mkdir(parents=True, exist_ok=True)
    (config / "storage.toml").write_text(
        storage_manifest_text(
            tmp_path / "shell-tmp",
            repositories=(repo,),
            policy={"shell_temp_max_bytes": 16},
        ),
        encoding="utf-8",
    )
    shell_temp = tmp_path / "shell-tmp"
    shell_temp.mkdir()
    (shell_temp / "growth").write_bytes(b"x" * 17)
    system_temp = tmp_path / "system-tmp"
    system_temp.mkdir()
    monkeypatch.setenv("AGENTS_STORAGE_CONFIG", str(config / "storage.toml"))
    monkeypatch.setattr("agents_governance.temp.SYSTEM_TEMP", system_temp)

    items = global_findings()

    assert [(item.path, item.kind) for item in items] == [(shell_temp, "prohibited")]


def test_global_audit_reports_canonical_report_store_limit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    local_storage_manifest: Path,
) -> None:
    reports = tmp_path / "state" / "agents" / "temp" / "reports"
    reports.mkdir(parents=True)
    (reports / "evidence.json").write_bytes(b"x" * 17)
    local_storage_manifest.write_text(
        storage_manifest_text(tmp_path / "shell-tmp", policy={"report_max_bytes": 16}),
        encoding="utf-8",
    )
    system_temp = tmp_path / "system-tmp"
    system_temp.mkdir()
    monkeypatch.setattr("agents_governance.temp.SYSTEM_TEMP", system_temp)

    items = global_findings()

    assert [(item.path, item.kind, item.size_bytes) for item in items] == [
        (reports, "prohibited", 17)
    ]
