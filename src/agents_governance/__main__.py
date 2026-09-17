"""Allow ``python -m agents_governance`` as an alternative to agentsctl."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
