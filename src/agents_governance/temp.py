"""Bounded scratch execution and conservative garbage collection."""

from __future__ import annotations

import fcntl
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Any

from .atomic_io import stage_text

SYSTEM_TEMP = Path("/tmp")
MARKER = ".agents-temp-run.json"
LOCK = ".agents-temp-run.lock"
REPORT_LOCK = ".agents-report-publication.lock"
KNOWN_DIRS = frozenset(
    {
        "tmp",
        "go-tmp",
        "go-build",
        "python",
        "node",
        "cargo",
        "cargo-target",
        "gradle",
        "ccache",
    }
)
PROHIBITED_NAMES = frozenset({".git", ".dolt", ".venv", "venv", "node_modules"})
MAIN_THREAD_ID = threading.get_ident()
DATABASE_SUFFIXES = frozenset({".db", ".sqlite", ".sqlite3"})


@dataclass(frozen=True)
class TempPolicy:
    warning_bytes: int
    failure_bytes: int
    orphan_age_seconds: int
    poll_seconds: float
    termination_grace_seconds: float

    def __post_init__(self) -> None:
        integer_values = {
            "warning_bytes": self.warning_bytes,
            "failure_bytes": self.failure_bytes,
            "orphan_age_seconds": self.orphan_age_seconds,
        }
        for integer_name, integer_value in integer_values.items():
            if type(integer_value) is not int or integer_value <= 0:
                raise ValueError(f"{integer_name} must be a positive integer")
        if self.warning_bytes >= self.failure_bytes:
            raise ValueError("warning_bytes must be lower than failure_bytes")
        for float_name, float_value in {
            "poll_seconds": self.poll_seconds,
            "termination_grace_seconds": self.termination_grace_seconds,
        }.items():
            if type(float_value) is not float or float_value <= 0:
                raise ValueError(f"{float_name} must be a positive float")
        if self.poll_seconds > self.termination_grace_seconds:
            raise ValueError("poll_seconds must not exceed termination_grace_seconds")


@dataclass(frozen=True)
class StoragePolicy:
    shell_temp: Path
    shell_temp_max_bytes: int
    report_max_bytes: int
    temp: TempPolicy


@dataclass(frozen=True)
class StorageManifest:
    version: int
    repositories: tuple[Path, ...]
    policy: StoragePolicy


class StorageManifestError(RuntimeError):
    """The configured storage authority is missing, malformed, or unsafe."""


class _RunInterrupted(Exception):
    def __init__(self, signum: int) -> None:
        self.signum = signum


def _terminate_group(
    process: subprocess.Popen[bytes] | subprocess.Popen[str], policy: TempPolicy
) -> None:
    process_group = process.pid
    try:
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        process.wait()
        return
    deadline = time.monotonic() + policy.termination_grace_seconds
    while time.monotonic() < deadline:
        process.poll()
        try:
            os.killpg(process_group, 0)
        except ProcessLookupError:
            process.wait()
            return
        time.sleep(policy.poll_seconds)
    try:
        os.killpg(process_group, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()
    deadline = time.monotonic() + policy.termination_grace_seconds
    while time.monotonic() < deadline:
        try:
            os.killpg(process_group, 0)
        except ProcessLookupError:
            return
        time.sleep(policy.poll_seconds)
    raise RuntimeError(f"owned process group did not terminate: {process_group}")


@dataclass(frozen=True)
class TempFinding:
    path: Path
    kind: str
    message: str
    size_bytes: int = 0


@dataclass(frozen=True)
class RunReport:
    command: tuple[str, ...]
    repo: str
    scratch: str
    started_at: str
    finished_at: str
    exit_code: int
    peak_bytes: int
    warning_bytes: int
    failure_bytes: int
    stopped_for_limit: bool
    scratch_retained: bool


@dataclass
class _ReportPublication:
    lock_file: IO[str]
    json_candidate: Path
    json_destination: Path
    tsv_candidate: Path
    tsv_destination: Path

    def commit(self) -> None:
        """Publish TSV first and JSON last as the canonical success marker."""

        self.tsv_candidate.replace(self.tsv_destination)
        try:
            self.json_candidate.replace(self.json_destination)
        except BaseException as error:
            try:
                self.tsv_destination.replace(self.tsv_candidate)
            except OSError as rollback_error:
                error.add_note(
                    "partial report publication could not be rolled back to its "
                    f"candidate: {rollback_error}"
                )
                raise error from rollback_error
            raise

    def close(self) -> None:
        self.lock_file.close()


def _absolute_environment_path(name: str, value: str) -> Path:
    """Reject unresolved or relative storage roots before any directory is made."""

    path = Path(value)
    if "$" in value or not path.is_absolute():
        raise RuntimeError(f"{name} must be an expanded absolute path")
    return path


def _home() -> Path:
    value = os.environ.get("HOME")
    if not value:
        raise RuntimeError("HOME is required")
    return _absolute_environment_path("HOME", value)


def _xdg(name: str, fallback: str) -> Path:
    value = os.environ.get(name)
    return _absolute_environment_path(name, value) if value else _home() / fallback


def state_root() -> Path:
    return _xdg("XDG_STATE_HOME", ".local/state") / "agents" / "temp"


def cache_root() -> Path:
    return _xdg("XDG_CACHE_HOME", ".cache")


def _under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def resolve_repo(cwd: Path) -> Path:
    """Resolve the Git owner and reject repositories located in system temp."""

    probe = subprocess.run(
        ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if probe.returncode:
        raise RuntimeError(f"not inside a Git repository: {cwd}")
    repo = Path(probe.stdout.strip()).resolve()
    if _under(repo, SYSTEM_TEMP):
        raise RuntimeError(f"repositories under /tmp are prohibited: {repo}")
    return repo


def managed_temp(repo: Path) -> Path:
    """Return the repository-owned scratch root without following symlinks."""

    resolved = resolve_repo(repo)
    destination = resolved / ".test-tmp"
    if destination.is_symlink():
        raise RuntimeError(f"scratch root must not be a symlink: {destination}")
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    return destination


def _mkdir(path: Path) -> Path:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError(f"managed path must not be a symlink: {path}")
    return path


def create_run(repo: Path) -> tuple[Path, IO[str]]:
    scratch = Path(tempfile.mkdtemp(prefix="run.", dir=managed_temp(repo)))
    lock_file: IO[str] | None = None
    try:
        for name in KNOWN_DIRS:
            _mkdir(scratch / name)
        marker = {
            "version": 1,
            "owner_pid": os.getpid(),
            "repo": str(repo.resolve()),
            "created_at": datetime.now(UTC).isoformat(),
            "owned_dirs": sorted(KNOWN_DIRS),
        }
        (scratch / MARKER).write_text(
            json.dumps(marker, sort_keys=True) + "\n", encoding="utf-8"
        )
        lock_file = (scratch / LOCK).open("w", encoding="utf-8")
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_file.write(f"{os.getpid()}\n")
        lock_file.flush()
        return scratch, lock_file
    except BaseException as error:
        cleanup_errors: list[Exception] = []
        if lock_file is not None:
            try:
                lock_file.close()
            except OSError as cleanup_error:
                cleanup_errors.append(cleanup_error)
        try:
            protected = _protected_descendant(scratch)
            if protected is None:
                _remove_owned_tree(scratch)
                scratch.rmdir()
            else:
                error.add_note(
                    f"partial scratch retained because it contains {protected}: "
                    f"{scratch}"
                )
        except (OSError, RuntimeError) as cleanup_error:
            cleanup_errors.append(cleanup_error)
        if cleanup_errors:
            error.add_note(
                "partial scratch rollback failed: "
                + "; ".join(str(item) for item in cleanup_errors)
            )
            raise error from cleanup_errors[0]
        raise


def managed_env(repo: Path, scratch: Path) -> dict[str, str]:
    """Build isolated test/build paths while sharing reusable dependency caches."""

    environment = os.environ.copy()
    environment["HOME"] = str(_home())
    shared = cache_root()
    mappings = {
        "TMPDIR": scratch,
        "GOTMPDIR": scratch / "go-tmp",
        "GOCACHE": scratch / "go-build",
        "GOMODCACHE": shared / "go-mod",
        "UV_CACHE_DIR": shared / "uv",
        "PIP_CACHE_DIR": shared / "pip",
        "npm_config_cache": shared / "npm",
        "NODE_COMPILE_CACHE": shared / "node-compile-cache",
        "BUN_INSTALL_CACHE_DIR": shared / "bun",
        "CARGO_HOME": shared / "cargo",
        "CARGO_TARGET_DIR": scratch / "cargo-target",
        "GRADLE_USER_HOME": shared / "gradle",
        "CCACHE_DIR": shared / "ccache",
    }
    for key, value in mappings.items():
        environment[key] = str(_mkdir(value))
    return environment


def _tree_size(path: Path) -> int:
    if path.is_file() and not path.is_symlink():
        try:
            return path.stat().st_size
        except FileNotFoundError:
            return 0
    total = 0
    try:
        entries = list(os.scandir(path))
    except (FileNotFoundError, NotADirectoryError):
        return 0
    for entry in entries:
        try:
            if entry.is_symlink():
                continue
            total += (
                _tree_size(Path(entry.path))
                if entry.is_dir(follow_symlinks=False)
                else entry.stat(follow_symlinks=False).st_size
            )
        except FileNotFoundError:
            continue
    return total


def _report_renderings(report: RunReport) -> tuple[str, str]:
    payload = asdict(report)
    columns = tuple(payload)
    values = tuple(json.dumps(payload[key], separators=(",", ":")) for key in columns)
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        "\t".join(columns) + "\n" + "\t".join(values) + "\n",
    )


def _report_usage(reports: Path) -> int:
    total = 0
    for entry in reports.iterdir():
        if entry.name == REPORT_LOCK:
            continue
        if entry.is_symlink():
            raise RuntimeError(f"report store contains a symbolic link: {entry}")
        if not entry.is_file():
            raise RuntimeError(f"report store contains a non-file entry: {entry}")
        total += entry.stat().st_size
    return total


def _open_report_lock(reports: Path) -> IO[str]:
    lock_path = reports / REPORT_LOCK
    if lock_path.is_symlink():
        raise RuntimeError(
            f"report publication lock must not be a symlink: {lock_path}"
        )
    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(lock_path, flags, 0o600)
    handle = os.fdopen(descriptor, "a+", encoding="utf-8")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
    except BaseException:
        handle.close()
        raise
    return handle


def _prepare_report(report: RunReport, max_bytes: int) -> _ReportPublication:
    if type(max_bytes) is not int or max_bytes <= 0:
        raise ValueError("report_max_bytes must be a positive integer")
    reports = _mkdir(state_root() / "reports")
    lock_file = _open_report_lock(reports)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    json_text, tsv_text = _report_renderings(report)
    json_destination = reports / f"{stamp}.json"
    tsv_destination = reports / f"{stamp}.tsv"
    try:
        if json_destination.exists() or tsv_destination.exists():
            raise FileExistsError(f"report publication collision: {stamp}")
        usage = _report_usage(reports)
        required = len(json_text.encode()) + len(tsv_text.encode())
        if usage + required > max_bytes:
            raise RuntimeError(
                "report store capacity exceeded: "
                f"{usage} existing + {required} new > {max_bytes} bytes"
            )
        json_candidate = stage_text(json_destination, json_text, mode=0o600)
        try:
            tsv_candidate = stage_text(tsv_destination, tsv_text, mode=0o600)
        except BaseException as error:
            error.add_note(
                f"unpublished JSON report evidence retained: {json_candidate}"
            )
            raise
        return _ReportPublication(
            lock_file,
            json_candidate,
            json_destination,
            tsv_candidate,
            tsv_destination,
        )
    except BaseException:
        lock_file.close()
        raise


def _require_report_capacity(max_bytes: int) -> None:
    reports = state_root() / "reports"
    if not reports.exists():
        return
    if reports.is_symlink() or not reports.is_dir():
        raise RuntimeError(f"run report store must be a physical directory: {reports}")
    lock_file = _open_report_lock(reports)
    try:
        usage = _report_usage(reports)
        if usage >= max_bytes:
            raise RuntimeError(
                f"report store capacity exhausted: {usage} >= {max_bytes} bytes"
            )
    finally:
        lock_file.close()


def _write_report(report: RunReport, max_bytes: int | None = None) -> None:
    effective_max = (
        storage_manifest().policy.report_max_bytes if max_bytes is None else max_bytes
    )
    publication = _prepare_report(report, effective_max)
    try:
        publication.commit()
    finally:
        publication.close()


def run_command(
    command: Sequence[str], cwd: Path, policy: TempPolicy | None = None
) -> RunReport:
    """Run one owned process group with isolated scratch and bounded growth."""

    if not command:
        raise ValueError("temp run requires a command after --")
    manifest = storage_manifest()
    effective_policy = manifest.policy.temp if policy is None else policy
    _require_report_capacity(manifest.policy.report_max_bytes)
    repo = resolve_repo(cwd)
    scratch, lock_file = create_run(repo)
    started = datetime.now(UTC)
    try:
        environment = managed_env(repo, scratch)
        process = subprocess.Popen(
            tuple(command), cwd=cwd, env=environment, start_new_session=True
        )
    except BaseException as error:
        lock_file.close()
        try:
            protected = _protected_descendant(scratch)
            if protected is None:
                _remove_owned_tree(scratch)
                scratch.rmdir()
            else:
                error.add_note(
                    f"unstarted scratch retained because it contains {protected}: "
                    f"{scratch}"
                )
        except (OSError, RuntimeError) as cleanup_error:
            error.add_note(f"unstarted scratch cleanup failed: {cleanup_error}")
            raise error from cleanup_error
        raise
    peak = 0
    warned = False
    stopped = False
    interrupted_signal: int | None = None
    previous_handlers: dict[signal.Signals, Any] = {}
    final_size_probe = True

    def interrupt(signum: int, _frame: object) -> None:
        raise _RunInterrupted(signum)

    try:
        if threading.get_ident() == MAIN_THREAD_ID:
            for watched in (signal.SIGINT, signal.SIGTERM):
                previous_handlers[watched] = signal.signal(watched, interrupt)
        while process.poll() is None:
            size = _tree_size(scratch)
            peak = max(peak, size)
            if size >= effective_policy.warning_bytes and not warned:
                print(
                    f"WARNING: owned scratch reached {size} bytes: {scratch}",
                    file=sys.stderr,
                )
                warned = True
            if size >= effective_policy.failure_bytes:
                _terminate_group(process, effective_policy)
                stopped = True
                break
            time.sleep(effective_policy.poll_seconds)
        exit_code = process.wait()
    except _RunInterrupted as error:
        interrupted_signal = error.signum
        for watched in previous_handlers:
            signal.signal(watched, signal.SIG_IGN)
        _terminate_group(process, effective_policy)
        exit_code = 128 + error.signum
    except KeyboardInterrupt:
        interrupted_signal = int(signal.SIGINT)
        for watched in previous_handlers:
            signal.signal(watched, signal.SIG_IGN)
        _terminate_group(process, effective_policy)
        exit_code = 128 + int(signal.SIGINT)
    except BaseException as error:
        final_size_probe = False
        for watched in previous_handlers:
            signal.signal(watched, signal.SIG_IGN)
        try:
            _terminate_group(process, effective_policy)
        except (OSError, RuntimeError) as cleanup_error:
            error.add_note(f"owned process-group cleanup failed: {cleanup_error}")
            raise error from cleanup_error
        raise
    finally:
        for watched, handler in previous_handlers.items():
            signal.signal(watched, handler)
        try:
            if final_size_probe:
                peak = max(peak, _tree_size(scratch))
        finally:
            lock_file.close()
    if (stopped or interrupted_signal is not None) and exit_code == 0:
        exit_code = 70
    retained = True
    remove_scratch = False
    if exit_code == 0:
        protected = _protected_descendant(scratch)
        if protected is None:
            retained = False
            remove_scratch = True
        else:
            print(
                f"FAIL: retained owned scratch containing {protected}: {scratch}",
                file=sys.stderr,
            )
            exit_code = 70
    report = RunReport(
        command=tuple(command),
        repo=str(repo),
        scratch=str(scratch),
        started_at=started.isoformat(),
        finished_at=datetime.now(UTC).isoformat(),
        exit_code=exit_code,
        peak_bytes=peak,
        warning_bytes=effective_policy.warning_bytes,
        failure_bytes=effective_policy.failure_bytes,
        stopped_for_limit=stopped,
        scratch_retained=retained,
    )
    publication = _prepare_report(report, manifest.policy.report_max_bytes)
    try:
        if remove_scratch:
            _remove_owned_tree(scratch)
            scratch.rmdir()
        publication.commit()
    finally:
        publication.close()
    return report


def _classify(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    if path.is_symlink():
        return "symlink", "preserve: symbolic link"
    if name in PROHIBITED_NAMES:
        return "prohibited", f"prohibited workspace/cache marker: {path.name}"
    if path.suffix.lower() in DATABASE_SUFFIXES:
        return "prohibited", "prohibited persistent database in /tmp"
    if name.endswith((".sock", ".lock")):
        return "ephemeral", "preserve: small socket or lock"
    prefixes = (
        "go-build",
        "pytest-",
        "node-compile-cache",
        "beads-",
        "aihub-",
        "flext-",
        "gt-junk",
        "pool-shell-",
        "agents-waza-check.",
    )
    if name.startswith(prefixes):
        return "residue", "unmanaged build/test residue in /tmp"
    return "unknown", "preserve: unclassified /tmp content"


def findings(temp_root: Path = SYSTEM_TEMP) -> list[TempFinding]:
    """Inventory /tmp structurally; never infer deletion permission from a prefix."""

    result: list[TempFinding] = []
    entries = list(temp_root.iterdir())
    for entry in entries:
        kind, message = _classify(entry)
        nested = (
            entry.is_dir()
            and not entry.is_symlink()
            and any((entry / marker).exists() for marker in PROHIBITED_NAMES)
        )
        if kind != "unknown" or nested:
            result.append(TempFinding(entry, kind, message, _tree_size(entry)))
    return sorted(result, key=lambda item: str(item.path))


def _exact_keys(table: dict[str, Any], expected: frozenset[str], context: str) -> None:
    actual = frozenset(table)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing {missing}")
        if extra:
            details.append(f"unexpected {extra}")
        raise StorageManifestError(f"{context} schema mismatch: {', '.join(details)}")


def _positive_integer(table: dict[str, Any], key: str) -> int:
    value = table[key]
    if type(value) is not int or value <= 0:
        raise StorageManifestError(f"policy.{key} must be a positive integer")
    return value


def _positive_float(table: dict[str, Any], key: str) -> float:
    value = table[key]
    if type(value) is not float or value <= 0:
        raise StorageManifestError(f"policy.{key} must be a positive float")
    return value


def _manifest_path(raw: str, context: str) -> Path:
    try:
        return _expand_local_path(raw)
    except RuntimeError as error:
        raise StorageManifestError(f"{context}: {error}") from error


def storage_manifest() -> StorageManifest:
    """Load and validate the one configured storage authority."""

    configured = os.environ.get("AGENTS_STORAGE_CONFIG")
    if not configured:
        raise StorageManifestError("AGENTS_STORAGE_CONFIG is required")
    path = Path(configured)
    if not path.is_absolute():
        raise StorageManifestError("AGENTS_STORAGE_CONFIG must be an absolute path")
    if path.is_symlink() or (path.exists() and path.resolve() != path):
        raise StorageManifestError(
            f"AGENTS_STORAGE_CONFIG must be a physical file, not a symlink: {path}"
        )
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise StorageManifestError(f"storage manifest unavailable: {error}") from error
    _exact_keys(data, frozenset({"version", "repositories", "policy"}), "storage")
    if type(data["version"]) is not int or data["version"] != 2:
        raise StorageManifestError("storage.version must be integer 2")

    raw_repositories = data["repositories"]
    if not isinstance(raw_repositories, list):
        raise StorageManifestError("storage.repositories must be an array")
    repositories: list[Path] = []
    for index, raw_entry in enumerate(raw_repositories):
        if not isinstance(raw_entry, dict):
            raise StorageManifestError(f"storage.repositories[{index}] must be a table")
        _exact_keys(
            raw_entry,
            frozenset({"path"}),
            f"storage.repositories[{index}]",
        )
        raw_path = raw_entry["path"]
        if not isinstance(raw_path, str) or not raw_path:
            raise StorageManifestError(
                f"storage.repositories[{index}].path must be a non-empty string"
            )
        repository = _manifest_path(raw_path, f"storage.repositories[{index}].path")
        if repository in repositories:
            raise StorageManifestError(
                f"duplicate storage repository path: {repository}"
            )
        repositories.append(repository)

    raw_policy = data["policy"]
    if not isinstance(raw_policy, dict):
        raise StorageManifestError("storage.policy must be a table")
    _exact_keys(
        raw_policy,
        frozenset(
            {
                "shell_temp",
                "shell_temp_max_bytes",
                "report_max_bytes",
                "warning_bytes",
                "failure_bytes",
                "orphan_age_days",
                "poll_seconds",
                "termination_grace_seconds",
            }
        ),
        "storage.policy",
    )
    raw_shell_temp = raw_policy["shell_temp"]
    if not isinstance(raw_shell_temp, str) or not raw_shell_temp:
        raise StorageManifestError("policy.shell_temp must be a non-empty string")
    orphan_age_days = _positive_integer(raw_policy, "orphan_age_days")
    if orphan_age_days < 7:
        raise StorageManifestError("policy.orphan_age_days must be at least 7")
    try:
        temp_policy = TempPolicy(
            warning_bytes=_positive_integer(raw_policy, "warning_bytes"),
            failure_bytes=_positive_integer(raw_policy, "failure_bytes"),
            orphan_age_seconds=orphan_age_days * 24 * 60 * 60,
            poll_seconds=_positive_float(raw_policy, "poll_seconds"),
            termination_grace_seconds=_positive_float(
                raw_policy, "termination_grace_seconds"
            ),
        )
    except ValueError as error:
        raise StorageManifestError(f"invalid storage policy: {error}") from error
    return StorageManifest(
        version=2,
        repositories=tuple(repositories),
        policy=StoragePolicy(
            shell_temp=_manifest_path(raw_shell_temp, "policy.shell_temp"),
            shell_temp_max_bytes=_positive_integer(raw_policy, "shell_temp_max_bytes"),
            report_max_bytes=_positive_integer(raw_policy, "report_max_bytes"),
            temp=temp_policy,
        ),
    )


def _expand_local_path(raw: str) -> Path:
    values = {
        "HOME": str(_home()),
        "XDG_CONFIG_HOME": str(_xdg("XDG_CONFIG_HOME", ".config")),
        "XDG_CACHE_HOME": str(_xdg("XDG_CACHE_HOME", ".cache")),
        "XDG_STATE_HOME": str(_xdg("XDG_STATE_HOME", ".local/state")),
    }
    expanded = raw
    for name, value in values.items():
        expanded = expanded.replace(f"${{{name}}}", value)
    if "$" in expanded:
        raise RuntimeError(f"unresolved path variable: {raw}")
    result = Path(expanded)
    if not result.is_absolute():
        raise RuntimeError(f"storage path must be absolute: {raw}")
    return result


def registered_repositories(
    manifest: StorageManifest | None = None,
) -> tuple[Path, ...]:
    configured = storage_manifest() if manifest is None else manifest
    result: list[Path] = []
    for path in configured.repositories:
        if path.resolve() != path or path.is_symlink():
            raise StorageManifestError(
                f"registered repository must be a physical canonical path: {path}"
            )
        if not path.is_dir() or resolve_repo(path) != path.resolve():
            raise StorageManifestError(
                f"registered repository is not a Git root: {path}"
            )
        result.append(path)
    return tuple(result)


def global_findings() -> list[TempFinding]:
    """Audit system temp and every explicitly registered repository."""

    manifest = storage_manifest()
    result = list(findings(SYSTEM_TEMP))
    for repo in registered_repositories(manifest):
        result.extend(repository_findings(repo))
    shell_temp = manifest.policy.shell_temp
    maximum = manifest.policy.shell_temp_max_bytes
    if shell_temp.is_symlink():
        raise StorageManifestError(
            f"policy.shell_temp must not be a symbolic link: {shell_temp}"
        )
    size = _tree_size(shell_temp)
    if size > maximum:
        result.append(
            TempFinding(
                shell_temp,
                "prohibited",
                f"shell fallback storage exceeds {maximum} bytes",
                size,
            )
        )
    reports = state_root() / "reports"
    if reports.exists():
        if reports.is_symlink() or not reports.is_dir():
            raise RuntimeError(
                f"run report store must be a physical directory: {reports}"
            )
        report_bytes = _report_usage(reports)
        if report_bytes > manifest.policy.report_max_bytes:
            result.append(
                TempFinding(
                    reports,
                    "prohibited",
                    "run report store exceeds policy.report_max_bytes",
                    report_bytes,
                )
            )
        for candidate in sorted(reports.glob("*.candidate")):
            result.append(
                TempFinding(
                    candidate,
                    "residue",
                    "incomplete run report publication requires operator review",
                    _tree_size(candidate),
                )
            )
    return sorted(result, key=lambda item: str(item.path))


def gc_all(*, apply: bool) -> tuple[list[Path], list[TempFinding]]:
    manifest = storage_manifest()
    eligible: list[Path] = []
    blocked: list[TempFinding] = []
    for repo in registered_repositories(manifest):
        repo_eligible, repo_blocked = gc(repo, apply=apply, policy=manifest.policy.temp)
        eligible.extend(repo_eligible)
        blocked.extend(repo_blocked)
    return eligible, blocked


def repository_findings(root: Path) -> list[TempFinding]:
    """Detect shell-expansion residue that must never exist below a repository."""

    result: list[TempFinding] = []
    prohibited = {
        "$HOME": "unexpanded home-directory variable created repository-local state",
        "~": "unexpanded home-directory variable created repository-local state",
        ".archive": "repository-local legacy archive coexists with canonical authority",
        ".skills-archive": "repository-local legacy skill archive coexists with canonical authority",
    }
    for name, message in prohibited.items():
        candidate = root / name
        if candidate.exists() or candidate.is_symlink():
            result.append(
                TempFinding(
                    candidate,
                    "residue",
                    message,
                    _tree_size(candidate),
                )
            )
    return result


def _locked(path: Path) -> bool:
    handle: IO[str] | None = None
    try:
        handle = (path / LOCK).open("a+", encoding="utf-8")
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        if handle is not None:
            handle.close()
        return True
    handle.close()
    return False


def _protected_descendant(path: Path) -> str | None:
    for root, dirs, files in os.walk(path, followlinks=False):
        current = Path(root)
        if current.is_symlink() or any(
            (current / name).is_symlink() for name in dirs + files
        ):
            return "symlink"
        names = set(dirs) | set(files)
        if names & PROHIBITED_NAMES:
            return "Git, virtualenv, dependency tree, or database"
        if any(Path(name).suffix.lower() in DATABASE_SUFFIXES for name in files):
            return "database"
    return None


def _remove_owned_tree(path: Path) -> None:
    for entry in os.scandir(path):
        child = Path(entry.path)
        if entry.is_symlink():
            raise RuntimeError(f"refused symlink during removal: {child}")
        if entry.is_dir(follow_symlinks=False):
            _remove_owned_tree(child)
            child.rmdir()
        else:
            child.unlink()


def _run_report_payload(path: Path) -> RunReport:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"invalid run report {path}: {error}") from error
    if not isinstance(payload, dict):
        raise TypeError(f"invalid run report {path}: root must be an object")
    expected = frozenset(RunReport.__dataclass_fields__)
    actual = frozenset(payload)
    if actual != expected:
        raise RuntimeError(
            f"invalid run report {path}: fields must be {sorted(expected)}"
        )
    command = payload["command"]
    if (
        not isinstance(command, list)
        or not command
        or not all(isinstance(item, str) and item for item in command)
    ):
        raise RuntimeError(f"invalid run report {path}: command must be non-empty")
    string_fields = ("repo", "scratch", "started_at", "finished_at")
    if any(
        not isinstance(payload[name], str) or not payload[name]
        for name in string_fields
    ):
        raise RuntimeError(f"invalid run report {path}: invalid string field")
    integer_fields = (
        "exit_code",
        "peak_bytes",
        "warning_bytes",
        "failure_bytes",
    )
    if any(type(payload[name]) is not int for name in integer_fields):
        raise RuntimeError(f"invalid run report {path}: invalid integer field")
    if payload["peak_bytes"] < 0 or payload["warning_bytes"] <= 0:
        raise RuntimeError(f"invalid run report {path}: invalid byte count")
    if payload["warning_bytes"] >= payload["failure_bytes"]:
        raise RuntimeError(f"invalid run report {path}: invalid run thresholds")
    boolean_fields = ("stopped_for_limit", "scratch_retained")
    if any(type(payload[name]) is not bool for name in boolean_fields):
        raise RuntimeError(f"invalid run report {path}: invalid boolean field")
    for name in ("repo", "scratch"):
        value = str(payload[name])
        if "$" in value or not Path(value).is_absolute():
            raise RuntimeError(f"invalid run report {path}: {name} must be absolute")
    return RunReport(
        command=tuple(command),
        repo=str(payload["repo"]),
        scratch=str(payload["scratch"]),
        started_at=str(payload["started_at"]),
        finished_at=str(payload["finished_at"]),
        exit_code=int(payload["exit_code"]),
        peak_bytes=int(payload["peak_bytes"]),
        warning_bytes=int(payload["warning_bytes"]),
        failure_bytes=int(payload["failure_bytes"]),
        stopped_for_limit=bool(payload["stopped_for_limit"]),
        scratch_retained=bool(payload["scratch_retained"]),
    )


def _successful_run_reports(repo: Path) -> set[Path]:
    reports = state_root() / "reports"
    if not reports.exists():
        return set()
    if reports.is_symlink() or not reports.is_dir():
        raise RuntimeError(f"run report store must be a physical directory: {reports}")
    entries = tuple(reports.iterdir())
    incomplete = sorted(path for path in entries if path.suffix == ".candidate")
    if incomplete:
        raise RuntimeError(
            "incomplete run report publication blocks GC: "
            + ", ".join(str(path) for path in incomplete)
        )
    report_files = tuple(path for path in entries if path.name != REPORT_LOCK)
    for path in report_files:
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"invalid run report store entry: {path}")
        if path.suffix not in {".json", ".tsv"}:
            raise RuntimeError(f"unknown run report store entry: {path}")
    json_by_stem = {path.stem: path for path in report_files if path.suffix == ".json"}
    tsv_by_stem = {path.stem: path for path in report_files if path.suffix == ".tsv"}
    if json_by_stem.keys() != tsv_by_stem.keys():
        raise RuntimeError("run report JSON/TSV projections are not paired")

    successful: set[Path] = set()
    owner = str(repo.resolve())
    scratch_root = managed_temp(repo)
    for stem, report_path in sorted(json_by_stem.items()):
        report = _run_report_payload(report_path)
        expected_tsv = _report_renderings(report)[1]
        try:
            actual_tsv = tsv_by_stem[stem].read_text(encoding="utf-8")
        except OSError as error:
            raise RuntimeError(f"run report TSV unavailable: {error}") from error
        if actual_tsv != expected_tsv:
            raise RuntimeError(f"run report JSON/TSV drift: {report_path}")
        if report.repo != owner:
            continue
        scratch = Path(report.scratch)
        if scratch.parent != scratch_root or not scratch.name.startswith("run."):
            raise RuntimeError(
                f"run report scratch is outside its repository owner: {report_path}"
            )
        if report.exit_code == 0:
            successful.add(scratch)
    return successful


def gc(
    repo: Path,
    *,
    apply: bool,
    policy: TempPolicy | None = None,
    now: float | None = None,
) -> tuple[list[Path], list[TempFinding]]:
    """Collect only old, marked, unlocked runs; preserve anything ambiguous."""

    effective_policy = storage_manifest().policy.temp if policy is None else policy
    root = managed_temp(repo)
    clock = time.time() if now is None else now
    successful = _successful_run_reports(repo)
    eligible: list[Path] = []
    blocked: list[TempFinding] = []
    for candidate in sorted(root.glob("run.*")):
        marker = candidate / MARKER
        if candidate.is_symlink() or not marker.is_file():
            blocked.append(
                TempFinding(
                    candidate, "unknown", "preserve: missing trusted run marker"
                )
            )
            continue
        try:
            marker_data = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            blocked.append(
                TempFinding(candidate, "unknown", "preserve: invalid run marker")
            )
            continue
        if marker_data.get("repo") != str(repo.resolve()):
            blocked.append(
                TempFinding(
                    candidate,
                    "unknown",
                    "preserve: marker repository does not match scratch owner",
                )
            )
            continue
        completed = candidate in successful
        if (
            not completed
            and clock - marker.stat().st_mtime < effective_policy.orphan_age_seconds
        ):
            blocked.append(
                TempFinding(
                    candidate, "young", "preserve: younger than orphan retention"
                )
            )
            continue
        if _locked(candidate):
            blocked.append(
                TempFinding(candidate, "active", "preserve: active owner lock")
            )
            continue
        protected = _protected_descendant(candidate)
        if protected is not None:
            blocked.append(
                TempFinding(candidate, "protected", f"preserve: contains {protected}")
            )
            continue
        allowed = KNOWN_DIRS | {MARKER, LOCK}
        unknown = {entry.name for entry in candidate.iterdir()} - allowed
        if unknown:
            blocked.append(
                TempFinding(
                    candidate, "unknown", f"preserve: unknown entries {sorted(unknown)}"
                )
            )
            continue
        eligible.append(candidate)
    if apply:
        for candidate in eligible:
            _remove_owned_tree(candidate)
            candidate.rmdir()
    return eligible, blocked


def status(repo: Path) -> dict[str, object]:
    manifest = storage_manifest()
    root = managed_temp(repo)
    runs = tuple(root.glob("run.*"))
    return {
        "repo": str(repo.resolve()),
        "scratch_root": str(root),
        "run_count": len(runs),
        "scratch_bytes": _tree_size(root),
        "state_root": str(state_root()),
        "cache_root": str(cache_root()),
        "warning_bytes": manifest.policy.temp.warning_bytes,
        "failure_bytes": manifest.policy.temp.failure_bytes,
        "orphan_age_seconds": manifest.policy.temp.orphan_age_seconds,
        "report_max_bytes": manifest.policy.report_max_bytes,
        "report_bytes": (
            _report_usage(state_root() / "reports")
            if (state_root() / "reports").is_dir()
            else 0
        ),
        "tmp_findings": sum(
            item.kind in {"prohibited", "residue"} for item in findings()
        ),
    }
