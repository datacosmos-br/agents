"""Run the complete Waza proof under one strict external lock."""

from __future__ import annotations

import fcntl
import os
import re
import subprocess
import sys
from pathlib import Path

_WARNING = re.compile(r"\bwarn(?:ing)?\b", re.IGNORECASE)
_WAZA = ("mise", "exec", "--", "waza")


def _run(command: tuple[str, ...], cwd: Path, label: str) -> str:
    print(f"WAZA {label}", flush=True)
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(completed.stdout)
    sys.stdout.flush()
    sys.stderr.write(completed.stderr)
    sys.stderr.flush()
    completed.check_returncode()
    output = f"{completed.stdout}\n{completed.stderr}"
    if not output.strip():
        raise RuntimeError(f"Waza produced no evidence for {label}")
    if _WARNING.search(output):
        raise RuntimeError(f"Waza emitted a forbidden warning for {label}")
    return output


def _projection_root(repository: Path) -> Path:
    configured = os.environ.get("WAZA_PROJECTION_ROOT")
    if configured is None:
        raise ValueError("WAZA_PROJECTION_ROOT is required")
    raw = Path(configured)
    if not raw.is_absolute() or raw.is_relative_to(repository):
        raise ValueError("WAZA_PROJECTION_ROOT must be an absolute external path")
    if raw.name != "waza-projection" or raw.parent.name != "agents-governance":
        raise ValueError(f"refusing unexpected Waza projection root: {raw}")
    for ancestor in (raw, *raw.parents):
        if ancestor.exists() and ancestor.is_symlink():
            raise ValueError(f"Waza projection ancestry must be physical: {ancestor}")
    raw.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    return raw.resolve()


def _verify(repository: Path, projection: Path) -> None:
    version = _run((*_WAZA, "--version"), repository, "version")
    if version.strip() != "waza version 0.38.7":
        raise ValueError(f"unexpected Waza version: {version.strip()!r}")
    _run(
        (sys.executable, "tools/render_waza_projection.py"),
        repository,
        "projection fixed point",
    )
    _run(
        (*_WAZA, "tokens", "check", "./skills", "--strict", "--no-update-check"),
        projection,
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
    verified = 0
    for evaluation in evaluations:
        name = evaluation.parent.name
        owners = tuple(
            path for path in (projection / "skills").rglob(name) if path.is_dir()
        )
        if len(owners) != 1:
            raise ValueError(f"projected skill owner is not unique: {name}")
        _run(
            (
                *_WAZA,
                "spec",
                "verify",
                "--skill",
                str(owners[0]),
                "--eval",
                str(evaluation),
                "--threshold",
                "1",
                "--fail",
                "--format",
                "human",
            ),
            projection,
            f"spec {name}",
        )
        verified += 1
    if verified != len(evaluations):
        raise RuntimeError(
            f"Waza verified {verified} suites, expected {len(evaluations)}"
        )
    print(f"WAZA spec verification: {verified} suites", flush=True)


def main() -> None:
    repository = Path(__file__).resolve().parents[1]
    projection = _projection_root(repository)
    lock_path = projection.parent / "waza.lock"
    if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
        raise ValueError(f"Waza lock must be a physical file: {lock_path}")
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _verify(repository, projection)


if __name__ == "__main__":
    main()
