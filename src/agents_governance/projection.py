"""Strict directory-surface projection with atomic physical publication."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass, replace
from enum import StrEnum
from functools import partial
from pathlib import Path, PurePosixPath
from typing import cast

import yaml

from .agent_profiles import (
    AgentContext,
    AgentProfile,
    AgentProvider,
    render_agent,
)
from .atomic_io import atomic_write_text
from .catalog import (
    NON_PORTABLE_PROJECT_REFERENCE,
    Catalog,
    SkillCategory,
    SkillRecord,
)
from .cleanup import (
    PreparedPublication,
    Publication,
    remove_physical,
    run_atomic_publications,
    run_with_cleanup,
)
from .commands import (
    CommandProvider,
    CommandRoute,
    CommandSpec,
    CommandTokenBudget,
    render_command,
    waza_bpe_counter,
)
from .frontmatter import cast_mapping, require_exact_fields
from .physical_paths import absolute_path, symlink_component
from .projection_authorization import (
    PROJECT_SELECTION,
    ProjectAuthorization,
    load_project_authorization,
)
from .projection_config import (
    DetectionCondition,
    DetectionConditionType,
    DetectionOperator,
    ProjectDetectionRule,
    ProjectionCell,
    ProjectionConfig,
    ProjectionContext,
    ProjectionStatus,
    ProjectionSurface,
    RuleLayout,
)
from .rule_adapters import RuleContext, RuleProvider, render_rule
from .rules import RuleDistribution, RuleSpec, prompt_defense_body
from .validation import validate_skill_catalogs

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_MARKDOWN_LINK = re.compile(r"!?\[[^\]\n]*\]\(([^)\n]+)\)")
_TEXT_SUFFIXES = frozenset(
    {
        "",
        ".css",
        ".html",
        ".ini",
        ".js",
        ".json",
        ".jsx",
        ".md",
        ".mdx",
        ".py",
        ".sh",
        ".toml",
        ".ts",
        ".tsx",
        ".txt",
        ".yaml",
        ".yml",
    }
)
_SELECTION_FIELDS_V1 = frozenset({"agents", "opt_ins", "selected_tags", "version"})
_SELECTION_FIELDS_V2 = frozenset(
    {"agents", "opt_ins", "selected_tags", "version", "detection_rules"}
)
_SELECTION_FIELDS_V3 = frozenset(
    {
        "agents",
        "detection_catalog_digest",
        "opt_ins",
        "project_profile",
        "selected_tags",
        "version",
    }
)
_DETECTION_EXCLUDED_COMPONENTS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".test-tmp",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "target",
    }
)
_DETECTION_MAX_FILES = 10_000
_DETECTION_MAX_FILE_BYTES = 1_048_576
_DETECTION_MAX_TOTAL_BYTES = 67_108_864
_MANIFEST_FIELDS = frozenset(
    {
        "context",
        "destination",
        "managed",
        "owner",
        "project",
        "providers",
        "selection",
        "surface",
        "version",
    }
)
_ENTRY_FIELDS = frozenset(
    {
        "activation",
        "adapter_version",
        "destination",
        "link_target",
        "origin",
        "physical_digest",
        "slug",
        "source_digest",
        "source_type",
    }
)
_ENTRY_FIELDS_V5 = _ENTRY_FIELDS - {"link_target"}
_PRIOR_PROJECTION_MANIFEST_VERSION = 5


class ProjectionDriftError(RuntimeError):
    """The project projection differs from its canonical source."""


class ProjectProfile(StrEnum):
    """Closed project-governance profiles selected by the association owner."""

    UNCLASSIFIED = "unclassified"
    INTERNAL = "internal"
    INTERNAL_FLEXT = "internal_flext"
    THIRD_PARTY_FORK = "third_party_fork"


@dataclass(frozen=True)
class ProjectionSelection:
    agents: tuple[str, ...] = ()
    opt_ins: tuple[str, ...] = ()
    selected_tags: tuple[str, ...] = ()
    project_profile: ProjectProfile = ProjectProfile.UNCLASSIFIED

    def payload(self) -> dict[str, list[str]]:
        return {
            "agents": list(self.agents),
            "opt_ins": list(self.opt_ins),
            "selected_tags": list(self.selected_tags),
        }


@dataclass(frozen=True)
class ProjectionSource:
    name: str
    source: Path
    origin: str
    source_digest: str
    physical_digest: str
    source_type: str
    slug: str
    activation: tuple[str, ...]
    content: str | None = None
    adapter_version: int = 1
    link_target: str | None = None

    def metadata(self) -> dict[str, object]:
        return {
            "activation": list(self.activation),
            "adapter_version": self.adapter_version,
            "destination": self.name,
            "link_target": self.link_target,
            "origin": self.origin,
            "physical_digest": self.physical_digest,
            "slug": self.slug,
            "source_digest": self.source_digest,
            "source_type": self.source_type,
        }


@dataclass(frozen=True)
class ProjectionPlan:
    project: Path
    root: Path
    providers: tuple[str, ...]
    context: ProjectionContext
    surface: ProjectionSurface
    selection: ProjectionSelection
    sources: tuple[ProjectionSource, ...]


@dataclass(frozen=True)
class _TargetState:
    plan: ProjectionPlan
    previous: dict[str, dict[str, object]]
    snapshot: str | None
    drift: bool
    retired_gc_links: dict[str, str]


@dataclass
class _StagedTarget:
    state: _TargetState
    stage: Path
    candidate: Path
    backup: Path
    candidate_snapshot: str
    created_parents: tuple[Path, ...] = ()
    installed: bool = False
    had_root: bool = False


def _strings(value: object, context: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item and item == item.strip() for item in value
    ):
        raise TypeError(f"{context} must be an array of non-empty trimmed strings")
    selected = tuple(cast(list[str], value))
    if selected != tuple(sorted(set(selected))):
        raise ValueError(f"{context} must be unique and sorted")
    return selected


def _tree_snapshot(root: Path, allowed_links: dict[str, str] | None = None) -> str:
    """Digest one destination tree; only managed alias links are permitted."""

    links = allowed_links or {}
    digest = hashlib.sha256()

    def visit(path: Path) -> None:
        metadata = path.lstat()
        relative = path.relative_to(root).as_posix() if path != root else "."
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(f"{stat.S_IMODE(metadata.st_mode):04o}".encode())
        digest.update(b"\0")
        if stat.S_ISLNK(metadata.st_mode):
            target = os.readlink(path)
            if links.get(relative) != target:
                raise ValueError(f"projection destination symlink forbidden: {path}")
            digest.update(b"symlink\0")
            digest.update(target.encode())
            digest.update(b"\0")
            return
        if stat.S_ISDIR(metadata.st_mode):
            digest.update(b"directory\0")
            with os.scandir(path) as entries:
                children = sorted((Path(entry.path) for entry in entries), key=str)
            for child in children:
                visit(child)
            return
        if stat.S_ISREG(metadata.st_mode):
            digest.update(b"file\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
            return
        raise RuntimeError(f"projection destination contains a special file: {path}")

    visit(root)
    return digest.hexdigest()


def _retired_gc_links(root: Path) -> dict[str, str]:
    """Validate the exact retired Gas City projection before atomic cutover."""

    manifest = root / ".gc-skill-ownership.json"
    if not manifest.exists() and not manifest.is_symlink():
        return {}
    if manifest.is_symlink() or not manifest.is_file():
        raise ValueError(f"retired Gas City manifest must be a physical file: {manifest}")
    payload = cast_mapping(json.loads(manifest.read_text(encoding="utf-8")), str(manifest))
    require_exact_fields(payload, frozenset({"targets"}), str(manifest))
    targets = cast_mapping(payload["targets"], f"{manifest}: targets")
    links: dict[str, str] = {}
    for name, raw_target in targets.items():
        if Path(name).name != name or not name:
            raise ValueError(f"retired Gas City skill name is invalid: {name!r}")
        if not isinstance(raw_target, str) or not raw_target:
            raise TypeError(f"retired Gas City skill target is invalid: {name}")
        destination = root / name
        if not destination.exists() and not destination.is_symlink():
            continue
        if not destination.is_symlink():
            raise ValueError(f"retired Gas City skill is not an owned symlink: {destination}")
        observed = os.readlink(destination)
        if observed != raw_target:
            raise ValueError(f"retired Gas City skill target differs: {destination}")
        links[name] = raw_target
    return links


def _discard_owned_tree(path: Path) -> None:
    """Remove one exact staging/publication tree without following links."""

    metadata = path.lstat()
    if stat.S_ISLNK(metadata.st_mode) or stat.S_ISREG(metadata.st_mode):
        path.unlink()
        return
    if not stat.S_ISDIR(metadata.st_mode):
        raise RuntimeError(f"owned projection artifact has unsupported type: {path}")
    with os.scandir(path) as entries:
        children = tuple(Path(entry.path) for entry in entries)
    for child in children:
        _discard_owned_tree(child)
    path.rmdir()


def _linked_worktree_owns(git_directory: Path, git_file: Path) -> bool:
    """Prove the administrative directory back-references this exact .git file.

    A linked worktree's administrative directory always carries a ``gitdir``
    file naming the worktree's own ``.git`` file. That back-reference is the
    physical ownership proof; a borrowed or external Git directory has none.

    Git writes that reference relative to the administrative directory when
    ``worktree.useRelativePaths`` is set, so it is resolved against that
    directory rather than against the current working directory.
    """

    back_pointer = git_directory / "gitdir"
    if not back_pointer.is_file():
        return False
    referenced = Path(back_pointer.read_text(encoding="utf-8").strip())
    if not referenced.is_absolute():
        referenced = git_directory / referenced
    return referenced.resolve() == git_file.resolve()


def _physical_project(cwd: Path) -> Path:
    current = absolute_path(cwd)
    if symlink_component(current) is not None or not current.is_dir():
        raise ValueError(f"invocation directory must be physical: {current}")
    for candidate in (current, *current.parents):
        git = candidate / ".git"
        if git.is_symlink():
            raise ValueError(f"Git metadata symlink forbidden: {git}")
        if git.exists():
            project = candidate.resolve(strict=True)
            metadata = git.lstat()
            if stat.S_ISDIR(metadata.st_mode):
                pass
            elif stat.S_ISREG(metadata.st_mode):
                git_directory = Path(
                    subprocess.run(
                        (
                            "git",
                            "-C",
                            str(project),
                            "rev-parse",
                            "--absolute-git-dir",
                        ),
                        check=True,
                        text=True,
                        stdout=subprocess.PIPE,
                    ).stdout.strip()
                ).resolve(strict=True)
                raw_superproject = subprocess.run(
                    (
                        "git",
                        "-C",
                        str(project),
                        "rev-parse",
                        "--show-superproject-working-tree",
                    ),
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                ).stdout.strip()
                if not raw_superproject:
                    if _linked_worktree_owns(git_directory, git):
                        return project
                    raise ValueError(
                        f"external Git directory is forbidden: {git_directory}"
                    )
                superproject = Path(raw_superproject).resolve(strict=True)
                project.relative_to(superproject)
                umbrella: Path | None = None
                for ancestor in (superproject, *superproject.parents):
                    root_git = ancestor / ".git"
                    if root_git.is_symlink():
                        raise ValueError(f"Git metadata symlink forbidden: {root_git}")
                    if root_git.is_dir() and stat.S_ISDIR(root_git.lstat().st_mode):
                        umbrella = ancestor.resolve(strict=True)
                        break
                if umbrella is None:
                    raise ValueError(
                        f"submodule umbrella has no physical .git directory: {project}"
                    )
                project.relative_to(umbrella)
                modules = (umbrella / ".git" / "modules").resolve(strict=True)
                if symlink_component(git_directory) is not None:
                    raise ValueError(
                        f"submodule Git directory traverses symlink: {git_directory}"
                    )
                if git_directory != modules and modules not in git_directory.parents:
                    raise ValueError(
                        f"submodule Git directory escapes umbrella: {git_directory}"
                    )
            else:
                raise ValueError(f"unsupported Git metadata type: {git}")
            return project
    raise ValueError(
        f"invocation directory is not inside a physical Git project: {cwd}"
    )


def _confined(project: Path, raw: str) -> Path:
    relative = Path(raw)
    if relative.is_absolute() or relative == Path(".") or ".." in relative.parts:
        raise ValueError(f"project projection path escapes repository: {raw}")
    target = absolute_path(project / relative)
    target.relative_to(project)
    symlink = symlink_component(target)
    if symlink is not None:
        raise ValueError(f"projection path symlink forbidden: {symlink}")
    return target


def _rendered_digests(name: str, content: str) -> tuple[str, str]:
    logical = hashlib.sha256()
    logical.update(name.encode())
    logical.update(b"\0")
    logical.update(content.encode())
    logical.update(b"\0")
    physical = hashlib.sha256()
    physical.update(b"file\0.\0")
    physical.update(b"0644\0")
    physical.update(content.encode())
    physical.update(b"\0")
    return logical.hexdigest(), physical.hexdigest()


def _local_link(target: str) -> str | None:
    raw = target.strip()
    if raw.startswith("<"):
        closing = raw.find(">", 1)
        raw = raw[1:closing] if closing > 0 else raw
    else:
        raw = raw.split(maxsplit=1)[0] if raw else raw
    if not raw or raw.startswith("#") or ":" in raw.split("/", 1)[0]:
        return None
    return raw.split("#", 1)[0].split("?", 1)[0]


def _validate_source_portability(source: Path, activation: str | None) -> None:
    Catalog.physical_tree_contract(source)
    files = (
        (source,)
        if source.is_file()
        else tuple(path for path in sorted(source.rglob("*")) if path.is_file())
    )
    for path in files:
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        if activation == "opt-in":
            continue
        if NON_PORTABLE_PROJECT_REFERENCE.search(text):
            raise ValueError(
                f"project source contains a non-portable reference: {path}"
            )
        if path.suffix.lower() not in {".md", ".mdx"}:
            continue
        for match in _MARKDOWN_LINK.finditer(text):
            target = _local_link(match.group(1))
            if target is None:
                continue
            if source.is_file():
                raise ValueError(f"rendered source contains a relative link: {path}")
            candidate = absolute_path(path.parent / target)
            candidate.relative_to(source)


def _rendered_source(
    *,
    name: str,
    source: Path,
    origin: str,
    source_type: str,
    slug: str,
    activation: tuple[str, ...],
    content: str,
    project_portability: bool,
) -> ProjectionSource:
    if project_portability and NON_PORTABLE_PROJECT_REFERENCE.search(content):
        raise ValueError(
            f"project {source_type} contains a non-portable reference: {source}"
        )
    logical, physical = _rendered_digests(name, content)
    return ProjectionSource(
        name,
        source,
        origin,
        logical,
        physical,
        source_type,
        slug,
        activation,
        content,
    )


class Projector:
    """Converge every supported project surface for the invocation project."""

    MANIFEST = ".agents-governance.json"
    SELECTION = PROJECT_SELECTION

    def __init__(
        self,
        catalog: Catalog,
        config: ProjectionConfig,
        commands: tuple[CommandSpec, ...],
        agents: tuple[AgentProfile, ...],
        rules: tuple[RuleSpec, ...],
    ) -> None:
        self.catalog = catalog
        self.config = config
        self.commands = commands
        self.agents = agents
        self.rules = rules

    @staticmethod
    def project_root() -> Path:
        """Derive the only projection target from the invocation directory."""

        return _physical_project(Path.cwd())

    @staticmethod
    def _bounded_detection_pattern(pattern: str, label: str) -> None:
        portable = PurePosixPath(pattern)
        if (
            portable.is_absolute()
            or not portable.parts
            or ".." in portable.parts
            or any(char in portable.parts[0] for char in "*?[")
        ):
            raise ValueError(
                f"{label} must use a bounded relative glob with a literal "
                f"first component: {pattern}"
            )

    @staticmethod
    def _contained_physical_path(candidate: Path, project: Path) -> Path | None:
        if candidate.is_symlink():
            return None
        resolved = candidate.resolve(strict=False)
        if not resolved.is_relative_to(project.resolve(strict=True)):
            return None
        return resolved

    @staticmethod
    def _detection_paths(condition: DetectionCondition) -> tuple[str, ...]:
        for path in condition.paths:
            Projector._bounded_detection_pattern(path, "detection condition paths")
        return condition.paths

    @staticmethod
    def _detect_condition_holds(project: Path, condition: DetectionCondition) -> bool:
        condition_type = condition.condition_type
        pattern = condition.pattern
        Projector._bounded_detection_pattern(pattern, "detection pattern")
        pattern_path = PurePosixPath(pattern)

        def excluded(candidate: Path) -> bool:
            return any(
                part in _DETECTION_EXCLUDED_COMPONENTS
                for part in candidate.relative_to(project).parts
            )

        if condition_type in (
            DetectionConditionType.FILE_CONTAINS,
            DetectionConditionType.FILE_NOT_CONTAINS,
        ):
            paths = Projector._detection_paths(condition)
            matched_files: set[Path] = set()
            total_bytes = 0
            for glob_pattern in paths:
                for candidate in project.glob(glob_pattern):
                    if excluded(candidate):
                        continue
                    if Projector._contained_physical_path(candidate, project) is None:
                        continue
                    if not candidate.is_file():
                        continue
                    if len(matched_files) >= _DETECTION_MAX_FILES:
                        raise ValueError(
                            f"detection paths exceeded {_DETECTION_MAX_FILES} files"
                        )
                    matched_files.add(candidate)

            for candidate in sorted(matched_files):
                size = candidate.stat().st_size
                if size > _DETECTION_MAX_FILE_BYTES:
                    raise ValueError(
                        f"{candidate} is {size} bytes; detection files may not "
                        f"exceed {_DETECTION_MAX_FILE_BYTES} bytes"
                    )
                total_bytes += size
                if total_bytes > _DETECTION_MAX_TOTAL_BYTES:
                    raise ValueError(
                        "detection files exceed "
                        f"{_DETECTION_MAX_TOTAL_BYTES} total bytes"
                    )

            contains = any(
                pattern in candidate.read_text(encoding="utf-8")
                for candidate in matched_files
            )
            return (
                contains
                if condition_type is DetectionConditionType.FILE_CONTAINS
                else not contains
            )

        matches: list[Path] = []
        for candidate in project.glob(pattern):
            if excluded(candidate):
                continue
            if Projector._contained_physical_path(candidate, project) is not None:
                matches.append(candidate)
            if len(matches) > _DETECTION_MAX_FILES:
                raise ValueError(
                    f"detection pattern exceeded {_DETECTION_MAX_FILES} paths"
                )
        has_match = bool(matches)
        if not has_match and not any(char in pattern_path.name for char in "*?["):
            candidate = project / pattern
            has_match = (
                candidate.is_file()
                and Projector._contained_physical_path(candidate, project) is not None
                and not candidate.is_symlink()
            )
        return (
            has_match
            if condition_type is DetectionConditionType.PATH_EXISTS
            else not has_match
        )

    @staticmethod
    def _detect_active_tags(
        project: Path, rules: tuple[ProjectDetectionRule, ...]
    ) -> set[str]:
        active: set[str] = set()
        seen_rule_ids: set[str] = set()
        for rule in rules:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", rule.rule_id):
                raise ValueError(f"detection rule id invalid: {rule.rule_id}")
            if rule.rule_id in seen_rule_ids:
                raise ValueError(
                    f"detection rules duplicates detection rule id {rule.rule_id}"
                )
            seen_rule_ids.add(rule.rule_id)
            results = [
                Projector._detect_condition_holds(project, condition)
                for condition in rule.conditions
            ]
            triggered = (
                all(results)
                if rule.operator is DetectionOperator.ALL
                else any(results)
                if rule.operator is DetectionOperator.ANY
                else not any(results)
            )
            if not triggered:
                continue
            for tag in rule.activate_tags:
                if not re.fullmatch(r"[a-z0-9]+(?:[-:][a-z0-9]+)*", tag):
                    raise ValueError(f"detection activate tag invalid: {tag}")
                active.add(tag)
        return active

    @staticmethod
    def _render_detection_rules(rules: tuple[ProjectDetectionRule, ...]):
        return [
            {
                "activate_tags": list(rule.activate_tags),
                "id": rule.rule_id,
                "when": {
                    rule.operator.value: [
                        {
                            **(
                                {"paths": list(condition.paths)}
                                if condition.paths
                                else {}
                            ),
                            "pattern": condition.pattern,
                            "type": condition.condition_type.value,
                        }
                        for condition in rule.conditions
                    ]
                },
            }
            for rule in rules
        ]

    @staticmethod
    def _detection_catalog_digest(rules: tuple[ProjectDetectionRule, ...]) -> str:
        payload = json.dumps(
            Projector._render_detection_rules(rules),
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _profile_from_tags(tags: set[str]) -> ProjectProfile | None:
        fork = "third-party-fork" in tags
        internal = "internal" in tags
        flext = "flext" in tags or "internal-flext" in tags
        if fork and (internal or flext):
            raise ValueError(
                "project detection produced conflicting ownership profiles"
            )
        if fork:
            return ProjectProfile.THIRD_PARTY_FORK
        if flext:
            return ProjectProfile.INTERNAL_FLEXT
        if internal:
            return ProjectProfile.INTERNAL
        return None

    @staticmethod
    def _selection_document(
        rules: tuple[ProjectDetectionRule, ...], profile: ProjectProfile
    ) -> str:
        return (
            json.dumps(
                {
                    "agents": [],
                    "detection_catalog_digest": Projector._detection_catalog_digest(
                        rules
                    ),
                    "opt_ins": [],
                    "project_profile": profile.value,
                    "selected_tags": [],
                    "version": 3,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )

    def authorize(self, project: Path) -> ProjectAuthorization:
        """Authorize a detected canonical project with one minimal selection."""

        authorization = load_project_authorization(project)
        if authorization.selected or not self.config.project_detection_rules:
            return authorization
        path = project / PROJECT_SELECTION
        active_tags = Projector._detect_active_tags(
            project, self.config.project_detection_rules
        )
        profile = Projector._profile_from_tags(active_tags)
        if profile is None:
            return authorization
        text = Projector._selection_document(
            self.config.project_detection_rules, profile
        )
        created: list[Path] = []

        def publish_selection() -> None:
            cursor = path.parent
            missing: list[Path] = []
            while not cursor.exists():
                missing.append(cursor)
                cursor = cursor.parent
            if symlink_component(cursor) is not None or not cursor.is_dir():
                raise ValueError(
                    f"selection parent must be a physical directory: {cursor}"
                )
            for directory in reversed(missing):
                directory.mkdir()
                created.append(directory)
            atomic_write_text(path, text, mode=0o644)

        def rollback_directories() -> None:
            for directory in reversed(created):
                directory.rmdir()

        run_with_cleanup(publish_selection, rollback_directories)
        return load_project_authorization(project)

    def _selection(
        self,
        authorization: ProjectAuthorization,
    ) -> ProjectionSelection | None:
        if authorization.payload is None:
            return None
        path = authorization.path
        payload = cast_mapping(json.loads(authorization.payload), str(path))
        version = payload.get("version")
        if version not in (1, 2, 3):
            raise ValueError(f"projection selection version must be 1, 2, or 3: {path}")
        allowed = (
            _SELECTION_FIELDS_V3
            if version == 3
            else _SELECTION_FIELDS_V2
            if version == 2 and "detection_rules" in payload
            else _SELECTION_FIELDS_V1
        )
        require_exact_fields(payload, allowed, str(path))
        agents = _strings(payload["agents"], f"{path}: agents")
        opt_ins = _strings(payload["opt_ins"], f"{path}: opt_ins")
        selected_tags: set[str] = set(
            _strings(payload["selected_tags"], f"{path}: selected_tags")
        )
        profile = ProjectProfile.UNCLASSIFIED
        if version == 3:
            raw_profile = payload["project_profile"]
            if not isinstance(raw_profile, str):
                raise TypeError(f"{path}: project_profile must be a string")
            profile = ProjectProfile(raw_profile)
            digest = payload["detection_catalog_digest"]
            if not isinstance(digest, str) or _DIGEST.fullmatch(digest) is None:
                raise TypeError(
                    f"{path}: detection_catalog_digest must be a SHA-256 digest"
                )
            expected_digest = Projector._detection_catalog_digest(
                self.config.project_detection_rules
            )
            if digest != expected_digest:
                raise ValueError(
                    f"{path}: detection catalog differs from canonical projection config"
                )
            detected_tags = Projector._detect_active_tags(
                authorization.project, self.config.project_detection_rules
            )
            detected_profile = Projector._profile_from_tags(detected_tags)
            if detected_profile is not None and detected_profile is not profile:
                raise ValueError(
                    f"{path}: project profile conflicts with current detection evidence"
                )
            if profile is ProjectProfile.INTERNAL:
                selected_tags.add("internal")
            elif profile is ProjectProfile.INTERNAL_FLEXT:
                selected_tags.update(("flext", "internal"))
            elif profile is ProjectProfile.THIRD_PARTY_FORK:
                selected_tags.add("third-party-fork")
            selected_tags.update(detected_tags)
        if version == 2 and "detection_rules" in payload:
            expected_rules = Projector._render_detection_rules(
                self.config.project_detection_rules
            )
            if payload["detection_rules"] != expected_rules:
                raise ValueError(
                    f"{path}: detection_rules must equal the canonical projection config"
                )
            selected_tags.update(
                Projector._detect_active_tags(
                    authorization.project,
                    self.config.project_detection_rules,
                )
            )
        return ProjectionSelection(
            agents, opt_ins, tuple(sorted(selected_tags)), profile
        )

    @staticmethod
    def _normalized_dependency(value: str) -> str | None:
        match = re.match(r"\s*([A-Za-z0-9@][A-Za-z0-9@/._-]*)", value)
        return match.group(1).lower().replace("_", "-") if match else None

    @classmethod
    def _dependencies(cls, project: Path) -> set[str]:
        names: set[str] = set()

        def add_requirements(raw: object, context: str) -> None:
            if not isinstance(raw, list) or not all(
                isinstance(item, str) for item in raw
            ):
                raise TypeError(f"{context} must be an array of strings")
            for item in cast(list[str], raw):
                normalized = cls._normalized_dependency(item)
                if normalized is not None:
                    names.add(normalized)

        pyproject = project / "pyproject.toml"
        if pyproject.is_symlink():
            raise ValueError(f"dependency manifest symlink forbidden: {pyproject}")
        if pyproject.is_file():
            loaded = cast_mapping(
                tomllib.loads(pyproject.read_text(encoding="utf-8")), str(pyproject)
            )

            if "project" in loaded:
                project_table = cast_mapping(loaded["project"], f"{pyproject}: project")
                add_requirements(
                    project_table.get("dependencies", []),
                    f"{pyproject}: project.dependencies",
                )
                optional = cast_mapping(
                    project_table.get("optional-dependencies", {}),
                    f"{pyproject}: project.optional-dependencies",
                )
                for optional_name, raw in optional.items():
                    add_requirements(
                        raw,
                        f"{pyproject}: project.optional-dependencies.{optional_name}",
                    )
            groups = cast_mapping(
                loaded.get("dependency-groups", {}),
                f"{pyproject}: dependency-groups",
            )
            for dependency_group_name, raw in groups.items():
                add_requirements(
                    raw,
                    f"{pyproject}: dependency-groups.{dependency_group_name}",
                )
            tool = cast_mapping(loaded.get("tool", {}), f"{pyproject}: tool")
            if "poetry" in tool:
                poetry = cast_mapping(tool["poetry"], f"{pyproject}: tool.poetry")
                direct = cast_mapping(
                    poetry.get("dependencies", {}),
                    f"{pyproject}: tool.poetry.dependencies",
                )
                names.update(
                    name.lower().replace("_", "-")
                    for name in direct
                    if name.lower() != "python"
                )
                poetry_groups = cast_mapping(
                    poetry.get("group", {}), f"{pyproject}: tool.poetry.group"
                )
                for group_name, raw_group in poetry_groups.items():
                    poetry_group = cast_mapping(
                        raw_group,
                        f"{pyproject}: tool.poetry.group.{group_name}",
                    )
                    group_dependencies = cast_mapping(
                        poetry_group.get("dependencies", {}),
                        f"{pyproject}: tool.poetry.group.{group_name}.dependencies",
                    )
                    names.update(
                        name.lower().replace("_", "-") for name in group_dependencies
                    )
        package_path = project / "package.json"
        if package_path.is_symlink():
            raise ValueError(f"dependency manifest symlink forbidden: {package_path}")
        if package_path.is_file():
            package = cast_mapping(
                json.loads(package_path.read_text(encoding="utf-8")), str(package_path)
            )
            for field in ("dependencies", "devDependencies", "peerDependencies"):
                dependencies = cast_mapping(
                    package.get(field, {}), f"{package_path}: {field}"
                )
                names.update(name.lower() for name in dependencies)
        pubspec_path = project / "pubspec.yaml"
        if pubspec_path.is_symlink():
            raise ValueError(f"dependency manifest symlink forbidden: {pubspec_path}")
        if pubspec_path.is_file():
            pubspec = cast_mapping(
                yaml.safe_load(pubspec_path.read_text(encoding="utf-8")),
                str(pubspec_path),
            )
            for field in ("dependencies", "dev_dependencies"):
                dependencies = cast_mapping(
                    pubspec.get(field, {}), f"{pubspec_path}: {field}"
                )
                names.update(name.lower() for name in dependencies)
                if any(
                    isinstance(requirement, dict)
                    and requirement.get("sdk") == "flutter"
                    for requirement in dependencies.values()
                ):
                    names.add("sdk:flutter")
        return names

    def _managed_prefixes(self) -> tuple[PurePosixPath, ...]:
        return tuple(
            sorted(
                {
                    PurePosixPath(cast(str, cell.path))
                    for cell in self.config.cells.values()
                    if cell.context is ProjectionContext.PROJECT
                    and cell.status is ProjectionStatus.SUPPORTED
                    and cell.surface is not ProjectionSurface.HOOKS
                },
                key=str,
            )
        )

    def _is_managed_evidence(self, project: Path, path: Path) -> bool:
        relative = PurePosixPath(path.relative_to(project).as_posix())
        return any(
            relative == prefix or prefix in relative.parents
            for prefix in self._managed_prefixes()
        )

    def _detector_matches(
        self, project: Path, detector: str, dependencies: set[str]
    ) -> bool:
        parts = detector.split(":", 2)
        if len(parts) != 3:
            raise ValueError(f"invalid project detector: {detector}")
        kind, value = parts[1], parts[2]
        if kind == "marker":
            candidate = _confined(project, value)
            return candidate.exists()
        if kind == "dependency":
            dependency_parts = value.split(":", 1)
            dependency = dependency_parts[-1].lower().replace("_", "-")
            return dependency in dependencies or value.lower() in dependencies
        if kind in {"owned-extension", "extension"}:
            suffix = value if value.startswith(".") else f".{value}"
            for candidate in sorted(project.rglob(f"*{suffix}")):
                if self._is_managed_evidence(project, candidate):
                    continue
                symlink = symlink_component(candidate)
                if symlink is not None:
                    raise ValueError(
                        f"project detector evidence symlink forbidden: {symlink}"
                    )
                if candidate.is_file():
                    return True
            return False
        if kind == "owned-glob":
            for candidate in sorted(project.glob(value)):
                if self._is_managed_evidence(project, candidate):
                    continue
                symlink = symlink_component(candidate)
                if symlink is not None:
                    raise ValueError(
                        f"project detector evidence symlink forbidden: {symlink}"
                    )
                if candidate.exists():
                    return True
            return False
        if kind in {"opt-in", "selected-tag"}:
            return False
        raise ValueError(f"unsupported project detector: {detector}")

    def _activated_skills(
        self,
        project: Path,
        selection: ProjectionSelection,
        dependencies: set[str],
        records: tuple[SkillRecord, ...],
    ) -> dict[str, tuple[str, ...]]:
        conditional = tuple(
            record
            for record in records
            if record.category.conditional and "project" in record.routes
        )
        if selection.project_profile is ProjectProfile.THIRD_PARTY_FORK:
            conditional = tuple(
                record
                for record in conditional
                if record.name in {"deployment-lifecycle", "upstream-fork-maintenance"}
            )
        known_opt_ins = {
            detector.split(":", 2)[2]
            for record in conditional
            for detector in record.detectors
            if detector.startswith("detect:opt-in:")
        }
        known_tags = {
            detector.split(":", 2)[2]
            for record in conditional
            for detector in record.detectors
            if detector.startswith("detect:selected-tag:")
        }
        unknown_opt_ins = set(selection.opt_ins) - known_opt_ins
        if unknown_opt_ins:
            raise ValueError(f"unknown project opt-in: {min(unknown_opt_ins)}")
        unknown_tags = set(selection.selected_tags) - known_tags
        if unknown_tags:
            raise ValueError(f"unknown selected tag: {min(unknown_tags)}")
        activated: dict[str, tuple[str, ...]] = {}
        for record in conditional:
            evidence: set[str] = set()
            for detector in record.detectors:
                kind, value = detector.split(":", 2)[1:]
                if kind == "opt-in":
                    matched = value in selection.opt_ins
                elif kind == "selected-tag":
                    matched = value in selection.selected_tags
                else:
                    matched = self._detector_matches(project, detector, dependencies)
                if matched:
                    evidence.add(detector.removeprefix("detect:"))
            if evidence:
                activated[record.name] = tuple(sorted(evidence))
        return activated

    def _skill_sources(
        self,
        records: tuple[SkillRecord, ...],
        selected: dict[str, tuple[str, ...]],
        local_names: frozenset[str],
        profile: ProjectProfile,
    ) -> tuple[ProjectionSource, ...]:
        activated: dict[str, set[str]] = {
            record.name: {"project-generic"}
            for record in records
            if record.category is SkillCategory.PROJECT_WIDE
            and profile is not ProjectProfile.THIRD_PARTY_FORK
        }
        for name, evidence in selected.items():
            activated[name] = set(evidence)
        sources: list[ProjectionSource] = []
        by_name = {record.name: record for record in records}
        for name in sorted(activated):
            record = by_name[name]
            _validate_source_portability(record.directory, record.activation)
            sources.append(
                ProjectionSource(
                    name,
                    record.directory,
                    "project:skills" if name in local_names else "agents:skills",
                    self.catalog.digest_tree(record.directory),
                    self.catalog.physical_tree_contract(record.directory),
                    "skill",
                    name,
                    tuple(sorted(activated[name])),
                )
            )
        return tuple(sources)

    def _personal_skill_sources(self) -> tuple[ProjectionSource, ...]:
        sources: list[ProjectionSource] = []
        for name in sorted(self.catalog.names_for("personal")):
            record = self.catalog.record(name)
            sources.append(
                ProjectionSource(
                    name,
                    record.directory,
                    "agents:skills",
                    self.catalog.digest_tree(record.directory),
                    self.catalog.physical_tree_contract(record.directory),
                    "skill",
                    name,
                    ("personal",),
                )
            )
        return tuple(sources)

    def _selected_agents(
        self,
        project: Path,
        selection: ProjectionSelection,
        dependencies: set[str],
        profiles: tuple[AgentProfile, ...],
    ) -> dict[str, tuple[str, ...]]:
        project_profiles = {
            profile.name: profile
            for profile in profiles
            if profile.distribution == "project-wide"
        }
        selectable = {
            profile.name
            for profile in project_profiles.values()
            if profile.activation == "opt-in"
        }
        unknown = set(selection.agents) - selectable
        if unknown:
            raise ValueError(f"unknown project agent opt-in: {min(unknown)}")
        selected: dict[str, tuple[str, ...]] = {
            name: (f"opt-in:{name}",) for name in selection.agents
        }
        for profile in project_profiles.values():
            if profile.activation != "detected":
                continue
            evidence = tuple(
                sorted(
                    detector.removeprefix("detect:")
                    for detector in profile.detectors
                    if self._detector_matches(project, detector, dependencies)
                )
            )
            if evidence:
                selected[profile.name] = evidence
        return selected

    @staticmethod
    def _native_name(cell: ProjectionCell, destination: PurePosixPath) -> str:
        assert cell.path is not None
        configured = PurePosixPath(cell.path.removeprefix("${HOME}/"))
        if destination.parent not in {PurePosixPath("."), configured}:
            raise ValueError(
                "adapter destination differs from projection matrix: "
                f"{cell.provider.value}/{cell.surface.value}/{destination}"
            )
        return destination.name

    def _plans(self, authorization: ProjectAuthorization) -> tuple[ProjectionPlan, ...]:
        project = authorization.project
        project_selection = self._selection(authorization)
        local_catalog = (
            Catalog.project(project, self.catalog)
            if project_selection is not None
            and project_selection.project_profile is ProjectProfile.UNCLASSIFIED
            else None
        )
        validate_skill_catalogs(self.catalog, local_catalog)
        local_records = local_catalog.records() if local_catalog is not None else ()
        project_records = tuple(
            record
            for record in (*self.catalog.records(), *local_records)
            if record.category is SkillCategory.PROJECT_WIDE
            or (record.category.conditional and "project" in record.routes)
        )
        local_skill_names = frozenset(record.name for record in local_records)
        dependencies = (
            self._dependencies(project) if project_selection is not None else set()
        )
        project_skills = (
            self._skill_sources(
                project_records,
                self._activated_skills(
                    project,
                    project_selection,
                    dependencies,
                    project_records,
                ),
                local_skill_names,
                project_selection.project_profile,
            )
            if project_selection is not None
            else ()
        )
        personal_skills = self._personal_skill_sources()
        prompt_defense: str | None = None
        token_counter = waza_bpe_counter(self.catalog.root) if self.commands else None
        home = Path.home().resolve(strict=True)
        grouped: dict[tuple[Path, ProjectionContext], dict[str, object]] = {}

        for context in ProjectionContext:
            boundary = home if context is ProjectionContext.PERSONAL else project
            selected_agents: dict[str, tuple[str, ...]]
            if context is ProjectionContext.PERSONAL:
                selection = ProjectionSelection()
                selected_agents = {
                    profile.name: ("always",)
                    for profile in self.agents
                    if profile.distribution == "agent-wide"
                }
            else:
                if project_selection is None:
                    continue
                selection = project_selection
                selected_agents = self._selected_agents(
                    project, project_selection, dependencies, self.agents
                )
            for provider in AgentProvider:
                for surface in ProjectionSurface:
                    if surface is ProjectionSurface.HOOKS:
                        continue
                    cell = self.config.cell(provider, context, surface)
                    if cell.status is ProjectionStatus.UNSUPPORTED:
                        continue
                    if (
                        surface is ProjectionSurface.RULES
                        and cell.layout is RuleLayout.DOCUMENT
                    ):
                        continue
                    assert cell.path is not None
                    configured = cell.path.removeprefix("${HOME}/")
                    root = _confined(boundary, configured)
                    if (
                        context is ProjectionContext.PERSONAL
                        and surface is ProjectionSurface.SKILLS
                        and root == self.catalog.root / "skills"
                    ):
                        continue
                    key = (root, context)
                    if key not in grouped:
                        grouped[key] = {
                            "boundary": boundary,
                            "providers": set(),
                            "selection": selection,
                            "sources": {},
                            "surface": surface,
                        }
                    bucket = grouped[key]
                    if bucket["surface"] is not surface:
                        raise ValueError(
                            f"projection surfaces share one destination: {root}"
                        )
                    cast(set[str], bucket["providers"]).add(provider.value)
                    rendered: list[ProjectionSource] = []
                    if surface is ProjectionSurface.SKILLS:
                        rendered.extend(
                            personal_skills
                            if context is ProjectionContext.PERSONAL
                            else project_skills
                        )
                    elif surface is ProjectionSurface.COMMANDS:
                        if token_counter is None:
                            raise RuntimeError(
                                "supported command surface has no inventory"
                            )
                        budget = CommandTokenBudget(cell.max_tokens, token_counter)
                        route = (
                            CommandRoute.AGENT
                            if context is ProjectionContext.PERSONAL
                            else CommandRoute.PROJECT
                        )
                        for command_spec in self.commands:
                            if command_spec.route is not route:
                                continue
                            command_artifact = render_command(
                                command_spec,
                                CommandProvider(provider.value),
                                token_budget=budget,
                            )
                            rendered.append(
                                _rendered_source(
                                    name=self._native_name(
                                        cell, command_artifact.destination
                                    ),
                                    source=command_spec.path,
                                    origin=f"agents:commands:{provider.value}",
                                    source_type="command",
                                    slug=command_spec.name,
                                    activation=(f"route:{route.value}",),
                                    content=command_artifact.content,
                                    project_portability=(
                                        context is ProjectionContext.PROJECT
                                    ),
                                )
                            )
                    elif surface is ProjectionSurface.AGENTS:
                        if prompt_defense is None:
                            prompt_defense = prompt_defense_body(self.rules)
                        agent_context = AgentContext(context.value)
                        for agent_profile in self.agents:
                            if agent_profile.name not in selected_agents:
                                continue
                            agent_artifact = render_agent(
                                agent_profile,
                                provider,
                                agent_context,
                                prompt_defense=prompt_defense,
                            )
                            rendered.append(
                                _rendered_source(
                                    name=self._native_name(
                                        cell, agent_artifact.destination
                                    ),
                                    source=agent_profile.path,
                                    origin=f"agents:agents:{provider.value}",
                                    source_type="agent",
                                    slug=agent_profile.name,
                                    activation=selected_agents[agent_profile.name],
                                    content=agent_artifact.content,
                                    project_portability=(
                                        context is ProjectionContext.PROJECT
                                    ),
                                )
                            )
                    else:
                        rule_context = RuleContext(context.value)
                        distributions = (
                            {RuleDistribution.BOTH, RuleDistribution.PERSONAL}
                            if context is ProjectionContext.PERSONAL
                            else {RuleDistribution.BOTH, RuleDistribution.PROJECT}
                        )
                        for rule_spec in self.rules:
                            if rule_spec.distribution not in distributions:
                                continue
                            rule_artifact = render_rule(
                                rule_spec,
                                RuleProvider(provider.value),
                                rule_context,
                            )
                            rendered.append(
                                _rendered_source(
                                    name=self._native_name(
                                        cell, rule_artifact.destination
                                    ),
                                    source=rule_spec.path,
                                    origin=f"agents:rules:{provider.value}",
                                    source_type="rule",
                                    slug=rule_spec.identity,
                                    activation=(
                                        f"route:{rule_spec.distribution.value}",
                                    ),
                                    content=rule_artifact.content,
                                    project_portability=(
                                        context is ProjectionContext.PROJECT
                                    ),
                                )
                            )
                    by_name = cast(dict[str, ProjectionSource], bucket["sources"])
                    for source in rendered:
                        previous = by_name.get(source.name)
                        if previous is not None and previous != source:
                            raise ValueError(
                                f"conflicting projection source: {root / source.name}"
                            )
                        by_name[source.name] = source

        project_skill_keys = {
            key: bucket
            for key, bucket in grouped.items()
            if key[1] is ProjectionContext.PROJECT
            and bucket["surface"] is ProjectionSurface.SKILLS
        }
        if project_skill_keys:
            provider_order = {
                provider.value: index for index, provider in enumerate(AgentProvider)
            }
            primary_key = min(
                project_skill_keys,
                key=lambda key: (
                    -len(cast(set[str], project_skill_keys[key]["providers"])),
                    min(
                        provider_order[name]
                        for name in cast(set[str], project_skill_keys[key]["providers"])
                    ),
                ),
            )
            primary_root = primary_key[0]
            primary_sources = cast(
                dict[str, ProjectionSource],
                project_skill_keys[primary_key]["sources"],
            )
            for key, bucket in project_skill_keys.items():
                if key == primary_key:
                    continue
                alias_root = key[0]
                sources = cast(dict[str, ProjectionSource], bucket["sources"])
                if frozenset(sources) != frozenset(primary_sources):
                    raise ValueError(
                        f"project skill surfaces diverge: {alias_root}, {primary_root}"
                    )
                aliased: dict[str, ProjectionSource] = {}
                for name, source in sorted(sources.items()):
                    link = os.path.relpath(primary_root / name, alias_root)
                    aliased[name] = replace(source, link_target=link)
                bucket["sources"] = aliased

        plans = tuple(
            ProjectionPlan(
                cast(Path, bucket["boundary"]),
                root,
                tuple(sorted(cast(set[str], bucket["providers"]))),
                context,
                cast(ProjectionSurface, bucket["surface"]),
                cast(ProjectionSelection, bucket["selection"]),
                tuple(
                    source
                    for _, source in sorted(
                        cast(dict[str, ProjectionSource], bucket["sources"]).items()
                    )
                ),
            )
            for (root, context), bucket in sorted(
                grouped.items(), key=lambda item: (str(item[0][0]), item[0][1].value)
            )
        )
        for index, plan in enumerate(plans):
            for other in plans[index + 1 :]:
                if plan.root in other.root.parents or other.root in plan.root.parents:
                    raise ValueError(
                        f"projection destinations overlap: {plan.root}, {other.root}"
                    )
            local_names = {source.name for source in plan.sources}
            for source in plan.sources:
                if source.content is None:
                    continue
                for match in _MARKDOWN_LINK.finditer(source.content):
                    target = _local_link(match.group(1))
                    if (
                        target is not None
                        and PurePosixPath(target).name not in local_names
                    ):
                        raise ValueError(
                            f"rendered relative link leaves projection surface: {source.source}"
                        )
        return plans

    def _manifest_payload(self, plan: ProjectionPlan) -> dict[str, object]:
        return {
            "version": self.config.projection_manifest_version,
            "owner": "agents-governance",
            "providers": list(plan.providers),
            "context": plan.context.value,
            "surface": plan.surface.value,
            "destination": plan.root.relative_to(plan.project).as_posix(),
            "project": ".",
            "selection": plan.selection.payload(),
            "managed": {source.name: source.metadata() for source in plan.sources},
        }

    def _manifest(self, root: Path) -> dict[str, object] | None:
        path = root / Projector.MANIFEST
        if not path.exists() and not path.is_symlink():
            return None
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"projection manifest must be a physical file: {path}")
        payload = cast_mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
        require_exact_fields(payload, _MANIFEST_FIELDS, str(path))
        version = payload["version"]
        if (
            version
            not in (
                self.config.projection_manifest_version,
                _PRIOR_PROJECTION_MANIFEST_VERSION,
            )
            or payload["owner"] != "agents-governance"
        ):
            raise ValueError(f"projection manifest owner/version is invalid: {path}")
        entry_fields = (
            _ENTRY_FIELDS
            if version == self.config.projection_manifest_version
            else _ENTRY_FIELDS_V5
        )
        if payload["context"] not in {context.value for context in ProjectionContext}:
            raise ValueError(f"projection manifest context is invalid: {path}")
        _strings(payload["providers"], f"{path}: providers")
        if payload["surface"] not in {surface.value for surface in ProjectionSurface}:
            raise ValueError(f"projection manifest surface is invalid: {path}")
        if payload["project"] != ".":
            raise ValueError(f"projection manifest project must equal '.': {path}")
        destination = payload["destination"]
        if not isinstance(destination, str):
            raise TypeError(f"projection manifest destination must be a string: {path}")
        relative = PurePosixPath(destination)
        if (
            relative.is_absolute()
            or relative == PurePosixPath(".")
            or ".." in relative.parts
        ):
            raise ValueError(
                f"projection manifest destination must be project-relative: {path}"
            )
        selection = cast_mapping(payload["selection"], f"{path}: selection")
        require_exact_fields(
            selection,
            frozenset({"agents", "opt_ins", "selected_tags"}),
            f"{path}: selection",
        )
        for field in ("agents", "opt_ins", "selected_tags"):
            _strings(selection[field], f"{path}: selection.{field}")
        managed = cast_mapping(payload["managed"], f"{path}: managed")
        for name, raw in managed.items():
            if Path(name).name != name or not name:
                raise ValueError(
                    f"projection manifest managed name is invalid: {name!r}"
                )
            entry = cast_mapping(raw, f"{path}: managed.{name}")
            require_exact_fields(entry, entry_fields, f"{path}: managed.{name}")
            if entry["adapter_version"] != 1 or entry["destination"] != name:
                raise ValueError(
                    f"projection manifest entry identity is invalid: {name}"
                )
            if entry["source_type"] not in {"agent", "command", "rule", "skill"}:
                raise ValueError(f"projection manifest entry type is invalid: {name}")
            for field in ("origin", "slug"):
                if not isinstance(entry[field], str) or not entry[field]:
                    raise ValueError(
                        f"projection manifest entry {field} is invalid: {name}"
                    )
            link_target = entry.get("link_target")
            if link_target is not None:
                if not isinstance(link_target, str) or not link_target:
                    raise ValueError(
                        f"projection manifest entry link_target is invalid: {name}"
                    )
                portable = PurePosixPath(link_target)
                if portable.is_absolute() or "\\" in link_target or not portable.parts:
                    raise ValueError(
                        f"projection manifest entry link_target is invalid: {name}"
                    )
            for field in ("physical_digest", "source_digest"):
                digest = entry[field]
                if not isinstance(digest, str) or _DIGEST.fullmatch(digest) is None:
                    raise ValueError(
                        f"projection manifest entry {field} is invalid: {name}"
                    )
            activation = _strings(
                entry["activation"], f"{path}: managed.{name}.activation"
            )
            if not activation:
                raise ValueError(
                    f"projection manifest entry activation is empty: {name}"
                )
        return payload

    def _state(self, plan: ProjectionPlan) -> _TargetState:
        root = plan.root
        if symlink_component(root) is not None:
            raise ValueError(f"projection path symlink forbidden: {root}")
        if not root.exists():
            return _TargetState(plan, {}, None, True, {})
        if not root.is_dir():
            raise ValueError(f"projection destination is not a directory: {root}")
        links = {
            source.name: source.link_target
            for source in plan.sources
            if source.link_target is not None
        }
        retired_gc_links = _retired_gc_links(root)
        links.update(retired_gc_links)
        snapshot = _tree_snapshot(root, links)
        payload = self._manifest(root)
        desired = self._manifest_payload(plan)
        previous: dict[str, dict[str, object]] = {}
        drift = payload is None
        if payload is not None:
            for field in (
                "context",
                "destination",
                "owner",
                "project",
                "surface",
            ):
                if payload[field] != desired[field]:
                    raise ValueError(
                        f"projection manifest authority differs at {root}: {field}"
                    )
            previous = cast(dict[str, dict[str, object]], payload["managed"])
            drift = payload != desired or (root / self.MANIFEST).read_text(
                encoding="utf-8"
            ) != self._render_manifest(desired)
        expected = {source.name: source for source in plan.sources}
        for name, source in expected.items():
            destination = root / name
            metadata = previous.get(name)
            if not destination.exists() and not destination.is_symlink():
                drift = True
                continue
            if source.link_target is not None:
                if destination.exists() and not destination.is_symlink():
                    raise ValueError(
                        "unadjudicated projection divergence: "
                        f"destination={destination}; proposed_source={source.source}; "
                        f"source_type={source.source_type}; "
                        f"proposed_origin={source.origin}; "
                        "current_type=physical; "
                        f"proposed_link_target={source.link_target}; "
                        "current_owner=unproven; disposition=preserve current object; "
                        "operator decision required before replacement"
                    )
                if metadata is None or source.metadata() != metadata:
                    drift = True
                continue
            if metadata is None:
                if (
                    not destination.is_symlink()
                    and (destination.is_file() or destination.is_dir())
                ) and (
                    self.catalog.digest_tree(destination) == source.source_digest
                    and self.catalog.physical_tree_contract(destination)
                    == source.physical_digest
                ):
                    drift = True
                    continue
                if destination.is_symlink():
                    observed = "current_type=symlink"
                elif destination.is_file() or destination.is_dir():
                    observed = (
                        "current_logical_digest="
                        f"{self.catalog.digest_tree(destination)}; "
                        "current_physical_digest="
                        f"{self.catalog.physical_tree_contract(destination)}"
                    )
                else:
                    observed = f"current_mode={destination.lstat().st_mode:o}"
                raise ValueError(
                    "unadjudicated projection divergence: "
                    f"destination={destination}; proposed_source={source.source}; "
                    f"source_type={source.source_type}; proposed_origin={source.origin}; "
                    f"{observed}; proposed_logical_digest={source.source_digest}; "
                    f"proposed_physical_digest={source.physical_digest}; "
                    "current_owner=unproven; disposition=preserve current object; "
                    "operator decision required before replacement"
                )
            logical = self.catalog.digest_tree(destination)
            physical = self.catalog.physical_tree_contract(destination)
            if (
                logical != metadata["source_digest"]
                or physical != metadata["physical_digest"]
            ):
                raise ValueError(f"managed projection was modified: {destination}")
            if source.metadata() != metadata:
                drift = True
        for name, metadata in previous.items():
            if name in expected:
                continue
            destination = root / name
            if destination.exists() or destination.is_symlink():
                if destination.is_symlink():
                    raise ValueError(
                        f"stale managed projection was modified: {destination}"
                    )
                logical = self.catalog.digest_tree(destination)
                physical = self.catalog.physical_tree_contract(destination)
                if (
                    logical != metadata["source_digest"]
                    or physical != metadata["physical_digest"]
                ):
                    raise ValueError(
                        f"stale managed projection was modified: {destination}"
                    )
            drift = True
        return _TargetState(
            plan,
            previous,
            snapshot,
            drift or bool(retired_gc_links),
            retired_gc_links,
        )

    @staticmethod
    def _render_manifest(payload: dict[str, object]) -> str:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    def _stage(self, state: _TargetState) -> _StagedTarget:
        plan = state.plan
        links = {
            source.name: source.link_target
            for source in plan.sources
            if source.link_target is not None
        }
        links.update(state.retired_gc_links)
        parent = plan.root.parent
        while not parent.exists():
            parent = parent.parent
        parent.relative_to(plan.project)
        if symlink_component(parent) is not None or not parent.is_dir():
            raise ValueError(f"projection staging parent must be physical: {parent}")
        stage = Path(tempfile.mkdtemp(prefix=".agents-stage.", dir=parent))
        candidate = stage / "candidate"
        backup = stage / "previous"

        def build() -> _StagedTarget:
            if plan.root.exists():
                shutil.copytree(plan.root, candidate, symlinks=True)
                if _tree_snapshot(candidate, links) != state.snapshot:
                    raise RuntimeError(f"projection staging copy differs: {plan.root}")
            else:
                candidate.mkdir()
            for retired in (*state.retired_gc_links, ".gc-skill-ownership.json"):
                destination = candidate / retired
                if destination.exists() or destination.is_symlink():
                    _discard_owned_tree(destination)
            expected = {source.name: source for source in plan.sources}
            for stale in set(state.previous) - set(expected):
                destination = candidate / stale
                if destination.exists() or destination.is_symlink():
                    _discard_owned_tree(destination)
            for source in plan.sources:
                destination = candidate / source.name
                if source.link_target is not None:
                    if destination.exists() or destination.is_symlink():
                        _discard_owned_tree(destination)
                    destination.symlink_to(source.link_target)
                    if os.readlink(destination) != source.link_target:
                        raise RuntimeError(f"staged alias link differs: {destination}")
                    continue
                if (
                    destination.exists()
                    and not destination.is_symlink()
                    and self.catalog.digest_tree(destination) == source.source_digest
                    and self.catalog.physical_tree_contract(destination)
                    == source.physical_digest
                ):
                    continue
                if destination.exists() or destination.is_symlink():
                    _discard_owned_tree(destination)
                if source.content is None:
                    if source.source.is_file():
                        shutil.copy2(source.source, destination, follow_symlinks=False)
                    else:
                        shutil.copytree(source.source, destination, symlinks=True)
                else:
                    destination.write_text(source.content, encoding="utf-8")
                    destination.chmod(0o644)
                if self.catalog.digest_tree(destination) != source.source_digest:
                    raise RuntimeError(
                        f"staged projection digest differs: {destination}"
                    )
                if (
                    self.catalog.physical_tree_contract(destination)
                    != source.physical_digest
                ):
                    raise RuntimeError(
                        f"staged physical contract differs: {destination}"
                    )
            manifest = candidate / self.MANIFEST
            if manifest.exists():
                remove_physical(manifest)
            manifest.write_text(
                self._render_manifest(self._manifest_payload(plan)), encoding="utf-8"
            )
            manifest.chmod(0o644)
            return _StagedTarget(
                state,
                stage,
                candidate,
                backup,
                _tree_snapshot(candidate, links),
            )

        return run_with_cleanup(build, lambda: _discard_owned_tree(stage))

    @staticmethod
    def _create_parent(staged: _StagedTarget) -> None:
        project = staged.state.plan.project
        parent = staged.state.plan.root.parent
        missing: list[Path] = []
        cursor = parent
        while cursor != project and not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        if cursor != project and project not in cursor.parents:
            raise ValueError(f"projection parent escapes project: {parent}")
        symlink = symlink_component(cursor)
        if symlink is not None or not cursor.is_dir():
            raise ValueError(f"projection parent is not physical: {cursor}")
        for directory in reversed(missing):
            directory.mkdir()
            staged.created_parents = (*staged.created_parents, directory)

    def _publish(self, staged: _StagedTarget) -> None:
        plan = staged.state.plan
        links = {
            source.name: source.link_target
            for source in plan.sources
            if source.link_target is not None
        }
        links.update(staged.state.retired_gc_links)
        root = plan.root
        current = (
            _tree_snapshot(root, links) if root.exists() or root.is_symlink() else None
        )
        if current != staged.state.snapshot:
            raise RuntimeError(f"projection changed after preflight: {root}")
        self._create_parent(staged)
        staged.had_root = root.exists()
        if staged.had_root:
            root.replace(staged.backup)
        staged.candidate.replace(root)
        staged.installed = True

    @staticmethod
    def _remove_empty(paths: tuple[Path, ...]) -> None:
        for path in reversed(paths):
            path.rmdir()

    def _rollback(self, staged: _StagedTarget) -> None:
        plan = staged.state.plan
        root = plan.root
        links = {
            source.name: source.link_target
            for source in plan.sources
            if source.link_target is not None
        }
        if staged.installed:
            if not root.exists() and not root.is_symlink():
                raise RuntimeError(
                    f"installed projection disappeared before rollback: {root}"
                )
            if _tree_snapshot(root, links) != staged.candidate_snapshot:
                raise RuntimeError(
                    f"installed projection changed before rollback: {root}"
                )
            _discard_owned_tree(root)
            staged.installed = False
        if staged.backup.exists():
            staged.backup.replace(root)
        self._remove_empty(staged.created_parents)

    def check(self) -> None:
        """Raise on the first project projection defect or drift."""

        project = self.project_root()
        authorization = self.authorize(project)
        for plan in self._plans(authorization):
            if not plan.root.exists():
                continue
            state = self._state(plan)
            if state.drift:
                raise ProjectionDriftError(f"project projection differs: {plan.root}")

    def _prepare_publication(self, state: _TargetState) -> PreparedPublication:
        staged = self._stage(state)
        return PreparedPublication(
            lambda: self._publish(staged),
            lambda: self._rollback(staged),
            lambda: (
                _discard_owned_tree(staged.stage) if staged.stage.exists() else None
            ),
        )

    def publications(
        self, authorization: ProjectAuthorization | None = None
    ) -> tuple[Publication, ...]:
        """Preflight and defer every changed directory publication."""

        selected = (
            self.authorize(self.project_root())
            if authorization is None
            else authorization
        )
        states = tuple(self._state(plan) for plan in self._plans(selected))
        return tuple(
            Publication(partial(self._prepare_publication, state))
            for state in states
            if state.drift
        )

    def apply(self) -> None:
        """Atomically converge every supported surface for the current project."""

        run_atomic_publications(self.publications())


__all__ = ("ProjectionDriftError", "Projector")
