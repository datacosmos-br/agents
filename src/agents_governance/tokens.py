"""Canonical Waza BPE token measurement."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def bpe_tokens(path: Path, root: Path) -> int:
    """Count model tokens with Waza's BPE tokenizer, failing closed."""
    completed = subprocess.run(
        ["waza", "tokens", "count", str(path), "--format", "json", "--tokenizer", "bpe", "--no-update-check"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Waza BPE token count failed for {path}: {completed.stderr.strip()}")
    try:
        payload = json.loads(completed.stdout)
        tokens = payload["totalTokens"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise RuntimeError(f"invalid Waza token output for {path}") from error
    if not isinstance(tokens, int) or tokens < 0:
        raise RuntimeError(f"invalid Waza token count for {path}: {tokens!r}")
    return tokens
