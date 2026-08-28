"""Single-verb command-line facade for canonical agent governance."""

from __future__ import annotations

import sys

from .runtime import WORKFLOWS, repository_root


def main() -> None:
    arguments = tuple(sys.argv[1:])
    if len(arguments) != 1 or arguments[0] not in WORKFLOWS:
        raise ValueError("agentsctl requires exactly one optionless verb")
    WORKFLOWS[arguments[0]](repository_root())


if __name__ == "__main__":
    main()
