"""Atomic retirement of the obsolete shell environment runtime."""

from __future__ import annotations

import hashlib
import stat
import tempfile
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from .cleanup import (
    PreparedPublication,
    Publication,
    remove_physical,
    run_with_cleanup,
)

_FULL_REMOVALS: dict[str, frozenset[str]] = {
    ".config/shell/env.sh": frozenset(
        {"07f6c01f2dd9dc78cb179102be44d2b71a05b8e2246c0eb94c509219221d69e1"}
    ),
    ".config/shell/env.zsh": frozenset(
        {"c19e8085c9960ddedc5050bc2748af10924a6dfa3ac7eb661e108d99a7731bbc"}
    ),
    ".config/shell/env.fish": frozenset(
        {"785828c816ec8b863c94cbc4e7a64ab073598d347ce289e8bb654cc8cf898bdc"}
    ),
    ".config/environment.d/shell/functions.sh": frozenset(
        {"29301a677d2df2a08acf6a4fb39bace6ecead13e52a5b536ef3a01564115a21d"}
    ),
    ".config/environment.d/shell/functions.fish": frozenset(
        {"718d625c20c48a99172dc41e4ca6400cd01bdbd0c6bbd6c6f313a3cbf7c22204"}
    ),
    ".config/environment.d/shell/aliases.toml": frozenset(
        {"759d8342e81185aea53ffe1b5da03f2f939a67ddc522a173ccec2369c0826f7a"}
    ),
    ".config/environment.d/shell/completions.toml": frozenset(
        {"ad11496573d094bb3b3ed1a3b54aa6adc315a7599b05219a592cd2ac41d66bbe"}
    ),
    ".config/environment.d/secrets/profiles.toml": frozenset(
        {"0a2701c5b9f348dc7dbcbd02261536dc9e66c4f5734cec2d3b3f940c295c84dc"}
    ),
    ".config/direnv/direnvrc": frozenset(
        {"4658058557bb767fe5f0c4f1918fec5c4c8e23070ab4fe11af01048716110bb8"}
    ),
    ".local/bin/environment-d-loader": frozenset(
        {
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "bdacec44ad1ca446da27f2cc535cebeb5802d81b4325c50738ad1250f2780300",
            "99050a07a3db6f99026987e97b7b04f5e955f491878c6882df0e0fa936613f00",
            "c2404c2f2c1027975c60ea0898324f64468924dcf3660107fa94ee07b55b4911",
        }
    ),
    ".local/bin/env-keyring": frozenset(
        {
            "31a7dafbfceaebaf125e7706ae3b50241565cf41117b88fa1094786883126081",
            "001e1c1e462763491d513b92bb949a4056d5ed5265636d38644d7351c4bbc3c1",
            "bf71add878cb2dc55729910e0d98978c69eae8ace9f360ba20d3d84d9b126196",
        }
    ),
}

_AGENT_COMMENT = (
    b"# Non-sensitive agent configuration only. Credentials belong in GNOME Keyring.\n"
)
_AGENT_COMMENT_REPLACEMENT = (
    b"# Non-sensitive agent configuration only. Required credentials come from "
    b"the invoking process environment.\n"
)
_PROJECT_COMMENT = (
    b"# Non-sensitive project environment. Secrets are injected by env-keyring.\n"
)
_PROJECT_COMMENT_REPLACEMENT = (
    b"# Non-sensitive project environment. Required credentials come from the "
    b"invoking process environment.\n"
)
_BASH_SOURCE = (
    b'[[ -f "$HOME/.config/shell/env.sh" ]] && source "$HOME/.config/shell/env.sh"\n'
)

_TRANSFORMS: dict[str, tuple[tuple[bytes, bytes], ...]] = {
    ".profile": (
        (
            (
                b"# POSIX login-shell adapter for the canonical environment.d "
                b"modules.\n"
                b'if [ -x "$HOME/.local/bin/environment-d-loader" ]; then\n'
                b'    eval "$("$HOME/.local/bin/environment-d-loader" bootstrap '
                b'--shell bash)"\nfi\n'
            ),
            b"",
        ),
    ),
    ".bashrc": ((_BASH_SOURCE + b"\n", b""), (_BASH_SOURCE, b"")),
    ".zshenv": (
        (
            (
                b"# Shared environment SSOT for login, interactive, and "
                b"non-interactive Zsh.\n"
                b'[[ -f "$HOME/.config/shell/env.zsh" ]] && source '
                b'"$HOME/.config/shell/env.zsh"\n'
            ),
            b"",
        ),
    ),
    ".config/fish/conf.d/00-environment-d.fish": (
        (
            (
                b"# Fish loads conf.d before config.fish. Bootstrap here so "
                b"inherited secrets are\n# removed before any later hook resolves a "
                b'mise shim.\nsource "$HOME/.config/shell/env.fish"\n'
            ),
            b"",
        ),
    ),
    ".config/environment.d/40-agents.conf": (
        (_AGENT_COMMENT, _AGENT_COMMENT_REPLACEMENT),
        (b"BASH_ENV=${HOME}/.config/shell/env.sh\n", b""),
    ),
    ".config/environment.d/projects/agent-tools.envrc": (
        (_PROJECT_COMMENT, _PROJECT_COMMENT_REPLACEMENT),
    ),
    ".config/environment.d/projects/automation.envrc": (
        (_PROJECT_COMMENT, _PROJECT_COMMENT_REPLACEMENT),
    ),
    ".config/environment.d/projects/enterprise-data.envrc": (
        (_PROJECT_COMMENT, _PROJECT_COMMENT_REPLACEMENT),
    ),
}


@dataclass(frozen=True)
class _Snapshot:
    data: bytes
    mode: int
    device: int
    inode: int
    modified_ns: int


@dataclass(frozen=True)
class _Change:
    path: Path
    snapshot: _Snapshot
    desired: bytes | None


@dataclass
class _StagedRetirement:
    changes: tuple[_Change, ...]
    stage: Path
    candidates: tuple[Path | None, ...]
    backups: tuple[Path, ...]


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _snapshot(path: Path) -> _Snapshot:
    details = path.lstat()
    if not stat.S_ISREG(details.st_mode):
        raise RuntimeError(f"retired environment target is not a regular file: {path}")
    return _Snapshot(
        path.read_bytes(),
        stat.S_IMODE(details.st_mode),
        details.st_dev,
        details.st_ino,
        details.st_mtime_ns,
    )


def _current(path: Path) -> _Snapshot | None:
    if not path.exists() and not path.is_symlink():
        return None
    return _snapshot(path)


class RetiredEnvironmentProjection:
    """Converge exact obsolete environment artifacts to absence."""

    def __init__(self, home: Path) -> None:
        if not home.is_absolute() or home.is_symlink() or not home.is_dir():
            raise ValueError(f"environment retirement home must be physical: {home}")
        if home.resolve(strict=True) != home:
            raise ValueError(f"environment retirement home must be canonical: {home}")
        self.home = home

    def _path(self, relative: str) -> Path:
        path = self.home / relative
        cursor = path.parent
        while cursor != self.home:
            if cursor.exists() and (cursor.is_symlink() or not cursor.is_dir()):
                raise RuntimeError(
                    f"retired environment parent must be physical: {cursor}"
                )
            cursor = cursor.parent
        return path

    @staticmethod
    def _transform(data: bytes, replacements: tuple[tuple[bytes, bytes], ...]) -> bytes:
        result = data
        for source, destination in replacements:
            occurrences = result.count(source)
            if occurrences > 1:
                raise RuntimeError("ambiguous retired environment content")
            if occurrences == 1:
                result = result.replace(source, destination, 1)
        return result

    def _changes(self) -> tuple[_Change, ...]:
        changes: list[_Change] = []
        home_device = self.home.stat().st_dev
        for relative, accepted in _FULL_REMOVALS.items():
            path = self._path(relative)
            snapshot = _current(path)
            if snapshot is None:
                continue
            if snapshot.device != home_device:
                raise RuntimeError(
                    f"retired environment target crosses filesystems: {path}"
                )
            if _digest(snapshot.data) not in accepted:
                raise RuntimeError(f"unrecognized retired environment artifact: {path}")
            changes.append(_Change(path, snapshot, None))
        for relative, replacements in _TRANSFORMS.items():
            path = self._path(relative)
            snapshot = _current(path)
            if snapshot is None:
                continue
            if snapshot.device != home_device:
                raise RuntimeError(
                    f"retired environment target crosses filesystems: {path}"
                )
            desired = self._transform(snapshot.data, replacements)
            if desired == snapshot.data:
                continue
            changes.append(_Change(path, snapshot, desired or None))
        return tuple(changes)

    def check(self) -> None:
        changes = self._changes()
        if changes:
            raise RuntimeError(f"retired environment residue: {changes[0].path}")

    @staticmethod
    def _prepare(changes: tuple[_Change, ...], home: Path) -> PreparedPublication:
        stage = Path(tempfile.mkdtemp(prefix=".agents-retired-environment.", dir=home))
        stage.chmod(0o700)

        def build() -> PreparedPublication:
            candidates_root = stage / "candidates"
            backups_root = stage / "backups"
            candidates_root.mkdir(mode=0o700)
            backups_root.mkdir(mode=0o700)
            candidates: list[Path | None] = []
            backups: list[Path] = []
            for index, change in enumerate(changes):
                candidate: Path | None = None
                if change.desired is not None:
                    candidate = candidates_root / str(index)
                    candidate.write_bytes(change.desired)
                    candidate.chmod(change.snapshot.mode)
                candidates.append(candidate)
                backups.append(backups_root / str(index))
            staged = _StagedRetirement(
                changes,
                stage,
                tuple(candidates),
                tuple(backups),
            )
            return PreparedPublication(
                partial(RetiredEnvironmentProjection._publish, staged),
                partial(RetiredEnvironmentProjection._rollback, staged),
                partial(RetiredEnvironmentProjection._cleanup, staged),
            )

        return run_with_cleanup(build, lambda: remove_physical(stage))

    @staticmethod
    def _publish(staged: _StagedRetirement) -> None:
        for change in staged.changes:
            if _current(change.path) != change.snapshot:
                raise RuntimeError(
                    f"retired environment changed after preflight: {change.path}"
                )
        for change, candidate, backup in zip(
            staged.changes, staged.candidates, staged.backups, strict=True
        ):
            change.path.replace(backup)
            if candidate is not None:
                candidate.replace(change.path)

    @staticmethod
    def _rollback(staged: _StagedRetirement) -> None:
        for change, backup in reversed(
            tuple(zip(staged.changes, staged.backups, strict=True))
        ):
            if not backup.exists():
                continue
            if change.path.exists() or change.path.is_symlink():
                remove_physical(change.path)
            backup.replace(change.path)

    @staticmethod
    def _cleanup(staged: _StagedRetirement) -> None:
        if staged.stage.exists():
            remove_physical(staged.stage)

    def publications(self) -> tuple[Publication, ...]:
        changes = self._changes()
        if not changes:
            return ()
        return (Publication(partial(self._prepare, changes, self.home)),)


__all__ = ("RetiredEnvironmentProjection",)
