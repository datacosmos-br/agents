"""Canonical strict-prelude semantic source."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

PRELUDE_START = "<!-- AIHUB-INVIOLABLE-LAW-PRELUDE v1 -->"
PRELUDE_END = "<!-- /AIHUB-INVIOLABLE-LAW-PRELUDE -->"


@dataclass(frozen=True)
class LawSurface:
    """Exact Agents-owned prelude exposed to a delivery consumer."""

    prelude: str
    digest: str

    @classmethod
    def load(cls, root: Path) -> LawSurface:
        source = root / "AGENTS.md"
        content = source.read_text(encoding="utf-8")
        if not content.startswith(PRELUDE_START + "\n"):
            raise ValueError(
                f"canonical AGENTS.md must start with {PRELUDE_START}: {source}"
            )
        end = content.find(PRELUDE_END)
        if end < 0:
            raise ValueError(f"canonical AGENTS.md is missing {PRELUDE_END}: {source}")
        boundary = end + len(PRELUDE_END)
        prelude = content[:boundary] + "\n"
        if content[boundary : boundary + 2] != "\n\n":
            raise ValueError(
                f"canonical law prelude must be followed by one blank line: {source}"
            )
        return cls(prelude, hashlib.sha256(prelude.encode()).hexdigest())


__all__ = ("PRELUDE_END", "PRELUDE_START", "LawSurface")
