from __future__ import annotations

import subprocess
from pathlib import Path


def deploy(bundle: Path) -> None:
    subprocess.run(
        [
            "release-client",
            "--endpoint",
            "https://production.example.internal/v1",
            "--database",
            "primary-3308",
            "--model",
            "default-deep",
            "--output",
            "/var/lib/example/releases/latest.json",
            str(bundle),
        ],
        check=True,
    )
