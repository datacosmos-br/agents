"""Typed, fail-closed validation for optional skill UI metadata."""

from __future__ import annotations

import re
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, cast

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
_BRAND_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
_YAML_STRING_TAG = "tag:yaml.org,2002:str"


@dataclass(frozen=True)
class SkillMetadataFinding:
    """One deterministic defect in a skill's ``agents/openai.yaml``."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class InterfaceMetadata:
    """Documented user-facing skill metadata."""

    display_name: str | None
    short_description: str | None
    icon_small: str | None
    icon_large: str | None
    brand_color: str | None
    default_prompt: str | None


@dataclass(frozen=True)
class ToolDependency:
    """One documented MCP dependency."""

    kind: str
    value: str
    description: str | None
    transport: str | None
    url: str | None


@dataclass(frozen=True)
class SkillMetadata:
    """Typed representation of one valid optional metadata document."""

    interface: InterfaceMetadata | None
    tools: tuple[ToolDependency, ...]
    allow_implicit_invocation: bool | None


class _Validator:
    def __init__(self, root: Path, path: Path, skill_name: str) -> None:
        self.root = root
        self.path = path
        self.skill_name = skill_name
        self.findings: list[SkillMetadataFinding] = []

    @property
    def relative_path(self) -> str:
        try:
            return self.path.relative_to(self.root).as_posix()
        except ValueError:
            return self.path.as_posix()

    def add(self, code: str, message: str) -> None:
        self.findings.append(SkillMetadataFinding(self.relative_path, code, message))

    def mapping(
        self,
        value: object,
        field: str,
        *,
        code: str = "section-type",
    ) -> dict[str, object] | None:
        if not isinstance(value, dict):
            self.add(code, f"{field} must be a mapping")
            return None
        raw = cast(dict[object, object], value)
        if not all(isinstance(key, str) for key in raw):
            self.add("field-type", f"{field} keys must be strings")
            return None
        return cast(dict[str, object], raw)

    def unknown_fields(
        self,
        value: dict[str, object],
        allowed: frozenset[str],
        field: str,
        *,
        legacy: frozenset[str] = frozenset(),
    ) -> None:
        for key in sorted(set(value) - allowed):
            if key in legacy:
                self.add("legacy-field", f"{field}.{key} is a legacy field")
            else:
                self.add("unknown-field", f"{field}.{key} is not documented")

    def string(
        self,
        value: dict[str, object],
        key: str,
        field: str,
        *,
        required: bool = False,
    ) -> str | None:
        if key not in value:
            if required:
                self.add("missing-field", f"{field}.{key} is required")
            return None
        raw = value[key]
        if not isinstance(raw, str):
            self.add("field-type", f"{field}.{key} must be a string")
            return None
        if not raw.strip():
            self.add("field-empty", f"{field}.{key} must not be empty")
            return None
        return raw

    def icon(self, value: str | None, field: str) -> None:
        if value is None:
            return
        portable = PurePosixPath(value)
        if (
            portable.is_absolute()
            or not value.startswith("./assets/")
            or ".." in portable.parts
            or "\\" in value
        ):
            self.add(
                "icon-path",
                f"interface.{field} must be a contained ./assets/ path",
            )
            return
        asset = self.path.parents[1] / value.removeprefix("./")
        assets = self.path.parents[1] / "assets"
        if assets.is_symlink() or asset.is_symlink():
            self.add("icon-symlink", f"interface.{field} must not be a symlink")
            return
        try:
            metadata = asset.lstat()
        except FileNotFoundError:
            self.add("icon-missing", f"interface.{field} asset does not exist")
            return
        except OSError as error:
            self.add("icon-io", f"interface.{field} cannot be inspected: {error}")
            return
        if not stat.S_ISREG(metadata.st_mode):
            self.add("icon-special", f"interface.{field} must be a regular file")

    def interface(self, value: object) -> InterfaceMetadata | None:
        section = self.mapping(value, "interface")
        if section is None:
            return None
        self.unknown_fields(section, _INTERFACE_FIELDS, "interface")
        display_name = self.string(section, "display_name", "interface")
        short_description = self.string(section, "short_description", "interface")
        icon_small = self.string(section, "icon_small", "interface")
        icon_large = self.string(section, "icon_large", "interface")
        brand_color = self.string(section, "brand_color", "interface")
        default_prompt = self.string(section, "default_prompt", "interface")
        if short_description is not None and not (25 <= len(short_description) <= 64):
            self.add(
                "short-description-length",
                "interface.short_description must contain 25-64 characters",
            )
        if brand_color is not None and _BRAND_COLOR.fullmatch(brand_color) is None:
            self.add(
                "brand-color",
                "interface.brand_color must be a six-digit hexadecimal color",
            )
        if default_prompt is not None:
            skill_reference = re.compile(
                rf"(?<![A-Za-z0-9_-])\${re.escape(self.skill_name)}"
                r"(?![A-Za-z0-9_-])"
            )
            if skill_reference.search(default_prompt) is None:
                self.add(
                    "default-prompt-skill",
                    f"interface.default_prompt must mention ${self.skill_name} exactly",
                )
        self.icon(icon_small, "icon_small")
        self.icon(icon_large, "icon_large")
        return InterfaceMetadata(
            display_name=display_name,
            short_description=short_description,
            icon_small=icon_small,
            icon_large=icon_large,
            brand_color=brand_color,
            default_prompt=default_prompt,
        )

    def dependencies(self, value: object) -> tuple[ToolDependency, ...]:
        section = self.mapping(value, "dependencies")
        if section is None:
            return ()
        self.unknown_fields(section, _DEPENDENCIES_FIELDS, "dependencies")
        if "tools" not in section:
            return ()
        raw_tools = section["tools"]
        if not isinstance(raw_tools, list):
            self.add("field-type", "dependencies.tools must be a list")
            return ()
        tools: list[ToolDependency] = []
        for index, raw_tool in enumerate(cast(list[object], raw_tools)):
            field = f"dependencies.tools[{index}]"
            tool = self.mapping(raw_tool, field, code="field-type")
            if tool is None:
                continue
            self.unknown_fields(tool, _TOOL_FIELDS, field)
            kind = self.string(tool, "type", field, required=True)
            dependency = self.string(tool, "value", field, required=True)
            description = self.string(tool, "description", field)
            transport = self.string(tool, "transport", field)
            url = self.string(tool, "url", field)
            if kind is not None and kind != "mcp":
                self.add(
                    "dependency-type",
                    f"{field}.type supports only the documented mcp value",
                )
            if kind == "mcp" and dependency is not None:
                tools.append(
                    ToolDependency(
                        kind=kind,
                        value=dependency,
                        description=description,
                        transport=transport,
                        url=url,
                    )
                )
        return tuple(tools)

    def policy(self, value: object) -> bool | None:
        section = self.mapping(value, "policy")
        if section is None:
            return None
        self.unknown_fields(section, _POLICY_FIELDS, "policy")
        if "allow_implicit_invocation" not in section:
            return None
        invocation = section["allow_implicit_invocation"]
        if not isinstance(invocation, bool):
            self.add(
                "field-type",
                "policy.allow_implicit_invocation must be a boolean",
            )
            return None
        return invocation

    def document(self, payload: dict[str, object]) -> SkillMetadata:
        self.unknown_fields(
            payload,
            _TOP_LEVEL_FIELDS,
            "document",
            legacy=_LEGACY_TOP_LEVEL_FIELDS,
        )
        interface = (
            self.interface(payload["interface"]) if "interface" in payload else None
        )
        tools = (
            self.dependencies(payload["dependencies"])
            if "dependencies" in payload
            else ()
        )
        invocation = self.policy(payload["policy"]) if "policy" in payload else None
        return SkillMetadata(interface, tools, invocation)


def _node_structure_findings(validator: _Validator, node: Node) -> bool:
    """Validate YAML key uniqueness and the documented quoting contract."""

    duplicate = False

    def visit(current: Node, field: str) -> None:
        nonlocal duplicate
        if isinstance(current, MappingNode):
            seen: set[tuple[str, str]] = set()
            for key_node, value_node in current.value:
                key_name = (
                    key_node.value
                    if isinstance(key_node, ScalarNode)
                    else "<non-scalar>"
                )
                identity = (key_node.tag, key_name)
                if identity in seen:
                    duplicate = True
                    validator.add("duplicate-key", f"{field}.{key_name} is duplicated")
                seen.add(identity)
                if isinstance(key_node, ScalarNode) and key_node.style is not None:
                    validator.add(
                        "quoted-key", f"{field}.{key_name} key must be unquoted"
                    )
                visit(value_node, f"{field}.{key_name}")
            return
        if isinstance(current, SequenceNode):
            for index, child in enumerate(current.value):
                visit(child, f"{field}[{index}]")
            return
        if (
            isinstance(current, ScalarNode)
            and current.tag == _YAML_STRING_TAG
            and current.style not in {"'", '"'}
        ):
            validator.add("unquoted-string", f"{field} string must be quoted")

    visit(node, "document")
    return duplicate


def _validate_path(
    root: Path, path: Path, skill_name: str
) -> list[SkillMetadataFinding]:
    validator = _Validator(root, path, skill_name)
    if path.parent.is_symlink() or path.parents[1].is_symlink() or path.is_symlink():
        validator.add("metadata-symlink", "metadata path must not contain a symlink")
        return validator.findings
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return []
    except OSError as error:
        validator.add("metadata-io", f"metadata cannot be inspected: {error}")
        return validator.findings
    if not stat.S_ISREG(metadata.st_mode):
        validator.add("metadata-special", "metadata must be a regular file")
        return validator.findings
    try:
        text = path.read_text(encoding="utf-8")
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        payload: Any = yaml.safe_load(text)
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        validator.add("yaml-invalid", f"metadata YAML cannot be loaded: {error}")
        return validator.findings
    if not isinstance(node, MappingNode) or not isinstance(payload, dict):
        validator.add("document-type", "metadata document must be a mapping")
        return validator.findings
    if _node_structure_findings(validator, node):
        return validator.findings
    raw_payload = cast(dict[object, object], payload)
    if not all(isinstance(key, str) for key in raw_payload):
        validator.add("field-type", "document keys must be strings")
        return validator.findings
    validator.document(cast(dict[str, object], raw_payload))
    return validator.findings


def validate(root: Path) -> tuple[SkillMetadataFinding, ...]:
    """Validate optional OpenAI metadata for every recursively discovered skill."""

    canonical_root = root.absolute()
    skills_root = canonical_root / "skills"
    if not skills_root.is_dir():
        return ()
    findings: list[SkillMetadataFinding] = []
    for skill_file in sorted(skills_root.rglob("SKILL.md")):
        skill_directory = skill_file.parent
        metadata_path = skill_directory / "agents" / "openai.yaml"
        findings.extend(
            _validate_path(canonical_root, metadata_path, skill_directory.name)
        )
    return tuple(
        sorted(
            findings, key=lambda finding: (finding.path, finding.code, finding.message)
        )
    )
