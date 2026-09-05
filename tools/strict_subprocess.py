"""Execute one causal subprocess and reject warning or empty evidence."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_WARNING = re.compile(r"\bwarn(?:ing)?\b", re.IGNORECASE)


def run_strict(
    command: tuple[str, ...],
    cwd: Path,
    label: str,
    environment: dict[str, str] | None = None,
) -> str:
    """Forward exact output and raise on nonzero, empty, or warning evidence."""

    print(label, flush=True)
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
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
        raise RuntimeError(f"subprocess produced no evidence: {label}")
    if _WARNING.search(output):
        raise RuntimeError(f"subprocess emitted a forbidden warning: {label}")
    return output


__all__ = ("run_strict",)
