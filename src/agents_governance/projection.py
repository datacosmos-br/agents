"""Strict directory-surface projection with atomic physical publication."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import tomllib
from dataclasses import dataclass
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
from .catalog import NON_PORTABLE_PROJECT_REFERENCE, Catalog
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
from .projection_authorization import (
    PROJECT_SELECTION,
    ProjectAuthorization,
    load_project_authorization,
)
from .projection_config import (
    ProjectionCell,
    ProjectionConfig,
    ProjectionContext,
    ProjectionStatus,
    ProjectionSurface,
    RuleLayout,
)
from .rule_adapters import RuleContext, RuleProvider, render_rule
from .rules import RuleDistribution, RuleSpec

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
_SELECTION_FIELDS = frozenset({"agents", "opt_ins", "selected_tags", "version"})
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
        "origin",
        "physical_digest",
        "slug",
        "source_digest",
        "source_type",
    }
)


class ProjectionDriftError(RuntimeError):
    """The project projection differs from its canonical source."""


@dataclass(frozen=True)
class ProjectionSelection:
    agents: tuple[str, ...] = ()
    opt_ins: tuple[str, ...] = ()
    selected_tags: tuple[str, ...] = ()

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

    def metadata(self) -> dict[str, object]:
        return {
            "activation": list(self.activation),
            "adapter_version": self.adapter_version,
            "destination": self.name,
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


def _mapping(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{context} must be an object with string keys")
    return cast(dict[str, object], value)


def _exact(value: dict[str, object], fields: frozenset[str], context: str) -> None:
    if frozenset(value) != fields:
        raise ValueError(
            f"{context} fields must equal {', '.join(sorted(fields))}; "
            f"got {', '.join(sorted(value)) or 'none'}"
        )


def _strings(value: object, context: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item and item == item.strip() for item in value
    ):
        raise TypeError(f"{context} must be an array of non-empty trimmed strings")
    selected = tuple(cast(list[str], value))
    if selected != tuple(sorted(set(selected))):
        raise ValueError(f"{context} must be unique and sorted")
    return selected


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def _symlink_component(path: Path) -> Path | None:
    absolute = _absolute(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        if current.is_symlink():
            return current
        if not current.exists():
            break
    return None


def _tree_snapshot(root: Path) -> str:
    """Digest one physical destination tree and reject every symlink."""

    digest = hashlib.sha256()

    def visit(path: Path) -> None:
        metadata = path.lstat()
        relative = path.relative_to(root).as_posix() if path != root else "."
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(f"{stat.S_IMODE(metadata.st_mode):04o}".encode())
        digest.update(b"\0")
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"projection destination symlink forbidden: {path}")
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


def _physical_project(cwd: Path) -> Path:
    current = _absolute(cwd)
    if _symlink_component(current) is not None or not current.is_dir():
        raise ValueError(f"invocation directory must be physical: {current}")
    for candidate in (current, *current.parents):
        git = candidate / ".git"
        if git.is_symlink():
            raise ValueError(f"Git metadata symlink forbidden: {git}")
        if git.exists():
            if not git.is_dir() or not stat.S_ISDIR(git.lstat().st_mode):
                raise ValueError(
                    f"project must own a physical .git directory: {candidate}"
                )
            project = candidate.resolve(strict=True)
            if project == Path("/tmp") or Path("/tmp") in project.parents:
                raise ValueError(f"repositories under /tmp are prohibited: {project}")
            return project
    raise ValueError(
        f"invocation directory is not inside a physical Git project: {cwd}"
    )


def _confined(project: Path, raw: str) -> Path:
    relative = Path(raw)
    if relative.is_absolute() or relative == Path(".") or ".." in relative.parts:
        raise ValueError(f"project projection path escapes repository: {raw}")
    target = _absolute(project / relative)
    target.relative_to(project)
    symlink = _symlink_component(target)
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


def _validate_source_portability(source: Path) -> None:
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
            candidate = _absolute(path.parent / target)
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
    def _selection(
        authorization: ProjectAuthorization,
    ) -> ProjectionSelection | None:
        if authorization.payload is None:
            return None
        path = authorization.path
        payload = _mapping(json.loads(authorization.payload), str(path))
        _exact(payload, _SELECTION_FIELDS, str(path))
        if payload["version"] != 1:
            raise ValueError(f"projection selection version must equal 1: {path}")
        return ProjectionSelection(
            _strings(payload["agents"], f"{path}: agents"),
            _strings(payload["opt_ins"], f"{path}: opt_ins"),
            _strings(payload["selected_tags"], f"{path}: selected_tags"),
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
            loaded = _mapping(
                tomllib.loads(pyproject.read_text(encoding="utf-8")), str(pyproject)
            )

            if "project" in loaded:
                project_table = _mapping(loaded["project"], f"{pyproject}: project")
                add_requirements(
                    project_table.get("dependencies", []),
                    f"{pyproject}: project.dependencies",
                )
                optional = _mapping(
                    project_table.get("optional-dependencies", {}),
                    f"{pyproject}: project.optional-dependencies",
                )
                for optional_name, raw in optional.items():
                    add_requirements(
                        raw,
                        f"{pyproject}: project.optional-dependencies.{optional_name}",
                    )
            groups = _mapping(
                loaded.get("dependency-groups", {}),
                f"{pyproject}: dependency-groups",
            )
            for dependency_group_name, raw in groups.items():
                add_requirements(
                    raw,
                    f"{pyproject}: dependency-groups.{dependency_group_name}",
                )
            tool = _mapping(loaded.get("tool", {}), f"{pyproject}: tool")
            if "poetry" in tool:
                poetry = _mapping(tool["poetry"], f"{pyproject}: tool.poetry")
                direct = _mapping(
                    poetry.get("dependencies", {}),
                    f"{pyproject}: tool.poetry.dependencies",
                )
                names.update(
                    name.lower().replace("_", "-")
                    for name in direct
                    if name.lower() != "python"
                )
                poetry_groups = _mapping(
                    poetry.get("group", {}), f"{pyproject}: tool.poetry.group"
                )
                for group_name, raw_group in poetry_groups.items():
                    poetry_group = _mapping(
                        raw_group,
                        f"{pyproject}: tool.poetry.group.{group_name}",
                    )
                    group_dependencies = _mapping(
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
            package = _mapping(
                json.loads(package_path.read_text(encoding="utf-8")), str(package_path)
            )
            for field in ("dependencies", "devDependencies", "peerDependencies"):
                dependencies = _mapping(
                    package.get(field, {}), f"{package_path}: {field}"
                )
                names.update(name.lower() for name in dependencies)
        pubspec_path = project / "pubspec.yaml"
        if pubspec_path.is_symlink():
            raise ValueError(f"dependency manifest symlink forbidden: {pubspec_path}")
        if pubspec_path.is_file():
            pubspec = _mapping(
                yaml.safe_load(pubspec_path.read_text(encoding="utf-8")),
                str(pubspec_path),
            )
            for field in ("dependencies", "dev_dependencies"):
                dependencies = _mapping(
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
                symlink = _symlink_component(candidate)
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
                symlink = _symlink_component(candidate)
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
    ) -> dict[str, tuple[str, ...]]:
        records = tuple(
            record
            for record in self.catalog.records()
            if record.category.conditional and record.route == "project"
        )
        known_opt_ins = {
            detector.split(":", 2)[2]
            for record in records
            for detector in record.detectors
            if detector.startswith("detect:opt-in:")
        }
        known_tags = {
            detector.split(":", 2)[2]
            for record in records
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
        for record in records:
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
        self, selected: dict[str, tuple[str, ...]]
    ) -> tuple[ProjectionSource, ...]:
        activated: dict[str, set[str]] = {
            name: {"project-generic"}
            for name in self.catalog.names_for("project-generic")
        }
        for name, evidence in selected.items():
            activated[name] = set(evidence)
        sources: list[ProjectionSource] = []
        for name in sorted(activated):
            record = self.catalog.record(name)
            _validate_source_portability(record.directory)
            sources.append(
                ProjectionSource(
                    name,
                    record.directory,
                    "agents:skills",
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
        dependencies = (
            self._dependencies(project) if project_selection is not None else set()
        )
        project_skills = (
            self._skill_sources(
                self._activated_skills(project, project_selection, dependencies)
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
                            prompt_defense = (
                                self.catalog.root
                                / "rules"
                                / "security"
                                / "prompt-defense.md"
                            ).read_text(encoding="utf-8")
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
        payload = _mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
        _exact(payload, _MANIFEST_FIELDS, str(path))
        if (
            payload["version"] != self.config.projection_manifest_version
            or payload["owner"] != "agents-governance"
        ):
            raise ValueError(f"projection manifest owner/version is invalid: {path}")
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
        selection = _mapping(payload["selection"], f"{path}: selection")
        _exact(
            selection,
            frozenset({"agents", "opt_ins", "selected_tags"}),
            f"{path}: selection",
        )
        for field in ("agents", "opt_ins", "selected_tags"):
            _strings(selection[field], f"{path}: selection.{field}")
        managed = _mapping(payload["managed"], f"{path}: managed")
        for name, raw in managed.items():
            if Path(name).name != name or not name:
                raise ValueError(
                    f"projection manifest managed name is invalid: {name!r}"
                )
            entry = _mapping(raw, f"{path}: managed.{name}")
            _exact(entry, _ENTRY_FIELDS, f"{path}: managed.{name}")
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
        if _symlink_component(root) is not None:
            raise ValueError(f"projection path symlink forbidden: {root}")
        if not root.exists():
            return _TargetState(plan, {}, None, True)
        if not root.is_dir():
            raise ValueError(f"projection destination is not a directory: {root}")
        snapshot = _tree_snapshot(root)
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
                "version",
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
        return _TargetState(plan, previous, snapshot, drift)

    @staticmethod
    def _render_manifest(payload: dict[str, object]) -> str:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    def _stage(self, state: _TargetState) -> _StagedTarget:
        plan = state.plan
        parent = plan.root.parent
        while not parent.exists():
            parent = parent.parent
        parent.relative_to(plan.project)
        if _symlink_component(parent) is not None or not parent.is_dir():
            raise ValueError(f"projection staging parent must be physical: {parent}")
        stage = Path(tempfile.mkdtemp(prefix=".agents-stage.", dir=parent))
        candidate = stage / "candidate"
        backup = stage / "previous"

        def build() -> _StagedTarget:
            if plan.root.exists():
                shutil.copytree(plan.root, candidate, symlinks=True)
                if _tree_snapshot(candidate) != state.snapshot:
                    raise RuntimeError(f"projection staging copy differs: {plan.root}")
            else:
                candidate.mkdir()
            expected = {source.name: source for source in plan.sources}
            for stale in set(state.previous) - set(expected):
                destination = candidate / stale
                if destination.exists() or destination.is_symlink():
                    _discard_owned_tree(destination)
            for source in plan.sources:
                destination = candidate / source.name
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
                _tree_snapshot(candidate),
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
        symlink = _symlink_component(cursor)
        if symlink is not None or not cursor.is_dir():
            raise ValueError(f"projection parent is not physical: {cursor}")
        for directory in reversed(missing):
            directory.mkdir()
            staged.created_parents = (*staged.created_parents, directory)

    def _publish(self, staged: _StagedTarget) -> None:
        root = staged.state.plan.root
        current = _tree_snapshot(root) if root.exists() or root.is_symlink() else None
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
        root = staged.state.plan.root
        if staged.installed:
            if not root.exists() and not root.is_symlink():
                raise RuntimeError(
                    f"installed projection disappeared before rollback: {root}"
                )
            if _tree_snapshot(root) != staged.candidate_snapshot:
                raise RuntimeError(
                    f"installed projection changed before rollback: {root}"
                )
            remove_physical(root)
            staged.installed = False
        if staged.backup.exists():
            staged.backup.replace(root)
        self._remove_empty(staged.created_parents)

    def check(self) -> None:
        """Raise on the first project projection defect or drift."""

        project = self.project_root()
        authorization = load_project_authorization(project)
        for plan in self._plans(authorization):
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
            load_project_authorization(self.project_root())
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
