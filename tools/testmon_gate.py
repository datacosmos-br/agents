"""Run pytest-testmon with strict cache and outcome accounting."""

from __future__ import annotations

import fcntl
import os
import sqlite3
import tempfile
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import pytest
from testmon.configure import TmConf
from testmon.db import DATA_VERSION
from testmon.pytest_testmon import TestmonSelect

_DATABASE_TABLES = frozenset(
    {"environment", "file_fp", "test_execution", "test_execution_file_fp"}
)
_SIDECAR_SUFFIXES = ("-journal", "-shm", "-wal")


@dataclass(frozen=True)
class DatabaseState:
    """One validated physical snapshot of the testmon database."""

    device: int
    inode: int
    tests: frozenset[str]
    executions: int
    failures: int
    missing_durations: int
    dependency_edges: int


@dataclass
class PytestAudit:
    """Observe pytest/testmon without changing its execution semantics."""

    mode: str
    config: pytest.Config | None = None
    selected: set[str] = field(default_factory=set)
    executed: set[str] = field(default_factory=set)
    warnings: int = 0
    skips: int = 0
    xfails: int = 0

    @pytest.hookimpl(trylast=True)
    def pytest_configure(self, config: pytest.Config) -> None:
        tm_conf = cast(TmConf, getattr(config, "testmon_config"))
        expected_select = self.mode == "incremental"
        if (
            not tm_conf.collect
            or tm_conf.select is not expected_select
            or tm_conf.tmnet
        ):
            raise RuntimeError(
                "testmon mode is not canonical: "
                f"collect={tm_conf.collect} select={tm_conf.select} tmnet={tm_conf.tmnet}"
            )
        for plugin in ("TestmonCollect", "TestmonSelect"):
            if not config.pluginmanager.hasplugin(plugin):
                raise RuntimeError(f"required testmon plugin is absent: {plugin}")
        self.config = config

    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, items: list[pytest.Item]) -> None:
        self.selected = {item.nodeid for item in items}

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        if report.when == "call":
            self.executed.add(report.nodeid)
        if report.skipped:
            self.skips += 1
        if hasattr(report, "wasxfail"):
            self.xfails += 1

    def pytest_warning_recorded(
        self,
        warning_message: warnings.WarningMessage,
        when: str,
        nodeid: str,
        location: tuple[str, int, str] | None,
    ) -> None:
        del warning_message, when, nodeid, location
        self.warnings += 1

    def deselected(self) -> frozenset[str]:
        if self.config is None:
            raise RuntimeError("pytest did not configure the testmon audit")
        plugin = self.config.pluginmanager.get_plugin("TestmonSelect")
        if not isinstance(plugin, TestmonSelect):
            raise TypeError("TestmonSelect plugin has an unexpected type")
        return frozenset(plugin.deselected_tests)


def _database_state(path: Path) -> DatabaseState:
    metadata = path.lstat()
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"testmon database must be a physical file: {path}")
    with sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) as connection:
        quick = tuple(row[0] for row in connection.execute("PRAGMA quick_check"))
        if quick != ("ok",):
            raise ValueError(f"testmon quick_check failed: {quick}")
        foreign_keys = tuple(connection.execute("PRAGMA foreign_key_check"))
        if foreign_keys:
            raise ValueError(f"testmon foreign_key_check failed: {foreign_keys[0]}")
        version = connection.execute("PRAGMA user_version").fetchone()
        if version != (DATA_VERSION,):
            raise ValueError(
                f"testmon schema {version[0] if version else None} != {DATA_VERSION}"
            )
        tables = frozenset(
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        )
        if not _DATABASE_TABLES <= tables:
            raise ValueError(
                f"testmon database tables missing: {sorted(_DATABASE_TABLES - tables)}"
            )
        rows = tuple(
            connection.execute("SELECT test_name, failed, duration FROM test_execution")
        )
        tests = frozenset(str(row[0]) for row in rows)
        edges = connection.execute(
            "SELECT count(*) FROM test_execution_file_fp"
        ).fetchone()
    if len(rows) != len(tests):
        raise ValueError("testmon database contains duplicate test executions")
    return DatabaseState(
        metadata.st_dev,
        metadata.st_ino,
        tests,
        len(rows),
        sum(int(row[1]) for row in rows),
        sum(row[2] is None for row in rows),
        int(edges[0]) if edges is not None else 0,
    )


def _validate_sidecars(path: Path) -> None:
    for suffix in _SIDECAR_SUFFIXES:
        sidecar = Path(f"{path}{suffix}")
        if sidecar.exists() or sidecar.is_symlink():
            raise ValueError(f"testmon SQLite sidecar residue: {sidecar}")


def _validate_path(repository: Path, datafile: Path) -> None:
    if not datafile.is_absolute() or datafile.is_relative_to(repository):
        raise ValueError("TESTMON_DATAFILE must be an absolute external cache path")
    for parent in (datafile.parent, *datafile.parents):
        if parent.exists() and parent.is_symlink():
            raise ValueError(f"testmon cache ancestry must be physical: {parent}")


def _run(mode: str, repository: Path, datafile: Path) -> int:
    existed = datafile.exists()
    if mode == "full" and not existed:
        raise ValueError("full testmon execution requires a seeded cache")
    before = _database_state(datafile) if existed else None
    _validate_sidecars(datafile)
    audit = PytestAudit(mode)
    with tempfile.TemporaryDirectory(prefix="scratch-", dir=datafile.parent) as scratch:
        arguments = [
            "--basetemp",
            scratch,
            "--testmon",
            "-vvv",
            "--maxfail=1",
            "-W",
            "error",
            "--strict-config",
            "--strict-markers",
        ]
        if mode == "full":
            arguments.append("--testmon-noselect")
        result = int(pytest.main(arguments, plugins=[audit]))
    if result != 0:
        return result
    after = _database_state(datafile)
    _validate_sidecars(datafile)
    if before is not None and (before.device, before.inode) != (
        after.device,
        after.inode,
    ):
        raise ValueError("testmon replaced its persistent database")
    if not after.tests or after.failures or after.missing_durations:
        raise ValueError(
            "testmon database outcome is invalid: "
            f"tests={len(after.tests)} failures={after.failures} "
            f"missing_durations={after.missing_durations}"
        )
    if after.dependency_edges <= 0:
        raise ValueError("testmon database contains no dependency evidence")
    if audit.warnings or audit.skips or audit.xfails:
        raise RuntimeError(
            "pytest emitted a forbidden outcome: "
            f"warnings={audit.warnings} skips={audit.skips} xfails={audit.xfails}"
        )
    deselected = audit.deselected()
    if audit.executed != audit.selected:
        raise RuntimeError(
            f"pytest selected {len(audit.selected)} tests but executed {len(audit.executed)}"
        )
    if mode == "full":
        if deselected or audit.executed != after.tests:
            raise RuntimeError(
                "full testmon accounting mismatch: "
                f"executed={len(audit.executed)} deselected={len(deselected)} "
                f"total={len(after.tests)}"
            )
    elif audit.executed & deselected or audit.executed | deselected != after.tests:
        raise RuntimeError(
            "incremental testmon accounting mismatch: "
            f"executed={len(audit.executed)} deselected={len(deselected)} "
            f"total={len(after.tests)}"
        )
    cache = "reused" if before is not None else "seeded"
    print(
        f"TESTMON mode={mode} cache={cache} collected={len(after.tests)} "
        f"executed={len(audit.executed)} deselected={len(deselected)} "
        f"total={after.executions} warnings=0 skips=0 integrity=ok"
    )
    return 0


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    mode = os.environ.get("TESTMON_MODE")
    if mode not in {"full", "incremental"}:
        raise ValueError("TESTMON_MODE must equal incremental or full")
    configured = os.environ.get("TESTMON_DATAFILE")
    if configured is None:
        raise ValueError("TESTMON_DATAFILE is required")
    datafile = Path(configured)
    _validate_path(repository, datafile)
    datafile.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = datafile.parent / "testmon.lock"
    if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
        raise ValueError(f"testmon lock must be a physical file: {lock_path}")
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _run(mode, repository, datafile)


if __name__ == "__main__":
    raise SystemExit(main())
