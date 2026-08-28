"""Canonical Waza BPE token measurement."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _tokens(command: list[str], root: Path, content: str | None = None) -> int:
    completed = subprocess.run(
        command,
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        input=content,
    )
    payload = json.loads(completed.stdout)
    tokens = payload["totalTokens"]
    if not isinstance(tokens, int) or tokens < 0:
        raise RuntimeError(f"invalid Waza token count: {tokens!r}")
    return tokens


def bpe_tokens(path: Path, root: Path) -> int:
    """Count one physical source with Waza's BPE tokenizer, failing closed."""

    return _tokens(
        [
            "waza",
            "tokens",
            "count",
            str(path),
            "--format",
            "json",
            "--tokenizer",
            "bpe",
            "--no-update-check",
        ],
        root,
    )


def bpe_content(content: str, root: Path) -> int:
    """Count in-memory text through Waza stdin without staging a source file."""

    return _tokens(
        [
            "waza",
            "tokens",
            "count",
            "/dev/stdin",
            "--format",
            "json",
            "--tokenizer",
            "bpe",
            "--no-update-check",
        ],
        root,
        content,
    )


__all__ = ("bpe_content", "bpe_tokens")
