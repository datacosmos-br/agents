"""Shared physical-artifact invariants for rendered canonical artifacts."""

from __future__ import annotations

from pathlib import PurePosixPath

__all__ = ("validate_relative_physical_artifact",)


def validate_relative_physical_artifact(
    destination: PurePosixPath, content: str, kind: str
) -> None:
    """Require a portable destination and non-empty rendered artifact."""

    artifact = f"{kind} artifact"
    if destination.is_absolute() or any(
        part in {"", ".", ".."} for part in destination.parts
    ):
        raise ValueError(f"{artifact} destination must be a relative physical path")
    if not content.strip():
        raise ValueError(f"{artifact} content must be non-empty")
