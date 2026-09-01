"""Strict storage-manifest and repository-placement owner."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

SYSTEM_TEMP = Path("/tmp")
_CONFIG_PATH = Path("config/storage.toml")
_ROOT_FIELDS = frozenset({"repositories", "version"})
_REPOSITORY_FIELDS = frozenset({"path"})
_RESIDUE = ("$HOME", ".archive", ".skills-archive", "~")


@dataclass(frozen=True)
class StorageManifest:
    version: int
    repositories: tuple[Path, ...]
    shell_temp: Path


def _mapping(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{context} must be a table")
    raw = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in raw):
        raise TypeError(f"{context} keys must be strings")
    return cast(dict[str, object], raw)


def _exact(value: dict[str, object], fields: frozenset[str], context: str) -> None:
    if frozenset(value) != fields:
        raise ValueError(
            f"{context} fields must equal {', '.join(sorted(fields))}; "
            f"got {', '.join(sorted(value)) or 'none'}"
        )


def _canonical(path: Path, context: str) -> Path:
    normalized = Path(os.path.abspath(path))
    canonical = normalized.resolve(strict=True)
    if canonical != normalized:
        raise ValueError(f"{context} must identify a physical path: {normalized}")
    return canonical


def _inside(path: Path, parent: Path) -> bool:
    candidate = path.resolve(strict=True).parts
    owner = parent.resolve(strict=True).parts
    return candidate[: len(owner)] == owner


def _configured_path(raw: object, config_dir: Path, context: str) -> Path:
    if not isinstance(raw, str) or not raw or raw != raw.strip():
        raise TypeError(f"{context} must be a non-empty trimmed string")
    expanded = raw.replace("${CONFIG_DIR}", str(config_dir))
    if "$" in expanded:
        raise ValueError(f"{context} contains an unresolved variable: {raw}")
    path = Path(expanded)
    if not path.is_absolute():
        raise ValueError(f"{context} must expand to an absolute path: {raw}")
    return _canonical(path, context)


def _repository(path: Path) -> None:
    if not path.is_dir():
        raise ValueError(f"registered repository must be a physical directory: {path}")
    if path == SYSTEM_TEMP.resolve(strict=True):
        raise ValueError("system temp itself cannot be a repository root")


def _storage_manifest(repository: Path) -> StorageManifest:
    path = _canonical(repository / _CONFIG_PATH, "storage configuration")
    if not path.is_file():
        raise ValueError(f"storage configuration must be a file: {path}")
    payload = _mapping(tomllib.loads(path.read_text(encoding="utf-8")), "storage")
    _exact(payload, _ROOT_FIELDS, "storage")
    if payload["version"] != 3:
        raise ValueError("storage.version must equal integer 3")
    raw_repositories = payload["repositories"]
    if not isinstance(raw_repositories, list) or not raw_repositories:
        raise TypeError("storage.repositories must be a non-empty table array")
    repositories: list[Path] = []
    for index, raw_entry in enumerate(cast(list[object], raw_repositories)):
        entry = _mapping(raw_entry, f"storage.repositories[{index}]")
        _exact(entry, _REPOSITORY_FIELDS, f"storage.repositories[{index}]")
        registered = _configured_path(
            entry["path"], path.parent, f"storage.repositories[{index}].path"
        )
        if registered in repositories:
            raise ValueError(f"duplicate registered repository: {registered}")
        _repository(registered)
        repositories.append(registered)
    shell_temp = _canonical(Path.home() / "tmp", "shell temp")
    if not shell_temp.is_dir():
        raise ValueError(f"shell_temp must be a physical directory: {shell_temp}")
    if _inside(shell_temp, SYSTEM_TEMP):
        raise ValueError(f"shell_temp must not use /tmp: {shell_temp}")
    for registered in repositories:
        if _inside(shell_temp, registered) or _inside(registered, shell_temp):
            raise ValueError(
                "shell_temp and repository roots must be disjoint: "
                f"{shell_temp}, {registered}"
            )
    return StorageManifest(3, tuple(repositories), shell_temp)


def require_repository_storage(root: Path) -> StorageManifest:
    """Validate the checkout's derived storage authority or raise immediately."""

    repository = _canonical(root, "repository root")
    _repository(repository)
    manifest = _storage_manifest(repository)
    if repository not in manifest.repositories:
        raise ValueError(
            f"repository is absent from the storage authority: {repository}"
        )
    for name in _RESIDUE:
        candidate = repository / name
        if candidate.exists() or candidate.is_symlink():
            raise ValueError(
                f"repository contains prohibited storage residue: {candidate}"
            )
    return manifest


__all__ = ("require_repository_storage",)
