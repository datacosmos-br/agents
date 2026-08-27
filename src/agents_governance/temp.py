"""Bounded, repository-local scratch execution and conservative garbage collection."""

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

SYSTEM_TEMP = Path("/tmp")
MARKER = ".agents-temp-run.json"
LOCK = ".agents-temp-run.lock"
KNOWN_DIRS = frozenset(
    {"tmp", "go-tmp", "go-build", "python", "node", "cargo", "gradle", "ccache"}
)
PROHIBITED_NAMES = frozenset({".git", ".dolt", ".venv", "venv", "node_modules"})
MAIN_THREAD_ID = threading.get_ident()
DATABASE_SUFFIXES = frozenset({".db", ".sqlite", ".sqlite3"})


@dataclass(frozen=True)
class TempPolicy:
    warning_bytes: int = 1 << 30
    failure_bytes: int = 5 << 30
    orphan_age_seconds: int = 7 * 24 * 60 * 60
    poll_seconds: float = 0.25


DEFAULT_POLICY = TempPolicy()


class _RunInterrupted(Exception):
    def __init__(self, signum: int) -> None:
        self.signum = signum


def _terminate_group(process: subprocess.Popen[bytes] | subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


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


def _xdg(name: str, fallback: str) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else Path.home() / fallback


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
    """Return the repository-local scratch owner without following symlinks."""

    destination = repo.resolve() / ".test-tmp"
    if destination.is_symlink():
        raise RuntimeError(f"scratch root must not be a symlink: {destination}")
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    filesystem = subprocess.run(
        ["stat", "-f", "-c", "%T", str(destination)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if filesystem == "btrfs":
        subprocess.run(
            ["chattr", "+C", str(destination)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
    return destination


def _mkdir(path: Path) -> Path:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError(f"managed path must not be a symlink: {path}")
    return path


def create_run(repo: Path) -> tuple[Path, IO[str]]:
    scratch = Path(tempfile.mkdtemp(prefix="run.", dir=managed_temp(repo)))
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


def managed_env(repo: Path, scratch: Path) -> dict[str, str]:
    """Build isolated test/build paths while sharing reusable dependency caches."""

    environment = os.environ.copy()
    shared = cache_root()
    mappings = {
        "TMPDIR": scratch / "tmp",
        "GOTMPDIR": scratch / "go-tmp",
        "GOCACHE": scratch / "go-build",
        "GOMODCACHE": shared / "go-mod",
        "UV_CACHE_DIR": shared / "uv",
        "PIP_CACHE_DIR": shared / "pip",
        "npm_config_cache": shared / "npm",
        "NODE_COMPILE_CACHE": shared / "node-compile-cache",
        "BUN_INSTALL_CACHE_DIR": shared / "bun",
        "CARGO_HOME": shared / "cargo",
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
        except (FileNotFoundError, PermissionError):
            return 0
    total = 0
    try:
        entries = list(os.scandir(path))
    except (FileNotFoundError, NotADirectoryError, PermissionError):
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
        except (FileNotFoundError, PermissionError):
            continue
    return total


def _write_report(report: RunReport) -> None:
    reports = _mkdir(state_root() / "reports")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    payload = asdict(report)
    (reports / f"{stamp}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    columns = tuple(payload)
    values = tuple(json.dumps(payload[key], separators=(",", ":")) for key in columns)
    (reports / f"{stamp}.tsv").write_text(
        "\t".join(columns) + "\n" + "\t".join(values) + "\n", encoding="utf-8"
    )


def run_command(
    command: Sequence[str], cwd: Path, policy: TempPolicy = DEFAULT_POLICY
) -> RunReport:
    """Run one owned process group with isolated scratch and bounded growth."""

    if not command:
        raise ValueError("temp run requires a command after --")
    repo = resolve_repo(cwd)
    scratch, lock_file = create_run(repo)
    started = datetime.now(UTC)
    process = subprocess.Popen(
        tuple(command), cwd=cwd, env=managed_env(repo, scratch), start_new_session=True
    )
    peak = 0
    warned = False
    stopped = False
    interrupted_signal: int | None = None
    previous_handlers: dict[signal.Signals, Any] = {}

    def interrupt(signum: int, _frame: object) -> None:
        raise _RunInterrupted(signum)

    if threading.get_ident() == MAIN_THREAD_ID:
        for watched in (signal.SIGINT, signal.SIGTERM):
            previous_handlers[watched] = signal.signal(watched, interrupt)
    try:
        while process.poll() is None:
            size = _tree_size(scratch)
            peak = max(peak, size)
            if size >= policy.warning_bytes and not warned:
                print(
                    f"WARNING: owned scratch reached {size} bytes: {scratch}",
                    file=sys.stderr,
                )
                warned = True
            if size >= policy.failure_bytes:
                _terminate_group(process)
                stopped = True
                break
            time.sleep(policy.poll_seconds)
        exit_code = process.wait()
    except _RunInterrupted as error:
        interrupted_signal = error.signum
        for watched in previous_handlers:
            signal.signal(watched, signal.SIG_IGN)
        _terminate_group(process)
        exit_code = 128 + error.signum
    except KeyboardInterrupt:
        interrupted_signal = int(signal.SIGINT)
        for watched in previous_handlers:
            signal.signal(watched, signal.SIG_IGN)
        _terminate_group(process)
        exit_code = 128 + int(signal.SIGINT)
    finally:
        for watched, handler in previous_handlers.items():
            signal.signal(watched, handler)
        peak = max(peak, _tree_size(scratch))
        lock_file.close()
    if (stopped or interrupted_signal is not None) and exit_code == 0:
        exit_code = 70
    retained = True
    if exit_code == 0:
        allowed = KNOWN_DIRS | {MARKER, LOCK}
        if {entry.name for entry in scratch.iterdir()} <= allowed:
            _remove_owned_tree(scratch, allow_owned_symlinks=True)
            scratch.rmdir()
            retained = False
    report = RunReport(
        command=tuple(command),
        repo=str(repo),
        scratch=str(scratch),
        started_at=started.isoformat(),
        finished_at=datetime.now(UTC).isoformat(),
        exit_code=exit_code,
        peak_bytes=peak,
        warning_bytes=policy.warning_bytes,
        failure_bytes=policy.failure_bytes,
        stopped_for_limit=stopped,
        scratch_retained=retained,
    )
    _write_report(report)
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
    try:
        entries = list(temp_root.iterdir())
    except FileNotFoundError:
        return result
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


def storage_manifest() -> dict[str, object]:
    """Load machine-local storage ownership without embedding it in this package."""
    config_home = _xdg("XDG_CONFIG_HOME", ".config")
    path = config_home / "environment.d" / "storage.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise RuntimeError(f"storage manifest unavailable: {error}") from error
    if data.get("version") != 1:
        raise RuntimeError("unsupported storage manifest version")
    return data


def _expand_local_path(raw: str) -> Path:
    values = {
        "HOME": str(Path.home()),
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


def registered_repositories() -> tuple[Path, ...]:
    entries = storage_manifest().get("repositories", [])
    if not isinstance(entries, list):
        raise TypeError("storage repositories must be an array")
    result: list[Path] = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise TypeError("invalid storage repository entry")
        path = _expand_local_path(entry["path"])
        if not path.is_dir() or resolve_repo(path) != path.resolve():
            raise RuntimeError(f"registered repository is not a Git root: {path}")
        result.append(path.resolve())
    return tuple(dict.fromkeys(result))


def global_findings() -> list[TempFinding]:
    """Audit system temp and every explicitly registered repository."""
    result = list(findings(SYSTEM_TEMP))
    for repo in registered_repositories():
        result.extend(repository_findings(repo))
    policy = storage_manifest().get("policy", {})
    if not isinstance(policy, dict):
        raise TypeError("storage policy must be a table")
    global_temp = _expand_local_path(
        str(policy.get("global_temp", "${HOME}/.local/tmp"))
    )
    maximum = int(policy.get("global_temp_max_bytes", 256 << 20))
    size = _tree_size(global_temp)
    if size > maximum:
        result.append(
            TempFinding(
                global_temp,
                "prohibited",
                f"global ephemeral storage exceeds {maximum} bytes",
                size,
            )
        )
    return sorted(result, key=lambda item: str(item.path))


def gc_all(*, apply: bool) -> tuple[list[Path], list[TempFinding]]:
    eligible: list[Path] = []
    blocked: list[TempFinding] = []
    for repo in registered_repositories():
        repo_eligible, repo_blocked = gc(repo, apply=apply)
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


def _remove_owned_tree(path: Path, *, allow_owned_symlinks: bool = False) -> None:
    for entry in os.scandir(path):
        child = Path(entry.path)
        if entry.is_symlink():
            if not allow_owned_symlinks:
                raise RuntimeError(f"refused symlink during removal: {child}")
            child.unlink()
            continue
        if entry.is_dir(follow_symlinks=False):
            _remove_owned_tree(child, allow_owned_symlinks=allow_owned_symlinks)
            child.rmdir()
        else:
            child.unlink()


def gc(
    repo: Path,
    *,
    apply: bool,
    policy: TempPolicy = DEFAULT_POLICY,
    now: float | None = None,
) -> tuple[list[Path], list[TempFinding]]:
    """Collect only old, marked, unlocked runs; preserve anything ambiguous."""

    root = managed_temp(repo)
    clock = time.time() if now is None else now
    successful: set[Path] = set()
    reports = state_root() / "reports"
    if reports.is_dir():
        for report_path in reports.glob("*.json"):
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
                if report.get("exit_code") == 0:
                    successful.add(Path(report["scratch"]))
            except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError):
                continue
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
        completed = candidate in successful
        if not completed and clock - marker.stat().st_mtime < policy.orphan_age_seconds:
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
        protected = None if completed else _protected_descendant(candidate)
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
            _remove_owned_tree(candidate, allow_owned_symlinks=candidate in successful)
            candidate.rmdir()
    return eligible, blocked


def status(repo: Path) -> dict[str, object]:
    root = managed_temp(repo)
    runs = tuple(root.glob("run.*"))
    return {
        "repo": str(repo.resolve()),
        "scratch_root": str(root),
        "run_count": len(runs),
        "scratch_bytes": _tree_size(root),
        "state_root": str(state_root()),
        "cache_root": str(cache_root()),
        "tmp_findings": sum(
            item.kind in {"prohibited", "residue"} for item in findings()
        ),
    }
