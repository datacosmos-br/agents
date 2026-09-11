#!/usr/bin/env python3
"""Convert `bd list --json` output to the wip-beads CSV input contract."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

COLUMNS = [
    "id",
    "title",
    "status",
    "issue_type",
    "priority",
    "parent_id",
    "labels",
    "dep_count",
]


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(
            "usage: bd_json_to_csv.py <bd-list.json> <wip-beads.csv>"
        )
    source = Path(sys.argv[1])
    target = Path(sys.argv[2])
    data = json.loads(source.read_text(encoding="utf-8"))
    rows = [COLUMNS]
    for bead in data:
        rows.append(
            [
                bead["id"],
                bead["title"],
                bead["status"],
                bead["issue_type"],
                bead["priority"],
                bead.get("parent") or "",
                "|".join(bead.get("labels", [])),
                bead.get("dependency_count", 0),
            ]
        )
    with target.open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(rows)


if __name__ == "__main__":
    main()
