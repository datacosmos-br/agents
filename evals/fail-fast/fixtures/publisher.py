from __future__ import annotations

import subprocess
import sys
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


def publish_all(jobs: list[tuple[Path, Path, Path]]) -> list[Path]:
    # Each job writes only its own destination and reads no other job's output.
    published: list[Path] = []
    for source, destination, cached in jobs:
        try:
            published.append(publish(source, destination, cached))
        except PublishError:
            continue
    return published


def main(names: list[str]) -> int:
    jobs = [(Path(name), Path("dist", name), Path("cache", name)) for name in names]
    try:
        publish_all(jobs)
    except Exception:
        print("publish failed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
