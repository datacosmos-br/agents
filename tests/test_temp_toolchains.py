from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agents_governance.temp import TempPolicy, run_command

FAST_POLICY = TempPolicy(poll_seconds=0.01)


def _git_repo(path: Path) -> Path:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    return path


def test_two_go_tests_use_distinct_owned_runs(monkeypatch, tmp_path: Path) -> None:
    repo = _git_repo(tmp_path / "go-project")
    (repo / "go.mod").write_text(
        "module example.test/temp\n\ngo 1.23\n", encoding="utf-8"
    )
    (repo / "main.go").write_text(
        "package temp\nfunc Answer() int { return 42 }\n", encoding="utf-8"
    )
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))

    with ThreadPoolExecutor(max_workers=2) as pool:
        reports = tuple(
            pool.map(
                lambda _: run_command(["go", "test", "./..."], repo, FAST_POLICY),
                range(2),
            )
        )

    assert all(report.exit_code == 0 for report in reports)
    assert reports[0].scratch != reports[1].scratch
    assert all(report.scratch_retained is False for report in reports)
    assert all(not Path(report.scratch).exists() for report in reports)
    assert (tmp_path / "cache" / "go-mod").is_dir()


def test_python_node_bun_rust_and_java_commands_use_bounded_runner(
    monkeypatch, tmp_path: Path
) -> None:
    repo = _git_repo(tmp_path / "multi-project")
    (repo / "Cargo.toml").write_text(
        '[package]\nname = "temp-check"\nversion = "0.1.0"\nedition = "2024"\n',
        encoding="utf-8",
    )
    source = repo / "src"
    source.mkdir()
    (source / "lib.rs").write_text("pub fn answer() -> u8 { 42 }\n", encoding="utf-8")
    (repo / "Main.java").write_text(
        "final class Main { public static void main(String[] args) {} }\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))

    commands = (
        ["python", "-c", "print('python-ok')"],
        ["node", "-e", "console.log('node-ok')"],
        ["bun", "-e", "console.log('bun-ok')"],
        ["cargo", "check", "--quiet"],
        ["sh", "-c", 'javac -d "$TMPDIR/java" Main.java'],
    )
    reports = [run_command(command, repo, FAST_POLICY) for command in commands]

    assert [report.exit_code for report in reports] == [0, 0, 0, 0, 0]
    assert len({report.scratch for report in reports}) == 5
    assert (tmp_path / "cache" / "node-compile-cache").is_dir()
