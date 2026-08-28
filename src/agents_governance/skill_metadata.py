"""Strict validation for optional provider UI metadata."""

from __future__ import annotations

import re
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import cast

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

_TOP_LEVEL_FIELDS = frozenset({"dependencies", "interface", "policy"})
_LEGACY_TOP_LEVEL_FIELDS = frozenset({"description", "model", "name", "tools"})
_INTERFACE_FIELDS = frozenset(
    {
        "brand_color",
        "default_prompt",
        "display_name",
        "icon_large",
        "icon_small",
        "short_description",
    }
)
_DEPENDENCIES_FIELDS = frozenset({"tools"})
_TOOL_FIELDS = frozenset({"description", "transport", "type", "url", "value"})
_POLICY_FIELDS = frozenset({"allow_implicit_invocation"})
_BRAND_COLOR = re.compile(r"#[0-9A-Fa-f]{6}\Z")
_YAML_STRING_TAG = "tag:yaml.org,2002:str"


@dataclass(frozen=True)
class InterfaceMetadata:
    display_name: str | None
    short_description: str | None
    icon_small: str | None
    icon_large: str | None
    brand_color: str | None
    default_prompt: str | None


@dataclass(frozen=True)
class ToolDependency:
    kind: str
    value: str
    description: str | None
    transport: str | None
    url: str | None


@dataclass(frozen=True)
class SkillMetadata:
    path: Path
    interface: InterfaceMetadata | None
    tools: tuple[ToolDependency, ...]
    allow_implicit_invocation: bool | None


def _mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"{field} must be a mapping")
    raw = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in raw):
        raise TypeError(f"{field} keys must be strings")
    return cast(dict[str, object], raw)


def _known_fields(
    value: dict[str, object],
    allowed: frozenset[str],
    field: str,
    *,
    legacy: frozenset[str] = frozenset(),
) -> None:
    unknown = tuple(sorted(frozenset(value) - allowed))
    if not unknown:
        return
    key = unknown[0]
    if key in legacy:
        raise ValueError(f"{field}.{key} is a legacy field")
    raise ValueError(f"{field}.{key} is not documented")


def _string(
    value: dict[str, object], key: str, field: str, *, required: bool = False
) -> str | None:
    if key not in value:
        if required:
            raise ValueError(f"{field}.{key} is required")
        return None
    raw = value[key]
    if not isinstance(raw, str):
        raise TypeError(f"{field}.{key} must be a string")
    if not raw.strip():
        raise ValueError(f"{field}.{key} must not be empty")
    return raw


def _physical_asset(metadata_path: Path, value: str, field: str) -> None:
    portable = PurePosixPath(value)
    if (
        portable.is_absolute()
        or not value.startswith("./assets/")
        or ".." in portable.parts
        or "\\" in value
    ):
        raise ValueError(f"interface.{field} must be a contained ./assets/ path")
    skill = metadata_path.parents[1]
    assets = skill / "assets"
    asset = skill.joinpath(*portable.parts)
    cursor = skill
    for part in portable.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"interface.{field} must not traverse a symlink")
    asset.resolve(strict=True).relative_to(assets.resolve(strict=True))
    if not stat.S_ISREG(asset.lstat().st_mode):
        raise ValueError(f"interface.{field} must be a regular file")


def _interface(
    metadata_path: Path, skill_name: str, value: object
) -> InterfaceMetadata:
    section = _mapping(value, "interface")
    _known_fields(section, _INTERFACE_FIELDS, "interface")
    display_name = _string(section, "display_name", "interface")
    short_description = _string(section, "short_description", "interface")
    icon_small = _string(section, "icon_small", "interface")
    icon_large = _string(section, "icon_large", "interface")
    brand_color = _string(section, "brand_color", "interface")
    default_prompt = _string(section, "default_prompt", "interface")
    if short_description is not None and not 25 <= len(short_description) <= 64:
        raise ValueError("interface.short_description must contain 25-64 characters")
    if brand_color is not None and _BRAND_COLOR.fullmatch(brand_color) is None:
        raise ValueError("interface.brand_color must be a six-digit hexadecimal color")
    if default_prompt is not None:
        reference = re.compile(
            rf"(?<![A-Za-z0-9_-])\${re.escape(skill_name)}(?![A-Za-z0-9_-])"
        )
        if reference.search(default_prompt) is None:
            raise ValueError(
                f"interface.default_prompt must mention ${skill_name} exactly"
            )
    if icon_small is not None:
        _physical_asset(metadata_path, icon_small, "icon_small")
    if icon_large is not None:
        _physical_asset(metadata_path, icon_large, "icon_large")
    return InterfaceMetadata(
        display_name,
        short_description,
        icon_small,
        icon_large,
        brand_color,
        default_prompt,
    )


def _dependencies(value: object) -> tuple[ToolDependency, ...]:
    section = _mapping(value, "dependencies")
    _known_fields(section, _DEPENDENCIES_FIELDS, "dependencies")
    if "tools" not in section:
        return ()
    raw_tools = section["tools"]
    if not isinstance(raw_tools, list):
        raise TypeError("dependencies.tools must be a list")
    tools: list[ToolDependency] = []
    identities: set[tuple[str, str]] = set()
    for index, raw_tool in enumerate(cast(list[object], raw_tools)):
        field = f"dependencies.tools[{index}]"
        tool = _mapping(raw_tool, field)
        _known_fields(tool, _TOOL_FIELDS, field)
        kind = _string(tool, "type", field, required=True)
        dependency = _string(tool, "value", field, required=True)
        assert kind is not None
        assert dependency is not None
        if kind != "mcp":
            raise ValueError(f"{field}.type supports only the documented mcp value")
        identity = kind, dependency
        if identity in identities:
            raise ValueError(f"{field} duplicates an earlier dependency")
        identities.add(identity)
        tools.append(
            ToolDependency(
                kind,
                dependency,
                _string(tool, "description", field),
                _string(tool, "transport", field),
                _string(tool, "url", field),
            )
        )
    return tuple(tools)


def _policy(value: object) -> bool | None:
    section = _mapping(value, "policy")
    _known_fields(section, _POLICY_FIELDS, "policy")
    if "allow_implicit_invocation" not in section:
        return None
    invocation = section["allow_implicit_invocation"]
    if not isinstance(invocation, bool):
        raise TypeError("policy.allow_implicit_invocation must be a boolean")
    return invocation


def _structure(node: Node, field: str = "document") -> None:
    if isinstance(node, MappingNode):
        seen: set[tuple[str, str]] = set()
        for key_node, value_node in node.value:
            if not isinstance(key_node, ScalarNode):
                raise TypeError(f"{field} key must be a scalar")
            identity = key_node.tag, key_node.value
            if identity in seen:
                raise ValueError(f"{field}.{key_node.value} is duplicated")
            seen.add(identity)
            if key_node.style is not None:
                raise ValueError(f"{field}.{key_node.value} key must be unquoted")
            _structure(value_node, f"{field}.{key_node.value}")
        return
    if isinstance(node, SequenceNode):
        for index, child in enumerate(node.value):
            _structure(child, f"{field}[{index}]")
        return
    if (
        isinstance(node, ScalarNode)
        and node.tag == _YAML_STRING_TAG
        and node.style not in {"'", '"'}
    ):
        raise ValueError(f"{field} string must be quoted")


def _load(root: Path, path: Path, skill_name: str) -> SkillMetadata | None:
    if path.parent.is_symlink() or path.parents[1].is_symlink() or path.is_symlink():
        raise ValueError(f"metadata path must be physical: {path.relative_to(root)}")
    if not path.exists():
        return None
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError(f"metadata must be a regular file: {path.relative_to(root)}")
    text = path.read_text(encoding="utf-8")
    node = yaml.compose(text, Loader=yaml.SafeLoader)
    payload = yaml.safe_load(text)
    if not isinstance(node, MappingNode):
        raise TypeError(
            f"metadata document must be a mapping: {path.relative_to(root)}"
        )
    _structure(node)
    document = _mapping(payload, "document")
    _known_fields(
        document,
        _TOP_LEVEL_FIELDS,
        "document",
        legacy=_LEGACY_TOP_LEVEL_FIELDS,
    )
    interface = (
        _interface(path, skill_name, document["interface"])
        if "interface" in document
        else None
    )
    tools = (
        _dependencies(document["dependencies"]) if "dependencies" in document else ()
    )
    invocation = _policy(document["policy"]) if "policy" in document else None
    return SkillMetadata(path, interface, tools, invocation)


def validate(root: Path) -> tuple[SkillMetadata, ...]:
    """Return all optional metadata documents or raise on the first defect."""

    canonical_root = root.resolve(strict=True)
    skills_root = canonical_root / "skills"
    if skills_root.is_symlink() or not skills_root.is_dir():
        raise ValueError(f"skills root must be a physical directory: {skills_root}")
    documents: list[SkillMetadata] = []
    for skill_file in sorted(skills_root.rglob("SKILL.md")):
        if skill_file.is_symlink() or not stat.S_ISREG(skill_file.lstat().st_mode):
            raise ValueError(f"skill source must be a physical file: {skill_file}")
        metadata = _load(
            canonical_root,
            skill_file.parent / "agents" / "openai.yaml",
            skill_file.parent.name,
        )
        if metadata is not None:
            documents.append(metadata)
    return tuple(documents)


__all__ = (
    "InterfaceMetadata",
    "SkillMetadata",
    "ToolDependency",
    "validate",
)
