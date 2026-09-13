"""Execute one causal subprocess and reject warning or empty evidence."""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path

_WARNING = re.compile(r"\bwarn(?:ing)?\b", re.IGNORECASE)


def describe(command: tuple[str, ...], cwd: Path, label: str) -> str:
    """Return the evidence header naming label, working directory and argv."""
    return f"{label}\ncwd: {cwd}\ncommand: {shlex.join(command)}"


def capture_strict(
    command: tuple[str, ...],
    cwd: Path,
    label: str,
    environment: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Run one subprocess and return ``(stdout, stderr)``; raise on bad evidence.

    Performs no console I/O, so callers that run several commands concurrently
    can publish each command's evidence in a deterministic order. Nonzero exit
    propagates as the native ``CalledProcessError``; empty or warning-bearing
    output raises ``RuntimeError``.
    """
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    completed.check_returncode()
    output = f"{completed.stdout}\n{completed.stderr}"
    if not output.strip():
        raise RuntimeError(f"subprocess produced no evidence: {label}")
    if _WARNING.search(output):
        raise RuntimeError(f"subprocess emitted a forbidden warning: {label}")
    return completed.stdout, completed.stderr


def publish(header: str, stdout: str, stderr: str) -> None:
    """Forward one command's exact evidence to the console."""
    print(header, flush=True)
    sys.stdout.write(stdout)
    sys.stdout.flush()
    sys.stderr.write(stderr)
    sys.stderr.flush()


def run_strict(
    command: tuple[str, ...],
    cwd: Path,
    label: str,
    environment: dict[str, str] | None = None,
) -> str:
    """Forward exact output and raise on nonzero, empty, or warning evidence."""
    header = describe(command, cwd, label)
    print(header, flush=True)
    try:
        stdout, stderr = capture_strict(command, cwd, label, environment)
    except subprocess.CalledProcessError as failure:
        sys.stdout.write(failure.stdout or "")
        sys.stdout.flush()
        sys.stderr.write(failure.stderr or "")
        sys.stderr.flush()
        raise
    sys.stdout.write(stdout)
    sys.stdout.flush()
    sys.stderr.write(stderr)
    sys.stderr.flush()
    return f"{stdout}\n{stderr}"


__all__ = ("capture_strict", "describe", "publish", "run_strict")
