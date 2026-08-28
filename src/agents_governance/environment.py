"""Strict process-environment validation."""

from __future__ import annotations

import os
import re

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_UNEXPANDED = re.compile(
    r"(?:\$[A-Za-z_][A-Za-z0-9_]*|\$\{[^{}]+\}|%[A-Za-z_][A-Za-z0-9_]*%)"
)


def required_environment(name: str, *, conflicts: tuple[str, ...] = ()) -> str:
    """Return one exact required value or raise before the caller has effects."""
    if _NAME.fullmatch(name) is None:
        raise ValueError("invalid required environment variable name")
    if len(set(conflicts)) != len(conflicts) or name in conflicts:
        raise ValueError(f"invalid conflicting environment names for {name}")
    for conflict in conflicts:
        if _NAME.fullmatch(conflict) is None:
            raise ValueError(f"invalid conflicting environment name for {name}")
        if conflict in os.environ:
            raise ValueError(f"conflicting environment variable for {name}: {conflict}")

    if name not in os.environ:
        raise ValueError(f"required environment variable is missing or empty: {name}")
    value = os.environ[name]
    if not value or value != value.strip():
        raise ValueError(f"required environment variable is missing or empty: {name}")
    if _UNEXPANDED.search(value) is not None:
        raise ValueError(f"required environment variable is unexpanded: {name}")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"required environment variable is invalid: {name}")
    return value
