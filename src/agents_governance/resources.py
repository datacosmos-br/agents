"""Locate canonical data files bundled with the installed runtime.

For a release wheel, all canonical data (config/, skills/, rules/, etc.) is
bundled under ``_data`` inside the package.  For an editable / development
install the data files remain at the source checkout root and are resolved via
PEP 610 metadata (see :mod:`provenance`).
"""

from __future__ import annotations

import hashlib
import stat
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from .capsule import render_capsule
from .frontmatter import cast_mapping
from .provenance import source_root

if TYPE_CHECKING:
    from .bundle import GovernanceBundle


@dataclass(frozen=True)
class CatalogResource:
    """One neutral central-catalog publication, not a source checkout pointer."""

    relative_path: str
    content: bytes
    mode: int
    sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.relative_path, str):
            raise TypeError("catalog resource identity must be text")
        _relative_path(self.relative_path)
        if not isinstance(self.content, bytes):
            raise TypeError("catalog resource content must be immutable bytes")
        permission_bits = (
            stat.S_IRWXU
            | stat.S_IRWXG
            | stat.S_IRWXO
            | stat.S_ISUID
            | stat.S_ISGID
            | stat.S_ISVTX
        )
        if type(self.mode) is not int or self.mode & ~permission_bits:
            raise ValueError("catalog resource mode must contain permission bits only")
        if self.sha256 != hashlib.sha256(self.content).hexdigest():
            raise ValueError("catalog resource digest must match its immutable bytes")


def resource_root() -> Path:
    """Return the filesystem path to canonical data files.

    A release wheel bundles data under ``_data/`` inside the package directory;
    that path is returned directly.  An editable / development install has no
    ``_data`` directory, so the source checkout root is resolved via PEP 610
    ``direct_url.json`` instead.
    """

    package_dir = Path(__file__).resolve().parent
    bundled = package_dir / "_data"
    if bundled.is_dir():
        return bundled
    return source_root()


def _relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or ".." in path.parts
        or value == "."
        or "\\" in value
        or "\x00" in value
    ):
        raise ValueError(f"catalog path must be portable and relative: {value!r}")
    return path


def _physical_path(root: Path, relative: PurePosixPath) -> Path:
    cursor = root
    for part in relative.parts:
        cursor /= part
        mode = cursor.lstat().st_mode
        if not stat.S_ISDIR(mode) and not stat.S_ISREG(mode):
            raise ValueError(f"catalog path must be physical: {cursor}")
    return cursor


def _catalog_files(root: Path) -> tuple[Path, ...]:
    """Use the existing artifact enrollment, never scan the checkout root."""
    manifest = _physical_path(root, PurePosixPath("pyproject.toml"))
    document = tomllib.loads(manifest.read_text(encoding="utf-8"))
    enrollment = cast_mapping(
        document["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"],
        "wheel force-include",
    )
    files: set[Path] = set()

    def collect(path: Path) -> None:
        _relative_path(path.relative_to(root).as_posix())
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            if path in files:
                raise ValueError(f"overlapping catalog enrollment: {path}")
            files.add(path)
        elif stat.S_ISDIR(mode):
            for child in sorted(path.iterdir()):
                collect(child)
        else:
            raise ValueError(f"unsupported catalog resource type: {path}")

    for source, destination in sorted(enrollment.items()):
        relative = _relative_path(source)
        expected = f"agents_governance/_data/{relative.as_posix()}"
        if destination != expected:
            raise ValueError(f"catalog enrollment must preserve identity: {source}")
        path = _physical_path(root, relative)
        # These packaged inputs serve SDK loading, not the central catalog.
        if source not in {"config", "pyproject.toml"}:
            collect(path)
    return tuple(sorted(files, key=lambda path: path.relative_to(root).as_posix()))


def catalog_resources(bundle: GovernanceBundle) -> tuple[CatalogResource, ...]:
    """Capture the enrolled central catalog with neutral SDK-owned instructions.

    Regular hardlinks retain their distinct path identities, as in the skill
    resource owner. Symlinks and unsupported entries fail before content is read.
    No publication, filesystem writes or consumer-specific adaptation occurs.
    """
    root = bundle.root
    if root.is_symlink() or not root.is_dir() or root != root.resolve(strict=True):
        raise ValueError(f"catalog root must be a resolved physical directory: {root}")
    skill_resources = {
        resource.path: resource
        for skill in bundle.skills
        for resource in skill.resources
    }
    captured: list[CatalogResource] = []
    for path in _catalog_files(root):
        identity = path.relative_to(root).as_posix()
        mode = stat.S_IMODE(path.lstat().st_mode)
        if mode & 0o7022:
            raise ValueError(f"catalog resource mode is unsafe: {path} ({mode:#o})")
        if identity == "AGENTS.md":
            content = (bundle.law.prelude + "\n" + render_capsule(bundle).text).encode(
                "utf-8"
            )
        else:
            content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        resource = skill_resources.get(path)
        if resource is not None and (
            digest != resource.sha256 or mode != resource.mode
        ):
            raise ValueError(f"skill resource changed bytes or declared mode: {path}")
        captured.append(CatalogResource(identity, content, mode, digest))
    if skill_resources.keys() - {root / item.relative_path for item in captured}:
        raise ValueError("catalog enrollment omits validated skill resources")
    if not any(item.relative_path == "AGENTS.md" for item in captured):
        raise ValueError("catalog enrollment omits neutral AGENTS.md")
    return tuple(captured)


__all__ = ("CatalogResource", "catalog_resources", "resource_root")
