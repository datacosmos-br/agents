#!/usr/bin/env python3
"""Docs linking gate: ADR index bijection and relative link resolution.

Stdlib-only by design: this gate must run exactly as CI runs it, without
project provisioning. It proves two linking contracts:

1. The ``docs/adr/README.md`` index table is a bijection with the physical
   ``docs/adr/ADR-NNNN-*.md`` files: every file has exactly one row and every
   row resolves to exactly one file.
2. Every relative Markdown link inside ``docs/**/*.md`` resolves to a
   physical file in this repository.

Any defect exits non-zero with the full defect list; silence proves green.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ADR_ROW = re.compile(r"`(ADR-\d{4})`")
_ADR_FILE = re.compile(r"(ADR-\d{4})-.*\.md\Z")
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def _adr_bijection(root: Path) -> list[str]:
    defects: list[str] = []
    adr_dir = root / "docs" / "adr"
    readme = adr_dir / "README.md"
    indexed = _ADR_ROW.findall(readme.read_text(encoding="utf-8"))
    if len(indexed) != len(set(indexed)):
        duplicated = sorted(one for one in set(indexed) if indexed.count(one) > 1)
        defects.append(f"ADR index duplicates: {', '.join(duplicated)}")
    files: dict[str, Path] = {}
    for path in adr_dir.glob("ADR-*.md"):
        match = _ADR_FILE.fullmatch(path.name)
        if match is None:
            defects.append(f"ADR file name does not carry an ADR number: {path.name}")
            continue
        files[match.group(1)] = path
    for number in sorted(set(indexed) - set(files)):
        defects.append(f"ADR index row without file: {number}")
    for number in sorted(set(files) - set(indexed)):
        defects.append(f"ADR file without index row: {files[number].name}")
    return defects


def _relative_links(root: Path) -> list[str]:
    defects: list[str] = []
    for path in sorted((root / "docs").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        in_fence = False
        for line in text.splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in _LINK.findall(line):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                candidate = target.split("#", 1)[0]
                if not candidate:
                    continue
                resolved = (path.parent / candidate).resolve()
                if not resolved.is_file():
                    defects.append(f"{path.relative_to(root)}: broken link -> {target}")
    return defects


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    defects = _adr_bijection(root) + _relative_links(root)
    if defects:
        print("DOCS LINK GATE RED:")
        for defect in defects:
            print(f"  - {defect}")
        return 1
    adr_count = len(tuple((root / "docs" / "adr").glob("ADR-*.md")))
    print(
        f"DOCS LINK GATE OK: ADR bijection holds ({adr_count} files), relative links resolve"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
