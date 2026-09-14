"""Declared resource policy for the canonical skill catalog."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal

from .frontmatter import cast_mapping, require_exact_fields


@dataclass(frozen=True)
class ResourceOptions:
    """Policy, never a guess from a filename or decoding failure."""

    format: Literal["utf-8", "binary"]
    executable: bool

    @classmethod
    def parse(cls, value: object, label: str) -> ResourceOptions:
        document = cast_mapping(value, label)
        require_exact_fields(document, frozenset({"format", "executable"}), label)
        encoding = document["format"]
        executable = document["executable"]
        if encoding not in {"utf-8", "binary"}:
            raise ValueError(f"{label}.format must be utf-8 or binary")
        if not isinstance(executable, bool):
            raise TypeError(f"{label}.executable must be boolean")
        if encoding == "utf-8":
            return cls("utf-8", executable)
        return cls("binary", executable)


@dataclass(frozen=True)
class SkillResource:
    """One discovered physical resource with its declared publication contract."""

    path: Path
    format: Literal["utf-8", "binary"]
    executable: bool
    mode: int
    sha256: str


@dataclass(frozen=True)
class ResourcePolicy:
    """The resource section of config/skills.json, parsed exactly once."""

    default: ResourceOptions
    overrides: dict[str, ResourceOptions]
    file_mode: int
    executable_mode: int

    @classmethod
    def parse(cls, value: object) -> ResourcePolicy:
        document = cast_mapping(value, "resources")
        require_exact_fields(
            document,
            frozenset({"default", "overrides", "file_mode", "executable_mode"}),
            "resources",
        )
        file_mode = document["file_mode"]
        executable_mode = document["executable_mode"]
        for label, mode in (
            ("file_mode", file_mode),
            ("executable_mode", executable_mode),
        ):
            if (
                type(mode) is not int
                or not 0 <= mode <= 0o777
                or mode & 0o022
                or not mode & 0o200
            ):
                raise ValueError(
                    f"resources.{label} must be an owner-writable safe mode"
                )
        if not isinstance(file_mode, int) or not isinstance(executable_mode, int):
            raise TypeError("resource modes must be integers")
        if file_mode & 0o111 or not executable_mode & 0o100:
            raise ValueError("resource modes must distinguish executable files")
        overrides: dict[str, ResourceOptions] = {}
        for identity, options in cast_mapping(
            document["overrides"], "resources.overrides"
        ).items():
            path = PurePosixPath(identity)
            if (
                path.is_absolute()
                or ".." in path.parts
                or "\\" in identity
                or "\x00" in identity
                or path.as_posix() != identity
                or identity == "."
                or path.name == "SKILL.md"
            ):
                raise ValueError(f"invalid resource override identity: {identity}")
            overrides[identity] = ResourceOptions.parse(
                options, f"resources.overrides.{identity}"
            )
        return cls(
            ResourceOptions.parse(document["default"], "resources.default"),
            overrides,
            file_mode,
            executable_mode,
        )

    def resource(self, root: Path, path: Path) -> SkillResource:
        """Bind one physical catalog member to configured policy and exact bytes."""
        identity = path.relative_to(root / "skills").as_posix()
        options = self.overrides.get(identity, self.default)
        content = path.read_bytes()
        if options.format == "utf-8":
            content.decode("utf-8")
        return SkillResource(
            path,
            options.format,
            options.executable,
            self.executable_mode if options.executable else self.file_mode,
            hashlib.sha256(content).hexdigest(),
        )

    def validate_inventory(
        self, root: Path, resources: tuple[SkillResource, ...]
    ) -> None:
        """Reject stale policy entries instead of silently retaining dead overrides."""
        known = {
            resource.path.relative_to(root / "skills").as_posix()
            for resource in resources
        }
        unknown = self.overrides.keys() - known
        if unknown:
            raise ValueError(
                f"resource overrides have no catalog owner: {sorted(unknown)}"
            )
