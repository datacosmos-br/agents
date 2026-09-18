"""Validate Python resources discovered through the canonical bundle inventory."""

from __future__ import annotations

import os
from pathlib import Path

from strict_subprocess import run_strict

from agents_governance import GovernanceBundle


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    bundle = GovernanceBundle.load(root)
    resources = tuple(
        sorted(
            str(resource.path)
            for skill in bundle.skills
            for resource in skill.resources
            if resource.format == "utf-8" and resource.path.suffix == ".py"
        )
    )
    if not resources:
        raise ValueError("bundle exposes no executable Python resources")
    operation = os.environ["PYTHON_RESOURCES_OPERATION"]
    commands: tuple[tuple[str, ...], ...]
    if operation == "format":
        commands = (("ruff", "format", *resources),)
    elif operation == "fix":
        commands = (("ruff", "check", "--fix", *resources),)
    elif operation == "check":
        commands = (
            ("ruff", "check", *resources),
            ("ruff", "format", "--check", *resources),
            ("pyright", *resources),
            ("mypy", *resources),
        )
    else:
        raise ValueError(f"unknown Python resource operation: {operation}")
    for command in commands:
        run_strict(command, root, f"Python resources: {operation}")


if __name__ == "__main__":
    main()
