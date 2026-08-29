"""Single-verb command-line facade for canonical agent governance."""

from __future__ import annotations

import sys

from .resources import resource_root
from .runtime import WORKFLOWS


def main() -> None:
    arguments = tuple(sys.argv[1:])
    if len(arguments) != 1 or arguments[0] not in WORKFLOWS:
        raise ValueError("agentsctl requires exactly one optionless verb")
    WORKFLOWS[arguments[0]](resource_root())


if __name__ == "__main__":
    main()
