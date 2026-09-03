"""Shared builders for fail-loud Waza evaluation fixtures."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import yaml


def write_eval_suite(
    root: Path,
    relative: str,
    *,
    name: str,
    skill: str,
    model: str,
    skill_directories: list[str],
    graders: list[dict[str, object]],
    tasks: Mapping[str, dict[str, object]],
) -> Path:
    """Write one complete canonical evaluation suite and return its directory."""

    directory = root / relative
    task_directory = directory / "tasks"
    task_directory.mkdir(parents=True)
    (directory / "eval.yaml").write_text(
        yaml.safe_dump(
            {
                "name": f"{name}-eval",
                "skill": skill,
                "config": {
                    "trials_per_task": 1,
                    "model": model,
                    "timeout_seconds": 60,
                    "parallel": False,
                    "max_attempts": 0,
                    "fail_fast": True,
                    "executor": "copilot-sdk",
                    "required_skills": [skill],
                    "skill_directories": skill_directories,
                },
                "graders": graders,
                "tasks": ["tasks/*.yaml"],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    for filename, payload in tasks.items():
        (task_directory / filename).write_text(
            yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
        )
    return directory
