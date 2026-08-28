"""Strict registry-free discovery of canonical engineering rules."""

from __future__ import annotations

import json
import os
import re
import stat
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import unquote, urlsplit

import yaml
from yaml.nodes import MappingNode, Node, SequenceNode

_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
_FRONTMATTER_FIELDS = frozenset({"description", "globs", "metadata"})
_METADATA_FIELDS = frozenset({"aihub.tags"})
_ROUTES = frozenset({"route:both", "route:personal", "route:project"})


class RuleActivation(StrEnum):
    ALWAYS = "always"
    PATH_SCOPED = "path-scoped"


class RuleDistribution(StrEnum):
    PERSONAL = "personal"
    PROJECT = "project"
    BOTH = "both"


@dataclass(frozen=True)
class RuleSpec:
    path: Path
    identity: str
    description: str | None
    activation: RuleActivation
    globs: tuple[str, ...]
    references: tuple[str, ...]
    body: str
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_spec(self)

    @property
    def category(self) -> str:
        parts = PurePosixPath(self.identity).parts
        return parts[0] if len(parts) > 1 else "root"

    @property
    def distribution(self) -> RuleDistribution:
        routes = tuple(tag for tag in self.tags if tag.startswith("route:"))
        return (
            RuleDistribution(routes[0].removeprefix("route:"))
            if routes
            else RuleDistribution.BOTH
        )


def _identity(path: Path, rules: Path) -> str:
    return path.relative_to(rules).with_suffix("").as_posix()


def _identity_valid(identity: str) -> bool:
    return all(_SLUG.fullmatch(part) for part in PurePosixPath(identity).parts)


def _description_valid(value: str) -> bool:
    return (
        value == value.strip()
        and bool(value)
        and "\n" not in value
        and "\r" not in value
    )


def _validate_glob(value: str) -> None:
    if value != value.strip() or not value:
        raise ValueError("rule path scope must be a non-empty trimmed string")
    if (
        value.startswith(("/", "~"))
        or "\\" in value
        or "//" in value
        or "$" in value
        or "\x00" in value
        or _SCHEME.match(value)
        or any(part in {"", ".", ".."} for part in PurePosixPath(value).parts)
    ):
        raise ValueError(f"rule path scope must remain repository-local: {value!r}")


def _validate_spec(spec: RuleSpec) -> None:
    if (
        not _identity_valid(spec.identity)
        or PurePosixPath(spec.identity).name != spec.path.stem
    ):
        raise ValueError("rule identity must be path-derived from lowercase slugs")
    if spec.description is not None and not _description_valid(spec.description):
        raise ValueError("rule description must be one non-empty trimmed line")
    if not spec.body.strip():
        raise ValueError("rule body must be non-empty")
    if len(spec.globs) != len(set(spec.globs)):
        raise ValueError("rule path scopes must be unique")
    for glob in spec.globs:
        _validate_glob(glob)
    expected_activation = (
        RuleActivation.PATH_SCOPED if spec.globs else RuleActivation.ALWAYS
    )
    if spec.activation is not expected_activation:
        raise ValueError("rule activation must be derived from path scopes")
    if tuple(sorted(set(spec.references))) != spec.references:
        raise ValueError("rule references must be unique and sorted")
    if any(
        not reference.startswith("rules/") or PurePosixPath(reference).suffix != ".md"
        for reference in spec.references
    ):
        raise ValueError("rule references must target canonical Markdown rules")
    if len(spec.tags) != len(set(spec.tags)) or spec.tags != tuple(sorted(spec.tags)):
        raise ValueError("rule tags must be unique and sorted")
    routes = tuple(tag for tag in spec.tags if tag.startswith("route:"))
    if spec.tags and (len(routes) != 1 or routes[0] not in _ROUTES):
        raise ValueError("tagged rules require exactly one supported route tag")


def _duplicate_key(node: Node) -> str | None:
    if isinstance(node, MappingNode):
        seen: set[str] = set()
        for key_node, value_node in node.value:
            key = str(getattr(key_node, "value", "<non-scalar>"))
            if key in seen:
                return key
            seen.add(key)
            duplicate = _duplicate_key(value_node)
            if duplicate is not None:
                return duplicate
    elif isinstance(node, SequenceNode):
        for child in node.value:
            duplicate = _duplicate_key(child)
            if duplicate is not None:
                return duplicate
    return None


def _split_source(path: Path) -> tuple[dict[str, object] | None, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, text
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
    source = text[4:marker]
    node = yaml.compose(source, Loader=yaml.SafeLoader)
    loaded = yaml.safe_load(source)
    if not isinstance(node, MappingNode) or not isinstance(loaded, dict):
        raise TypeError(f"{path}: frontmatter must be a mapping")
    duplicate = _duplicate_key(node)
    if duplicate is not None:
        raise ValueError(f"{path}: frontmatter key is duplicated: {duplicate}")
    raw = cast(dict[object, object], loaded)
    if not all(isinstance(key, str) for key in raw):
        raise TypeError(f"{path}: frontmatter keys must be strings")
    return cast(dict[str, object], raw), text[marker + 5 :].removeprefix("\n")


def _metadata(
    path: Path, raw: dict[str, object] | None
) -> tuple[str | None, tuple[str, ...], tuple[str, ...]]:
    if raw is None:
        return None, (), ()
    unknown = frozenset(raw) - _FRONTMATTER_FIELDS
    if unknown:
        raise ValueError(f"{path}: unknown rule fields: {', '.join(sorted(unknown))}")
    description: str | None = None
    if "description" in raw:
        value = raw["description"]
        if not isinstance(value, str) or not _description_valid(value):
            raise ValueError(f"{path}: description must be one non-empty trimmed line")
        description = value
    globs: tuple[str, ...] = ()
    if "globs" in raw:
        raw_globs = raw["globs"]
        if isinstance(raw_globs, str):
            globs = (raw_globs,)
        elif isinstance(raw_globs, list) and all(
            isinstance(item, str) for item in raw_globs
        ):
            globs = tuple(cast(list[str], raw_globs))
        else:
            raise TypeError(f"{path}: globs must be a string or string array")
        if not globs:
            raise ValueError(f"{path}: globs must not be empty")
        if len(globs) != len(set(globs)):
            raise ValueError(f"{path}: globs must be unique")
        for glob in globs:
            _validate_glob(glob)
    tags: tuple[str, ...] = ()
    if "metadata" in raw:
        metadata = raw["metadata"]
        if not isinstance(metadata, dict) or frozenset(metadata) != _METADATA_FIELDS:
            raise ValueError(f"{path}: metadata must contain only aihub.tags")
        encoded = cast(dict[str, object], metadata)["aihub.tags"]
        if not isinstance(encoded, str):
            raise TypeError(f"{path}: metadata.aihub.tags must be a JSON string")
        decoded = json.loads(encoded)
        if not isinstance(decoded, list) or not all(
            isinstance(item, str) for item in decoded
        ):
            raise TypeError(f"{path}: rule tags must encode an array of strings")
        tags = tuple(cast(list[str], decoded))
        if len(tags) != len(set(tags)) or tags != tuple(sorted(tags)):
            raise ValueError(f"{path}: rule tags must be unique and sorted")
        if len(tags) != 1 or tags[0] not in _ROUTES:
            raise ValueError(f"{path}: rule requires exactly one supported route tag")
    return description, globs, tags


def _link_target(raw: str) -> str:
    candidate = raw.strip()
    if candidate.startswith("<"):
        closing = candidate.find(">", 1)
        return candidate[1:closing] if closing > 0 else candidate
    return candidate.split(maxsplit=1)[0] if candidate else candidate


def _local_reference(root: Path, rules: Path, source: Path, target: str) -> str | None:
    if not target or target.startswith("#"):
        return None
    if _SCHEME.match(target):
        if urlsplit(target).scheme.lower() == "file":
            raise ValueError(f"{source}: file URI references are forbidden")
        return None
    decoded = unquote(target).split("#", 1)[0].split("?", 1)[0]
    if not decoded:
        return None
    if decoded.startswith(("/", "//", "~")) or "\\" in decoded or "$" in decoded:
        raise ValueError(f"{source}: reference must remain inside rules/: {target!r}")
    local = Path(
        os.path.normpath(source.parent.joinpath(*PurePosixPath(decoded).parts))
    )
    lexical_parts = local.relative_to(rules).parts
    cursor = rules
    for part in lexical_parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"{source}: reference target is symlinked: {target!r}")
    canonical = local.resolve(strict=True)
    canonical.relative_to(rules)
    if canonical.suffix != ".md" or not stat.S_ISREG(canonical.lstat().st_mode):
        raise ValueError(f"{source}: reference must target a physical Markdown rule")
    return canonical.relative_to(root).as_posix()


def _references(root: Path, rules: Path, source: Path, body: str) -> tuple[str, ...]:
    references: set[str] = set()
    for match in _LINK.finditer(body):
        reference = _local_reference(root, rules, source, _link_target(match.group(1)))
        if reference is not None:
            references.add(reference)
    return tuple(sorted(references))


def _walk(directory: Path) -> tuple[Path, ...]:
    files: list[Path] = []
    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        metadata = path.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"rule source must be physical: {path}")
        if stat.S_ISDIR(metadata.st_mode):
            if _SLUG.fullmatch(path.name) is None:
                raise ValueError(f"rule directory must be a lowercase slug: {path}")
            continue
        if not stat.S_ISREG(metadata.st_mode) or path.suffix != ".md":
            raise ValueError(f"rules support only physical Markdown files: {path}")
        if any(
            _SLUG.fullmatch(part) is None for part in relative.with_suffix("").parts
        ):
            raise ValueError(f"rule identity must contain lowercase slugs: {path}")
        files.append(path)
    if not files:
        raise ValueError(f"rule inventory is empty: {directory}")
    return tuple(files)


def audit_rule_specs(root: Path) -> tuple[RuleSpec, ...]:
    """Return every valid rule or raise on the first source defect."""

    repository = root.resolve(strict=True)
    rules = repository / "rules"
    if rules.is_symlink() or not rules.is_dir():
        raise ValueError(f"rules root must be a physical directory: {rules}")
    specs: list[RuleSpec] = []
    identities: set[str] = set()
    bodies: set[str] = set()
    for path in _walk(rules):
        identity = _identity(path, rules)
        folded = identity.casefold()
        if folded in identities:
            raise ValueError(
                f"case-insensitive rule identity is duplicated: {identity}"
            )
        identities.add(folded)
        raw, body = _split_source(path)
        description, globs, tags = _metadata(path, raw)
        references = _references(repository, rules, path, body)
        normalized_body = body.strip()
        if normalized_body in bodies:
            raise ValueError(f"rule body duplicates another canonical source: {path}")
        bodies.add(normalized_body)
        specs.append(
            RuleSpec(
                path,
                identity,
                description,
                RuleActivation.PATH_SCOPED if globs else RuleActivation.ALWAYS,
                globs,
                references,
                body,
                tags,
            )
        )
    return tuple(sorted(specs, key=lambda spec: spec.identity))


__all__ = (
    "RuleActivation",
    "RuleDistribution",
    "RuleSpec",
    "audit_rule_specs",
)
