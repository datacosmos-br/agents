"""Run the complete Waza proof under one strict external lock."""

from __future__ import annotations

import fcntl
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from strict_subprocess import capture_strict, describe, publish, run_strict

_WAZA = ("mise", "exec", "--", "waza")


def _run(
    command: tuple[str, ...],
    cwd: Path,
    label: str,
    environment: dict[str, str] | None = None,
) -> str:
    return run_strict(command, cwd, f"WAZA {label}", environment)


def _state_root(repository: Path) -> Path:
    configured = os.environ.get("WAZA_STATE_ROOT")
    if configured is None:
        raise ValueError("WAZA_STATE_ROOT is required")
    raw = Path(configured)
    if not raw.is_absolute() or raw.is_relative_to(repository):
        raise ValueError("WAZA_STATE_ROOT must be an absolute external path")
    if raw.name != "waza" or raw.parent.name != "agents-governance":
        raise ValueError(f"refusing unexpected Waza state root: {raw}")
    for ancestor in (raw, *raw.parents):
        if ancestor.exists() and ancestor.is_symlink():
            raise ValueError(f"Waza state ancestry must be physical: {ancestor}")
    raw.mkdir(mode=0o700, parents=True, exist_ok=True)
    return raw.resolve()


_WAZA_MINIMUM_VERSION = (0, 38, 7)


def _spec_command(skill: Path, evaluation: Path) -> tuple[str, ...]:
    return (
        *_WAZA,
        "spec",
        "verify",
        "--skill",
        str(skill),
        "--eval",
        str(evaluation),
        "--threshold",
        "1",
        "--fail",
        "--format",
        "human",
    )


def _verify_suites(
    repository: Path, projection: Path, evaluations: tuple[Path, ...]
) -> int:
    """Verify every projected suite concurrently; publish evidence in order.

    Each ``waza spec verify`` reads only the immutable projection, so the
    suites are independent: a bounded pool runs them in parallel to keep the
    gate inside its budget, while evidence is published in the sorted suite
    order and the first failure escapes as its native exception with the
    suite's own stdout/stderr forwarded first.
    """
    jobs: list[tuple[str, tuple[str, ...]]] = []
    for evaluation in evaluations:
        name = evaluation.parent.name
        owners = tuple(
            path for path in (projection / "skills").rglob(name) if path.is_dir()
        )
        if len(owners) != 1:
            raise ValueError(f"projected skill owner is not unique: {name}")
        jobs.append((name, _spec_command(owners[0], evaluation)))
    workers = max(1, min(len(jobs), os.cpu_count() or 1))
    verified = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(capture_strict, command, repository, f"WAZA spec {name}")
            for name, command in jobs
        ]
        for (name, command), future in zip(jobs, futures, strict=True):
            header = describe(command, repository, f"WAZA spec {name}")
            try:
                stdout, stderr = future.result()
            except subprocess.CalledProcessError as failure:
                for pending in futures:
                    pending.cancel()
                publish(header, failure.stdout or "", failure.stderr or "")
                raise
            except BaseException:
                for pending in futures:
                    pending.cancel()
                print(header, flush=True)
                raise
            publish(header, stdout, stderr)
            verified += 1
    return verified


def _verify(repository: Path, projection: Path) -> None:
    version = _run((*_WAZA, "--version"), repository, "version")
    # The toolchain owner (.mise.toml) selects the release; the gate proves a
    # compatible floor so newer toolchain selections never break this gate.
    digits = tuple(
        int(part)
        for part in version.strip().removeprefix("waza version ").split(".")[:3]
        if part.isdigit()
    )
    if len(digits) != 3 or digits < _WAZA_MINIMUM_VERSION:
        raise ValueError(
            f"waza below declared floor {_WAZA_MINIMUM_VERSION}: {version.strip()!r}"
        )
    environment = dict(os.environ)
    environment["WAZA_PROJECTION_ROOT"] = str(projection)
    _run(
        (sys.executable, "tools/render_waza_projection.py"),
        repository,
        "projection fixed point",
        environment,
    )
    _run(
        (
            *_WAZA,
            "tokens",
            "check",
            str(projection / "skills"),
            "--strict",
            "--no-update-check",
        ),
        repository,
        "projected skill token budgets",
    )
    for surface in (repository / "rules", repository / "commands"):
        _run(
            (*_WAZA, "tokens", "check", str(surface), "--strict", "--no-update-check"),
            repository,
            f"{surface.name} token budgets",
        )
    evaluations = tuple(sorted((projection / "evals").glob("*/eval.yaml")))
    if not evaluations:
        raise ValueError("Waza projection contains no evaluation suites")
    verified = _verify_suites(repository, projection, evaluations)
    if verified != len(evaluations):
        raise RuntimeError(
            f"Waza verified {verified} suites, expected {len(evaluations)}"
        )
    print(f"WAZA spec verification: {verified} suites", flush=True)


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    state = _state_root(repository)
    lock_path = state / "waza.lock"
    if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
        raise ValueError(f"Waza lock must be a physical file: {lock_path}")
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with tempfile.TemporaryDirectory(prefix="gate-", dir=state) as temporary:
            _verify(repository, Path(temporary) / "waza-projection")


if __name__ == "__main__":
    main()
