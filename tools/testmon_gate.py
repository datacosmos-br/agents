"""Run pytest-testmon with strict cache and outcome accounting."""

from __future__ import annotations

import fcntl
import importlib
import json
import os
import sqlite3
import sys
import tempfile
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from strict_subprocess import run_strict

_DATABASE_TABLES = frozenset(
    {"environment", "file_fp", "test_execution", "test_execution_file_fp"}
)
_SIDECAR_SUFFIXES = ("-journal", "-shm", "-wal")


def _testmon_data_version() -> int:
    module = importlib.import_module("testmon.db")
    value: object = getattr(module, "DATA_VERSION", None)
    if type(value) is not int:
        raise TypeError("testmon.db.DATA_VERSION must be an integer")
    return value


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


@dataclass(frozen=True)
class PytestAudit:
    """One validated accounting report emitted by the pytest child."""

    executed: frozenset[str]
    deselected: frozenset[str]
    warnings: int
    skips: int
    xfails: int


def _database_state(path: Path) -> DatabaseState:
    metadata = path.lstat()
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"testmon database must be a physical file: {path}")
    with closing(
        sqlite3.connect(f"{path.as_uri()}?mode=ro&immutable=1", uri=True)
    ) as connection:
        quick = tuple(row[0] for row in connection.execute("PRAGMA quick_check"))
        if quick != ("ok",):
            raise ValueError(f"testmon quick_check failed: {quick}")
        foreign_keys = tuple(connection.execute("PRAGMA foreign_key_check"))
        if foreign_keys:
            raise ValueError(f"testmon foreign_key_check failed: {foreign_keys[0]}")
        version = connection.execute("PRAGMA user_version").fetchone()
        expected_version = _testmon_data_version()
        if version != (expected_version,):
            raise ValueError(
                f"testmon schema {version[0] if version else None} "
                f"!= {expected_version}"
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


def _audit_report(path: Path) -> PytestAudit:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"pytest did not emit a physical audit report: {path}")
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not all(isinstance(key, str) for key in raw):
        raise TypeError("pytest audit report must be a string-keyed mapping")
    report = cast(dict[str, object], raw)
    expected = frozenset({"deselected", "executed", "skips", "warnings", "xfails"})
    if frozenset(report) != expected:
        raise ValueError("pytest audit report fields are not canonical")

    def nodeids(field: str) -> frozenset[str]:
        value = report[field]
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value
        ):
            raise TypeError(f"pytest audit {field} must contain nodeid strings")
        values = cast(list[str], value)
        if len(values) != len(set(values)):
            raise ValueError(f"pytest audit {field} contains duplicate nodeids")
        return frozenset(values)

    def count(field: str) -> int:
        value = report[field]
        if type(value) is not int or value < 0:
            raise TypeError(f"pytest audit {field} must be a non-negative integer")
        return value

    return PytestAudit(
        executed=nodeids("executed"),
        deselected=nodeids("deselected"),
        warnings=count("warnings"),
        skips=count("skips"),
        xfails=count("xfails"),
    )


def _run(mode: str, repository: Path, datafile: Path) -> int:
    existed = datafile.exists()
    if mode == "full" and not existed:
        raise ValueError("full testmon execution requires a seeded cache")
    _validate_sidecars(datafile)
    before = _database_state(datafile) if existed else None
    with tempfile.TemporaryDirectory(prefix="scratch-", dir=datafile.parent) as scratch:
        audit_path = Path(scratch) / "audit.json"
        arguments = [
            sys.executable,
            "-m",
            "pytest",
            "--basetemp",
            scratch,
            "--testmon",
            "-vvv",
            "--maxfail=1",
            "-W",
            "error",
            "--strict-config",
            "--strict-markers",
            "-p",
            "tools.testmon_pytest_plugin",
        ]
        if mode == "full":
            arguments.append("--testmon-noselect")
        environment = dict(os.environ)
        environment["TESTMON_AUDIT_PATH"] = str(audit_path)
        run_strict(tuple(arguments), repository, "TESTMON pytest", environment)
        audit = _audit_report(audit_path)
    _validate_sidecars(datafile)
    after = _database_state(datafile)
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
    deselected = audit.deselected
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


def _repair(datafile: Path) -> int:
    obsolete_scratch = datafile.parent / "scratch"
    if obsolete_scratch.is_symlink() or (
        obsolete_scratch.exists() and not obsolete_scratch.is_dir()
    ):
        raise ValueError(
            f"obsolete test scratch must be a physical directory: {obsolete_scratch}"
        )
    if obsolete_scratch.exists():
        if any(obsolete_scratch.iterdir()):
            raise ValueError(
                f"obsolete test scratch must be empty before removal: {obsolete_scratch}"
            )
        obsolete_scratch.rmdir()
    if not datafile.exists():
        _validate_sidecars(datafile)
        print("TESTMON repair cache=absent sidecars=0", flush=True)
        return 0
    if datafile.is_symlink() or not datafile.is_file():
        raise ValueError(f"testmon database must be a physical file: {datafile}")
    for suffix in _SIDECAR_SUFFIXES:
        sidecar = Path(f"{datafile}{suffix}")
        if sidecar.is_symlink() or (sidecar.exists() and not sidecar.is_file()):
            raise ValueError(f"testmon SQLite sidecar must be physical: {sidecar}")
    with closing(sqlite3.connect(datafile, timeout=0)) as connection:
        checkpoint = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        if checkpoint != (0, 0, 0):
            raise RuntimeError(f"testmon WAL checkpoint failed: {checkpoint}")
        quick = tuple(row[0] for row in connection.execute("PRAGMA quick_check"))
        if quick != ("ok",):
            raise ValueError(f"testmon quick_check failed during repair: {quick}")
        foreign_keys = tuple(connection.execute("PRAGMA foreign_key_check"))
        if foreign_keys:
            raise ValueError(
                f"testmon foreign_key_check failed during repair: {foreign_keys[0]}"
            )
    _validate_sidecars(datafile)
    state = _database_state(datafile)
    print(
        f"TESTMON repair cache=present tests={len(state.tests)} "
        "sidecars=0 integrity=ok",
        flush=True,
    )
    return 0


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    mode = os.environ.get("TESTMON_MODE")
    if mode not in {"full", "incremental", "repair"}:
        raise ValueError("TESTMON_MODE must equal full, incremental, or repair")
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
        return (
            _repair(datafile) if mode == "repair" else _run(mode, repository, datafile)
        )


if __name__ == "__main__":
    raise SystemExit(main())
