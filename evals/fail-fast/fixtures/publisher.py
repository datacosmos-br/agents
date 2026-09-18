from __future__ import annotations

import subprocess
from pathlib import Path


class PublishError(RuntimeError):
    pass


def publish(source: Path, destination: Path, cached: Path) -> Path:
    try:
        completed = subprocess.run(
            ["artifact-publisher", str(source), str(destination)],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return cached
    if completed.returncode != 0:
        return cached
    return destination
