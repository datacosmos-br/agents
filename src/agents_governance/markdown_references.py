"""Parse and resolve portable local Markdown references."""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

_FENCED_CODE = re.compile(r"^```.*?^```\s*$", re.MULTILINE | re.DOTALL)
_LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")


def _link_target(raw: str) -> str:
    candidate = raw.strip()
    if candidate.startswith("<"):
        closing = candidate.find(">", 1)
        return candidate[1:closing] if closing > 0 else candidate
    return candidate.split(maxsplit=1)[0] if candidate else candidate


def local_reference_targets(source: Path, markdown: str) -> tuple[str, ...]:
    """Return decoded local targets and reject non-portable URI forms."""

    targets: list[str] = []
    body = _FENCED_CODE.sub("", markdown)
    for match in _LINK.finditer(body):
        target = _link_target(match.group(1))
        if not target or target.startswith("#"):
            continue
        if _SCHEME.match(target):
            if urlsplit(target).scheme.lower() == "file":
                raise ValueError(f"{source}: file URI references are forbidden")
            continue
        decoded = unquote(target).split("#", 1)[0].split("?", 1)[0]
        if not decoded:
            continue
        if decoded.startswith(("/", "//", "~")) or any(
            marker in decoded for marker in ("\\", "$", "\x00")
        ):
            raise ValueError(
                f"{source}: reference must be portable and relative: {target!r}"
            )
        targets.append(decoded)
    return tuple(targets)


def resolve_physical_reference(boundary: Path, source: Path, target: str) -> Path:
    """Resolve one target inside its physical owner boundary."""

    owner = boundary.resolve(strict=True)
    local = Path(os.path.normpath(source.parent.joinpath(*PurePosixPath(target).parts)))
    lexical_parts = local.relative_to(owner).parts
    cursor = owner
    for part in lexical_parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"{source}: reference target is symlinked: {target!r}")
    canonical = local.resolve(strict=True)
    canonical.relative_to(owner)
    if not stat.S_ISREG(canonical.lstat().st_mode) and not stat.S_ISDIR(
        canonical.lstat().st_mode
    ):
        raise ValueError(f"{source}: reference target must be physical: {target!r}")
    return canonical


__all__ = ("local_reference_targets", "resolve_physical_reference")
