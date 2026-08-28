from __future__ import annotations

import sys

from delivery.worker import timeout_for


def main() -> None:
    channel = sys.argv[1]
    print(timeout_for(channel))


if __name__ == "__main__":
    main()
