"""Canonical Waza BPE token measurement."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def bpe_tokens(path: Path, root: Path) -> int:
    """Count model tokens with Waza's BPE tokenizer, failing closed."""
    completed = subprocess.run(
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
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    tokens = payload["totalTokens"]
    if not isinstance(tokens, int) or tokens < 0:
        raise RuntimeError(f"invalid Waza token count for {path}: {tokens!r}")
    return tokens
