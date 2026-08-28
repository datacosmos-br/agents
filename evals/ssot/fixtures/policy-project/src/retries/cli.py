from __future__ import annotations

import sys

from retries.worker import attempts_for


def main() -> int:
    channel = sys.argv[1]
    print(attempts_for(channel))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
