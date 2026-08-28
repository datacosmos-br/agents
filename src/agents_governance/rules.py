"""Typed, registry-free discovery of canonical engineering rules."""

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

_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_FRONTMATTER_FIELDS = frozenset({"description", "globs", "metadata"})
_METADATA_FIELDS = frozenset({"aihub.tags"})
_ROUTES = frozenset({"route:both", "route:personal", "route:project"})


class RuleActivation(StrEnum):
    """Canonical rule activation derived from local path scope metadata."""

    ALWAYS = "always"
    PATH_SCOPED = "path-scoped"


class RuleDistribution(StrEnum):
    """Projection route declared by semantic tags, never a registry."""

    PERSONAL = "personal"
    PROJECT = "project"
    BOTH = "both"


@dataclass(frozen=True)
class RuleFinding:
    """One blocking physical or semantic rule defect."""

    path: str
    code: str
    message: str


@dataclass(frozen=True)
class RuleSpec:
    """One fully validated canonical rule source."""

    path: Path
    identity: str
    description: str | None
    activation: RuleActivation
    globs: tuple[str, ...]
    references: tuple[str, ...]
    body: str
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        problem = _spec_problem(self)
        if problem is not None:
            raise ValueError(problem)

    @property
    def category(self) -> str:
        """Return the physical directory-owned taxonomy category."""

        parts = PurePosixPath(self.identity).parts
        return parts[0] if len(parts) > 1 else "root"

    @property
    def distribution(self) -> RuleDistribution:
        """Return the tag-derived route; untagged sources stay personal."""

        routes = tuple(tag for tag in self.tags if tag.startswith("route:"))
        return (
            RuleDistribution(routes[0].removeprefix("route:"))
            if routes
            else RuleDistribution.PERSONAL
        )


@dataclass(frozen=True)
class RuleAudit:
    """Deterministic rule discovery plus every blocking finding."""

    rules: tuple[RuleSpec, ...]
    findings: tuple[RuleFinding, ...]


class _RuleSourceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


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


def _glob_problem(value: str) -> str | None:
    if value != value.strip() or not value:
        return "path scope must be a non-empty trimmed string"
    if (
        value.startswith(("/", "~"))
        or "\\" in value
        or "//" in value
        or "$" in value
        or "\x00" in value
        or _SCHEME.match(value)
    ):
        return f"path scope must be repository-local: {value!r}"
    if any(part in {"", ".", ".."} for part in PurePosixPath(value).parts):
        return f"path scope must not escape or alias the project root: {value!r}"
    return None


def _spec_problem(spec: RuleSpec) -> str | None:
    if (
        not _identity_valid(spec.identity)
        or PurePosixPath(spec.identity).name != spec.path.stem
    ):
        return "rule identity must be path-derived from lowercase slugs"
    if spec.description is not None and not _description_valid(spec.description):
        return "rule description must be one non-empty trimmed line"
    if not spec.body.strip():
        return "rule body must be non-empty"
    if len(spec.globs) != len(set(spec.globs)):
        return "rule path scopes must be unique"
    if any(_glob_problem(glob) is not None for glob in spec.globs):
        return "rule path scope must be repository-local"
    expected_activation = (
        RuleActivation.PATH_SCOPED if spec.globs else RuleActivation.ALWAYS
    )
    if spec.activation is not expected_activation:
        return "rule activation must be derived from path scopes"
    if tuple(sorted(set(spec.references))) != spec.references:
        return "rule references must be unique and sorted"
    if any(
        not reference.startswith("rules/") or PurePosixPath(reference).suffix != ".md"
        for reference in spec.references
    ):
        return "rule references must target canonical Markdown rules"
    if len(spec.tags) != len(set(spec.tags)) or spec.tags != tuple(sorted(spec.tags)):
        return "rule tags must be unique and sorted"
    route_tags = tuple(tag for tag in spec.tags if tag.startswith("route:"))
    if spec.tags and (len(route_tags) != 1 or route_tags[0] not in _ROUTES):
        return "tagged rules require exactly one supported route tag"
    return None


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


def _split_source(text: str) -> tuple[dict[str, object] | None, str]:
    if not text.startswith("---\n"):
        return None, text
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise _RuleSourceError("rule-frontmatter", "unterminated YAML frontmatter")
    source = text[4:marker]
    try:
        node = yaml.compose(source, Loader=yaml.SafeLoader)
        loaded = yaml.safe_load(source)
    except yaml.YAMLError as error:
        raise _RuleSourceError(
            "rule-frontmatter", str(error).splitlines()[0]
        ) from error
    if not isinstance(node, MappingNode) or not isinstance(loaded, dict):
        raise _RuleSourceError("rule-frontmatter", "frontmatter must be a mapping")
    duplicate = _duplicate_key(node)
    if duplicate is not None:
        raise _RuleSourceError(
            "rule-frontmatter", f"frontmatter key is duplicated: {duplicate}"
        )
    raw = cast(dict[object, object], loaded)
    if not all(isinstance(key, str) for key in raw):
        raise _RuleSourceError("rule-frontmatter", "frontmatter keys must be strings")
    metadata = cast(dict[str, object], raw)
    unknown = sorted(set(metadata) - _FRONTMATTER_FIELDS)
    if unknown:
        raise _RuleSourceError(
            "rule-field", f"unknown rule frontmatter fields: {', '.join(unknown)}"
        )
    if not metadata:
        raise _RuleSourceError(
            "rule-frontmatter", "frontmatter must declare description or globs"
        )
    return metadata, text[marker + 5 :].removeprefix("\n")


def _metadata(
    raw: dict[str, object] | None,
) -> tuple[
    str | None,
    tuple[str, ...],
    tuple[str, ...],
]:
    if raw is None:
        return None, (), ()
    description = raw.get("description")
    if description is not None and (
        not isinstance(description, str) or not _description_valid(description)
    ):
        raise _RuleSourceError(
            "rule-description", "description must be one non-empty trimmed line"
        )
    raw_globs = raw.get("globs")
    if raw_globs is None:
        globs: tuple[str, ...] = ()
    elif isinstance(raw_globs, str):
        globs = (raw_globs,)
    elif isinstance(raw_globs, list) and all(
        isinstance(item, str) for item in raw_globs
    ):
        globs = tuple(cast(list[str], raw_globs))
    else:
        raise _RuleSourceError(
            "rule-globs", "globs must be a string or an array of strings"
        )
    if raw_globs is not None and not globs:
        raise _RuleSourceError("rule-globs", "globs must not be empty")
    if len(globs) != len(set(globs)):
        raise _RuleSourceError("rule-duplicate", "path scopes must be unique")
    for glob in globs:
        problem = _glob_problem(glob)
        if problem is not None:
            raise _RuleSourceError("rule-globs", problem)
    raw_metadata = raw.get("metadata")
    if raw_metadata is None:
        tags: tuple[str, ...] = ()
    else:
        if not isinstance(raw_metadata, dict) or set(raw_metadata) != _METADATA_FIELDS:
            raise _RuleSourceError("rule-tags", "metadata must contain only aihub.tags")
        encoded = raw_metadata.get("aihub.tags")
        if not isinstance(encoded, str):
            raise _RuleSourceError(
                "rule-tags", "metadata.aihub.tags must be a JSON string"
            )
        try:
            decoded: object = json.loads(encoded)
        except json.JSONDecodeError as error:
            raise _RuleSourceError("rule-tags", "invalid tag JSON") from error
        if not isinstance(decoded, list) or not all(
            isinstance(item, str) for item in decoded
        ):
            raise _RuleSourceError(
                "rule-tags", "metadata.aihub.tags must encode an array of strings"
            )
        tags = tuple(cast(list[str], decoded))
        if (
            len(tags) != len(set(tags))
            or tags != tuple(sorted(tags))
            or any(tag not in _ROUTES for tag in tags)
        ):
            raise _RuleSourceError(
                "rule-tags", "rules require unique sorted supported route tags"
            )
        if len(tags) != 1:
            raise _RuleSourceError(
                "rule-tags", "tagged rules require exactly one route tag"
            )
    return cast(str | None, description), globs, tags


def _link_target(raw: str) -> str:
    candidate = raw.strip()
    if candidate.startswith("<"):
        closing = candidate.find(">", 1)
        return candidate[1:closing] if closing > 0 else candidate
    return candidate.split(maxsplit=1)[0] if candidate else candidate


def _local_reference(
    root: Path, rules: Path, source: Path, target: str
) -> tuple[str | None, str | None]:
    if not target or target.startswith("#"):
        return None, None
    if _SCHEME.match(target):
        scheme = urlsplit(target).scheme.lower()
        if scheme == "file":
            return None, "file URI references are forbidden"
        return None, None
    decoded = unquote(target).split("#", 1)[0].split("?", 1)[0]
    if not decoded:
        return None, None
    if decoded.startswith(("/", "//", "~")) or "\\" in decoded or "$" in decoded:
        return None, f"reference must remain inside rules/: {target!r}"
    local = Path(
        os.path.normpath(source.parent.joinpath(*PurePosixPath(decoded).parts))
    )
    try:
        lexical_parts = local.relative_to(rules).parts
        cursor = rules
        for part in lexical_parts:
            cursor /= part
            if cursor.is_symlink():
                return None, f"reference target is symlinked: {target!r}"
        canonical = local.resolve(strict=False)
        canonical.relative_to(rules)
    except (OSError, ValueError):
        return None, f"reference escapes rules/: {target!r}"
    if canonical.suffix != ".md":
        return None, f"reference must target a Markdown rule: {target!r}"
    try:
        metadata = canonical.lstat()
    except OSError as error:
        return None, f"reference target is unavailable: {target!r}: {error}"
    if not stat.S_ISREG(metadata.st_mode):
        return None, f"reference target is not a physical file: {target!r}"
    return _relative(root, canonical), None


def _references(
    root: Path, rules: Path, source: Path, body: str
) -> tuple[tuple[str, ...], list[RuleFinding]]:
    relative = _relative(root, source)
    references: set[str] = set()
    findings: list[RuleFinding] = []
    for match in _LINK.finditer(body):
        target = _link_target(match.group(1))
        reference, problem = _local_reference(root, rules, source, target)
        if problem is not None:
            findings.append(RuleFinding(relative, "rule-reference", problem))
        elif reference is not None:
            references.add(reference)
    return tuple(sorted(references)), findings


def _walk(root: Path, directory: Path) -> tuple[list[Path], list[RuleFinding]]:
    files: list[Path] = []
    findings: list[RuleFinding] = []

    def visit(parent: Path) -> None:
        try:
            entries = sorted(parent.iterdir(), key=lambda path: path.name)
        except OSError as error:
            findings.append(RuleFinding(_relative(root, parent), "rule-io", str(error)))
            return
        for path in entries:
            relative = _relative(root, path)
            try:
                metadata = path.lstat()
            except OSError as error:
                findings.append(RuleFinding(relative, "rule-io", str(error)))
                continue
            if stat.S_ISLNK(metadata.st_mode):
                findings.append(
                    RuleFinding(
                        relative, "rule-symlink", "rule sources must be physical"
                    )
                )
            elif stat.S_ISDIR(metadata.st_mode):
                if _SLUG.fullmatch(path.name) is None:
                    findings.append(
                        RuleFinding(
                            relative,
                            "rule-path",
                            "rule directories must be lowercase path slugs",
                        )
                    )
                else:
                    visit(path)
            elif not stat.S_ISREG(metadata.st_mode) or path.suffix != ".md":
                findings.append(
                    RuleFinding(
                        relative,
                        "rule-path",
                        "rules/ supports only physical Markdown rule files",
                    )
                )
            else:
                files.append(path)

    visit(directory)
    return files, findings


def audit_rule_specs(root: Path) -> RuleAudit:
    """Discover every physical rule and collect all contract violations."""

    repository = root.resolve()
    rules = repository / "rules"
    try:
        root_metadata = rules.lstat()
    except FileNotFoundError:
        return RuleAudit(
            (), (RuleFinding("rules", "rule-root", "rules/ does not exist"),)
        )
    except OSError as error:
        return RuleAudit((), (RuleFinding("rules", "rule-io", str(error)),))
    if stat.S_ISLNK(root_metadata.st_mode):
        return RuleAudit(
            (), (RuleFinding("rules", "rule-symlink", "rules/ must be physical"),)
        )
    if not stat.S_ISDIR(root_metadata.st_mode):
        return RuleAudit(
            (), (RuleFinding("rules", "rule-root", "rules/ must be a directory"),)
        )

    candidates, findings = _walk(repository, rules)
    identities: dict[str, list[Path]] = {}
    for path in candidates:
        identities.setdefault(_identity(path, rules).casefold(), []).append(path)
    duplicate_paths = {
        path for paths in identities.values() if len(paths) > 1 for path in paths
    }

    specs: list[RuleSpec] = []
    for path in sorted(candidates):
        relative = _relative(repository, path)
        identity = _identity(path, rules)
        file_findings: list[RuleFinding] = []
        if not _identity_valid(identity):
            file_findings.append(
                RuleFinding(
                    relative,
                    "rule-path",
                    "rule paths must contain only lowercase slugs",
                )
            )
        if path in duplicate_paths:
            file_findings.append(
                RuleFinding(
                    relative,
                    "rule-duplicate",
                    f"case-insensitive rule identity is duplicated: {identity}",
                )
            )
        try:
            text = path.read_text(encoding="utf-8")
            raw, body = _split_source(text)
            description, globs, tags = _metadata(raw)
        except (OSError, UnicodeError) as error:
            file_findings.append(RuleFinding(relative, "rule-io", str(error)))
            findings.extend(file_findings)
            continue
        except _RuleSourceError as error:
            file_findings.append(RuleFinding(relative, error.code, str(error)))
            findings.extend(file_findings)
            continue
        if not body.strip():
            file_findings.append(
                RuleFinding(relative, "rule-body", "rule body must be non-empty")
            )
        references, reference_findings = _references(repository, rules, path, body)
        file_findings.extend(reference_findings)
        if not file_findings:
            specs.append(
                RuleSpec(
                    path=path,
                    identity=identity,
                    description=description,
                    activation=(
                        RuleActivation.PATH_SCOPED if globs else RuleActivation.ALWAYS
                    ),
                    globs=globs,
                    references=references,
                    body=body,
                    tags=tags,
                )
            )
        findings.extend(file_findings)

    bodies: dict[str, list[RuleSpec]] = {}
    for spec in specs:
        bodies.setdefault(spec.body.strip(), []).append(spec)
    duplicate_specs = {
        spec for matching in bodies.values() if len(matching) > 1 for spec in matching
    }
    for spec in duplicate_specs:
        findings.append(
            RuleFinding(
                _relative(repository, spec.path),
                "rule-duplicate",
                "rule body duplicates another canonical source",
            )
        )

    return RuleAudit(
        tuple(
            sorted(
                (spec for spec in specs if spec not in duplicate_specs),
                key=lambda spec: spec.identity,
            )
        ),
        tuple(sorted(findings, key=lambda item: (item.path, item.code, item.message))),
    )


__all__ = [
    "RuleActivation",
    "RuleAudit",
    "RuleDistribution",
    "RuleFinding",
    "RuleSpec",
    "audit_rule_specs",
]
