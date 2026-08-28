"""Copy-based, item-scoped projections with no cross-repository links."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from .agent_profiles import (
    AgentArtifact,
    AgentContext,
    AgentProvider,
    AgentRenderError,
    UnsupportedAgent,
    audit_agent_profiles,
    render_agent,
)
from .catalog import NON_PORTABLE_PROJECT_REFERENCE, Catalog
from .commands import (
    CommandArtifact,
    CommandProvider,
    CommandRenderError,
    CommandRoute,
    CommandSpec,
    CommandTokenBudget,
    UnsupportedCommand,
    audit_command_specs,
    render_command,
    waza_bpe_counter,
)
from .projection_config import (
    ProjectionCell,
    ProjectionContext,
    ProjectionStatus,
    ProjectionSurface,
    load_projection_config,
)
from .rule_adapters import (
    RuleArtifact,
    RuleContext,
    RuleProvider,
    RuleRenderError,
    UnsupportedRule,
    render_rule,
)
from .rules import RuleDistribution, audit_rule_specs


@dataclass(frozen=True)
class ProjectionFinding:
    target: str
    path: str
    message: str


@dataclass(frozen=True)
class SourceSkill:
    name: str
    directory: Path
    origin: str
    digest: str
    physical_digest: str
    portable: bool
    problem: str | None = None
    rendered_content: str | None = None
    source_type: str = "skill"
    slug: str | None = None
    adapter_version: int = 1


@dataclass(frozen=True)
class ProjectionPlan:
    """One grouped physical target with complete manifest ownership context."""

    label: str
    root: Path
    providers: tuple[str, ...]
    context: str
    surface: str
    sources: tuple[SourceSkill, ...]


class Projector:
    """Materialize validated copies while rejecting foreign modifications."""

    MANIFEST = ".agents-governance.json"
    _MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog
        self.projection_config = load_projection_config(catalog.root)

    @staticmethod
    def _copy_tree(source: Path, destination: Path) -> None:
        """Copy a tree independently, requesting CoW reflinks on Linux."""

        ancestor = Projector._path_symlink(source)
        if ancestor is not None:
            raise RuntimeError(f"source symlink forbidden: {ancestor}")
        symlink = Projector._tree_symlink(source)
        if symlink is not None:
            raise RuntimeError(f"source symlink forbidden: {symlink}")
        Catalog.physical_tree_contract(source)
        if sys.platform.startswith("linux"):
            subprocess.run(
                [
                    "cp",
                    "--archive",
                    "--reflink=auto",
                    "--no-target-directory",
                    str(source),
                    str(destination),
                ],
                check=True,
            )
            return
        if source.is_file():
            shutil.copy2(source, destination)
        else:
            shutil.copytree(source, destination, symlinks=False)

    @staticmethod
    def _absolute(path: Path) -> Path:
        expanded = os.path.expandvars(str(path.expanduser()))
        return Path(os.path.abspath(expanded))

    @classmethod
    def _expand(cls, value: str) -> Path:
        return cls._absolute(Path(value))

    @classmethod
    def _path_symlink(cls, path: Path) -> Path | None:
        """Return the first symlink component without resolving the path."""

        absolute = cls._absolute(path)
        current = Path(absolute.anchor)
        for part in absolute.parts[1:]:
            current /= part
            if current.is_symlink():
                return current
            if not current.exists():
                break
        return None

    @staticmethod
    def _tree_symlink(path: Path) -> Path | None:
        if path.is_symlink():
            return path
        if not path.is_dir():
            return None
        return next((item for item in path.rglob("*") if item.is_symlink()), None)

    def _safe_contract(self, path: Path) -> tuple[str | None, str | None, str | None]:
        if not path.exists() and not path.is_symlink():
            return None, None, "missing"
        if self._path_symlink(path) is not None:
            return None, None, "symlink"
        symlink = self._tree_symlink(path)
        if symlink is not None:
            return None, None, "symlink"
        if not path.is_file() and not path.is_dir():
            return None, None, "unsupported file type"
        try:
            return (
                self.catalog.digest_tree(path),
                self.catalog.physical_tree_contract(path),
                None,
            )
        except (OSError, ValueError) as error:
            return None, None, str(error)

    def personal_names(self, selected: str | None = None) -> tuple[str, ...]:
        names = tuple(sorted(provider.value for provider in AgentProvider))
        if selected is None:
            return names
        if selected not in names:
            raise ValueError(f"unknown personal target: {selected}")
        return (selected,)

    def _source(self, directory: Path, origin: str, *, portable: bool) -> SourceSkill:
        directory = self._absolute(directory)
        digest, physical_digest, problem = self._safe_contract(directory)
        return SourceSkill(
            directory.name,
            directory,
            origin,
            digest or "",
            physical_digest or "",
            portable,
            problem,
        )

    def _catalog_sources(self, distribution: str) -> tuple[SourceSkill, ...]:
        return tuple(
            self._source(
                self.catalog.record(name).directory,
                f"agents:{distribution}",
                portable=distribution != "personal",
            )
            for name in sorted(self.catalog.names_for(distribution))
        )

    def _command_specs(
        self, label: str
    ) -> tuple[tuple[CommandSpec, ...], list[ProjectionFinding]]:
        audit = audit_command_specs(
            self.catalog.root,
            (directory.name for directory in self.catalog.skill_dirs()),
        )
        findings = [
            ProjectionFinding(label, item.path, f"{item.code}: {item.message}")
            for item in audit.findings
        ]
        return audit.commands, findings

    @staticmethod
    def _rendered_content_digest(name: str, content: str) -> str:
        digest = hashlib.sha256()
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(content.encode())
        digest.update(b"\0")
        return digest.hexdigest()

    @staticmethod
    def _rendered_physical_digest(content: str) -> str:
        digest = hashlib.sha256()
        digest.update(b"file\0.\0")
        digest.update(b"0644\0")
        digest.update(content.encode())
        digest.update(b"\0")
        return digest.hexdigest()

    def _configured_command_budget(
        self, raw_max_tokens: object, label: str
    ) -> CommandTokenBudget:
        if raw_max_tokens is not None and (
            not isinstance(raw_max_tokens, int) or isinstance(raw_max_tokens, bool)
        ):
            raise TypeError(f"invalid command max_tokens for {label}")
        try:
            return CommandTokenBudget(
                raw_max_tokens, waza_bpe_counter(self.catalog.root)
            )
        except ValueError as error:
            raise ValueError(
                f"invalid command max_tokens for {label}: {error}"
            ) from error

    def _rendered_command_source(
        self,
        spec: CommandSpec,
        artifact: CommandArtifact,
        *,
        portable: bool,
    ) -> SourceSkill:
        name = artifact.destination.name
        return SourceSkill(
            name=name,
            directory=spec.path,
            origin=f"agents:commands:{artifact.provider.value}",
            digest=self._rendered_content_digest(name, artifact.content),
            physical_digest=self._rendered_physical_digest(artifact.content),
            portable=portable,
            rendered_content=artifact.content,
            source_type="command",
            slug=spec.name,
        )

    def _render_commands(
        self,
        specs: tuple[CommandSpec, ...],
        provider: CommandProvider,
        route: CommandRoute,
        label: str,
        token_budget: CommandTokenBudget | None,
    ) -> tuple[
        tuple[tuple[CommandSpec, CommandArtifact], ...], list[ProjectionFinding]
    ]:
        rendered: list[tuple[CommandSpec, CommandArtifact]] = []
        findings: list[ProjectionFinding] = []
        if provider is CommandProvider.COPILOT and shutil.which("copilot") is None:
            return (), [
                ProjectionFinding(
                    label,
                    "",
                    "UNSUPPORTED: GitHub Copilot CLI capability is not installed",
                )
            ]
        for spec in specs:
            if spec.route is not route:
                continue
            try:
                result = render_command(spec, provider, token_budget=token_budget)
            except CommandRenderError as error:
                findings.append(ProjectionFinding(label, str(spec.path), str(error)))
                continue
            if isinstance(result, UnsupportedCommand):
                findings.append(ProjectionFinding(label, str(spec.path), result.reason))
                continue
            rendered.append((spec, result))
        return tuple(rendered), findings

    @staticmethod
    def _native_artifact_target(target: Path, destination: Path) -> bool:
        native_parts = destination.parent.parts
        return not native_parts or target.parts[-len(native_parts) :] == native_parts

    def _cell_target(self, cell: ProjectionCell, project: Path | None) -> Path:
        assert cell.path is not None
        if cell.context is ProjectionContext.PERSONAL:
            return self._expand(cell.path)
        if project is None:
            raise ValueError("project projection cell requires a project root")
        return self._confined_project_path(project, cell.path)

    def _command_sources_v4(
        self,
        cell: ProjectionCell,
        target: Path,
        label: str,
    ) -> tuple[tuple[SourceSkill, ...], list[ProjectionFinding]]:
        specs, findings = self._command_specs(label)
        if findings:
            return (), findings
        provider = CommandProvider(cell.provider.value)
        route = (
            CommandRoute.AGENT
            if cell.context is ProjectionContext.PERSONAL
            else CommandRoute.PROJECT
        )
        budget = self._configured_command_budget(cell.max_tokens, label)
        rendered, render_findings = self._render_commands(
            specs, provider, route, label, budget
        )
        findings.extend(render_findings)
        sources: list[SourceSkill] = []
        for spec, artifact in rendered:
            if not self._native_artifact_target(target, Path(artifact.destination)):
                raise ValueError(
                    "command target is not provider-native: "
                    f"{cell.provider.value}/{cell.context.value}"
                )
            sources.append(
                self._rendered_command_source(
                    spec,
                    artifact,
                    portable=cell.context is ProjectionContext.PROJECT,
                )
            )
        return tuple(sources), findings

    def _agent_sources(
        self,
        cell: ProjectionCell,
        target: Path,
        label: str,
    ) -> tuple[tuple[SourceSkill, ...], list[ProjectionFinding]]:
        audit = audit_agent_profiles(self.catalog.root)
        findings = [
            ProjectionFinding(label, item.path, f"{item.code}: {item.message}")
            for item in audit.findings
        ]
        if findings:
            return (), findings
        distribution = (
            "agent-wide"
            if cell.context is ProjectionContext.PERSONAL
            else "project-wide"
        )
        prompt_defense = (
            self.catalog.root / "rules" / "security" / "prompt-defense.md"
        ).read_text(encoding="utf-8")
        sources: list[SourceSkill] = []
        for profile in audit.profiles:
            if profile.distribution != distribution:
                continue
            try:
                rendered = render_agent(
                    profile,
                    AgentProvider(cell.provider.value),
                    AgentContext(cell.context.value),
                    prompt_defense=prompt_defense,
                )
            except AgentRenderError as error:
                findings.append(ProjectionFinding(label, str(profile.path), str(error)))
                continue
            if isinstance(rendered, UnsupportedAgent):
                findings.append(
                    ProjectionFinding(label, str(profile.path), rendered.reason)
                )
                continue
            assert isinstance(rendered, AgentArtifact)
            if not self._native_artifact_target(target, Path(rendered.destination)):
                raise ValueError(
                    "agent target is not provider-native: "
                    f"{cell.provider.value}/{cell.context.value}"
                )
            name = rendered.destination.name
            sources.append(
                SourceSkill(
                    name=name,
                    directory=profile.path,
                    origin=f"agents:agents:{cell.provider.value}",
                    digest=self._rendered_content_digest(name, rendered.content),
                    physical_digest=self._rendered_physical_digest(rendered.content),
                    portable=cell.context is ProjectionContext.PROJECT,
                    rendered_content=rendered.content,
                    source_type="agent",
                    slug=profile.name,
                )
            )
        return tuple(sources), findings

    def _rule_sources(
        self,
        cell: ProjectionCell,
        target: Path,
        label: str,
    ) -> tuple[tuple[SourceSkill, ...], list[ProjectionFinding]]:
        audit = audit_rule_specs(self.catalog.root)
        findings = [
            ProjectionFinding(label, item.path, f"{item.code}: {item.message}")
            for item in audit.findings
        ]
        if findings:
            return (), findings
        accepted = (
            {RuleDistribution.PERSONAL, RuleDistribution.BOTH}
            if cell.context is ProjectionContext.PERSONAL
            else {RuleDistribution.PROJECT, RuleDistribution.BOTH}
        )
        sources: list[SourceSkill] = []
        for spec in audit.rules:
            if spec.distribution not in accepted:
                continue
            try:
                rendered = render_rule(
                    spec,
                    RuleProvider(cell.provider.value),
                    RuleContext(cell.context.value),
                )
            except RuleRenderError as error:
                findings.append(ProjectionFinding(label, str(spec.path), str(error)))
                continue
            if isinstance(rendered, UnsupportedRule):
                findings.append(
                    ProjectionFinding(label, str(spec.path), rendered.reason)
                )
                continue
            assert isinstance(rendered, RuleArtifact)
            if not self._native_artifact_target(target, Path(rendered.destination)):
                raise ValueError(
                    "rule target is not provider-native: "
                    f"{cell.provider.value}/{cell.context.value}"
                )
            name = rendered.destination.name
            sources.append(
                SourceSkill(
                    name=name,
                    directory=spec.path,
                    origin=f"agents:rules:{cell.provider.value}",
                    digest=self._rendered_content_digest(name, rendered.content),
                    physical_digest=self._rendered_physical_digest(rendered.content),
                    portable=cell.context is ProjectionContext.PROJECT,
                    rendered_content=rendered.content,
                    source_type="rule",
                    slug=spec.identity,
                )
            )
        return tuple(sources), findings

    def _sources_for_cell(
        self,
        cell: ProjectionCell,
        target: Path,
        label: str,
        project: Path | None,
    ) -> tuple[tuple[SourceSkill, ...], list[ProjectionFinding]]:
        if cell.surface is ProjectionSurface.SKILLS:
            sources = (
                self._catalog_sources("personal")
                if cell.context is ProjectionContext.PERSONAL
                else self.project_sources(cast(Path, project))
            )
            return sources, []
        if cell.surface is ProjectionSurface.COMMANDS:
            return self._command_sources_v4(cell, target, label)
        if cell.surface is ProjectionSurface.AGENTS:
            return self._agent_sources(cell, target, label)
        return self._rule_sources(cell, target, label)

    def _selected_cells(
        self,
        context: ProjectionContext,
        surface: ProjectionSurface,
        selected_provider: str | None,
    ) -> tuple[tuple[ProjectionCell, ...], list[ProjectionFinding]]:
        providers = (
            (AgentProvider(selected_provider),)
            if selected_provider is not None
            else tuple(AgentProvider)
        )
        cells: list[ProjectionCell] = []
        findings: list[ProjectionFinding] = []
        for provider in providers:
            cell = self.projection_config.cell(provider, context, surface)
            if cell.status is ProjectionStatus.UNSUPPORTED:
                if selected_provider is not None:
                    assert cell.reason is not None
                    findings.append(ProjectionFinding(provider.value, "", cell.reason))
                continue
            cells.append(cell)
        return tuple(cells), findings

    def _plans_for_context(
        self,
        context: ProjectionContext,
        surface: ProjectionSurface,
        projects: tuple[Path, ...],
        selected_provider: str | None,
    ) -> tuple[tuple[ProjectionPlan, ...], list[ProjectionFinding]]:
        cells, findings = self._selected_cells(context, surface, selected_provider)
        roots: tuple[Path | None, ...] = (
            (None,) if context is ProjectionContext.PERSONAL else projects
        )
        grouped: dict[tuple[Path, str, str], dict[str, object]] = {}
        for project in roots:
            for cell in cells:
                target = self._cell_target(cell, project)
                if (
                    context is ProjectionContext.PERSONAL
                    and surface is ProjectionSurface.SKILLS
                    and target == self.catalog.root / "skills"
                ):
                    self.catalog.require_valid()
                    continue
                label = cell.provider.value if project is None else str(project)
                try:
                    sources, source_findings = self._sources_for_cell(
                        cell, target, label, project
                    )
                except (
                    KeyError,
                    OSError,
                    RuntimeError,
                    TypeError,
                    ValueError,
                    tomllib.TOMLDecodeError,
                ) as error:
                    findings.append(ProjectionFinding(label, str(target), str(error)))
                    continue
                findings.extend(source_findings)
                key = (target, context.value, surface.value)
                bucket = grouped.setdefault(key, {"providers": set(), "sources": {}})
                cast(set[str], bucket["providers"]).add(cell.provider.value)
                by_name = cast(dict[str, SourceSkill], bucket["sources"])
                for source in sources:
                    previous = by_name.get(source.name)
                    if previous is not None and previous != source:
                        findings.append(
                            ProjectionFinding(
                                label,
                                str(target / source.name),
                                "conflicting provider projection render",
                            )
                        )
                        continue
                    by_name[source.name] = source
        plans = tuple(
            ProjectionPlan(
                label=str(target),
                root=target,
                providers=tuple(sorted(cast(set[str], bucket["providers"]))),
                context=context_name,
                surface=surface_name,
                sources=tuple(
                    cast(dict[str, SourceSkill], bucket["sources"])[name]
                    for name in sorted(cast(dict[str, SourceSkill], bucket["sources"]))
                ),
            )
            for (target, context_name, surface_name), bucket in sorted(
                grouped.items(), key=lambda item: str(item[0][0])
            )
        )
        return plans, findings

    @staticmethod
    def _manifest(root: Path) -> dict[str, Any]:
        path = root / Projector.MANIFEST
        if not path.exists() and not path.is_symlink():
            return {}
        if path.is_symlink() or not path.is_file():
            raise ValueError("projection manifest must be a physical regular file")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("projection manifest is not valid JSON") from error
        if not isinstance(payload, dict):
            raise TypeError("projection manifest must be an object")
        if payload.get("version") != 4:
            raise ValueError("projection manifest must use version 4")
        expected_root_fields = {
            "context",
            "destination",
            "managed",
            "owner",
            "providers",
            "surface",
            "version",
        }
        if set(payload) != expected_root_fields:
            raise ValueError("projection manifest contains undocumented fields")
        if payload.get("owner") != "agents-governance":
            raise ValueError("projection manifest has an invalid owner")
        providers = payload.get("providers")
        if (
            not isinstance(providers, list)
            or not providers
            or not all(isinstance(provider, str) and provider for provider in providers)
            or providers != sorted(set(providers))
        ):
            raise ValueError("projection manifest providers must be unique and sorted")
        if payload.get("context") not in {
            context.value for context in ProjectionContext
        }:
            raise ValueError("projection manifest has an invalid context")
        if payload.get("surface") not in {
            surface.value for surface in ProjectionSurface
        }:
            raise ValueError("projection manifest has an invalid surface")
        destination = payload.get("destination")
        if not isinstance(destination, str) or not Path(destination).is_absolute():
            raise ValueError("projection manifest destination must be absolute")
        managed = payload.get("managed")
        if not isinstance(managed, dict):
            raise TypeError("projection manifest managed field must be an object")
        validated: dict[str, dict[str, object]] = {}
        entry_fields = {
            "adapter_version",
            "destination",
            "origin",
            "physical_digest",
            "slug",
            "source_digest",
            "source_type",
        }
        for raw_name, raw_metadata in managed.items():
            if (
                not isinstance(raw_name, str)
                or not raw_name
                or Path(raw_name).name != raw_name
            ):
                raise ValueError("projection manifest contains an invalid managed name")
            if not isinstance(raw_metadata, dict) or set(raw_metadata) != entry_fields:
                raise ValueError(
                    f"projection manifest entry {raw_name!r} has invalid fields"
                )
            source_digest = raw_metadata.get("source_digest")
            physical_digest = raw_metadata.get("physical_digest")
            origin = raw_metadata.get("origin")
            if (
                raw_metadata.get("adapter_version") != 1
                or raw_metadata.get("destination") != raw_name
                or not isinstance(source_digest, str)
                or not source_digest
                or not isinstance(physical_digest, str)
                or not physical_digest
                or not isinstance(origin, str)
                or not origin
                or not isinstance(raw_metadata.get("slug"), str)
                or not raw_metadata.get("slug")
                or raw_metadata.get("source_type")
                not in {"agent", "command", "rule", "skill"}
            ):
                raise ValueError(
                    f"projection manifest entry {raw_name!r} has invalid values"
                )
            validated[raw_name] = cast(dict[str, object], raw_metadata)
        return {
            "version": 4,
            "owner": "agents-governance",
            "providers": providers,
            "context": payload["context"],
            "surface": payload["surface"],
            "destination": destination,
            "managed": validated,
        }

    @staticmethod
    def _manifest_payload(plan: ProjectionPlan) -> dict[str, Any]:
        return {
            "version": 4,
            "owner": "agents-governance",
            "providers": list(plan.providers),
            "context": plan.context,
            "surface": plan.surface,
            "destination": str(plan.root),
            "managed": {
                source.name: {
                    "adapter_version": source.adapter_version,
                    "destination": source.name,
                    "origin": source.origin,
                    "physical_digest": source.physical_digest,
                    "slug": source.slug or source.name,
                    "source_digest": source.digest,
                    "source_type": source.source_type,
                }
                for source in plan.sources
            },
        }

    @staticmethod
    def _normalized_dependency(value: str) -> str | None:
        match = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", value)
        return match.group(1).lower().replace("_", "-") if match else None

    @classmethod
    def _pyproject(cls, root: Path) -> dict[str, Any]:
        path = root / "pyproject.toml"
        if path.is_symlink():
            raise ValueError(f"pyproject.toml symlink forbidden: {path}")
        if not path.is_file():
            return {}
        loaded = tomllib.loads(path.read_text(encoding="utf-8"))
        return loaded if isinstance(loaded, dict) else {}

    @classmethod
    def _python_dependencies(cls, loaded: dict[str, Any]) -> set[str]:
        names: set[str] = set()

        def add_values(value: object) -> None:
            if isinstance(value, str):
                normalized = cls._normalized_dependency(value)
                if normalized is not None:
                    names.add(normalized)
            elif isinstance(value, list):
                for item in value:
                    add_values(item)

        project = loaded.get("project", {})
        if isinstance(project, dict):
            add_values(project.get("dependencies", []))
            optional = project.get("optional-dependencies", {})
            if isinstance(optional, dict):
                for dependencies in optional.values():
                    add_values(dependencies)
        groups = loaded.get("dependency-groups", {})
        if isinstance(groups, dict):
            for dependencies in groups.values():
                add_values(dependencies)
        tool = loaded.get("tool", {})
        if isinstance(tool, dict):
            uv = tool.get("uv", {})
            if isinstance(uv, dict):
                add_values(uv.get("dev-dependencies", []))
            poetry = tool.get("poetry", {})
            if isinstance(poetry, dict):
                dependencies = poetry.get("dependencies", {})
                if isinstance(dependencies, dict):
                    names.update(
                        str(name).lower().replace("_", "-")
                        for name in dependencies
                        if str(name).lower() != "python"
                    )
                poetry_groups = poetry.get("group", {})
                if isinstance(poetry_groups, dict):
                    for group in poetry_groups.values():
                        if not isinstance(group, dict):
                            continue
                        group_dependencies = group.get("dependencies", {})
                        if isinstance(group_dependencies, dict):
                            names.update(
                                str(name).lower().replace("_", "-")
                                for name in group_dependencies
                            )
        return names

    @classmethod
    def _dependency_inventory(cls, root: Path) -> dict[str, set[str]]:
        inventory: dict[str, set[str]] = {
            "python": set(),
            "npm": set(),
            "dart": set(),
        }
        loaded = cls._pyproject(root)
        inventory["python"] = cls._python_dependencies(loaded)
        package_json = root / "package.json"
        if package_json.is_symlink():
            raise ValueError(f"package.json symlink forbidden: {package_json}")
        if package_json.is_file():
            package = json.loads(package_json.read_text(encoding="utf-8"))
            if not isinstance(package, dict):
                raise ValueError(f"package.json must contain an object: {package_json}")
            for field in ("dependencies", "devDependencies", "peerDependencies"):
                dependencies = package.get(field, {})
                if not isinstance(dependencies, dict):
                    raise TypeError(f"package.json {field} must be an object")
                inventory["npm"].update(str(name).lower() for name in dependencies)
        pubspec_path = root / "pubspec.yaml"
        if pubspec_path.is_symlink():
            raise ValueError(f"pubspec.yaml symlink forbidden: {pubspec_path}")
        if pubspec_path.is_file():
            try:
                pubspec = yaml.safe_load(pubspec_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as error:
                raise ValueError(f"invalid pubspec.yaml: {pubspec_path}") from error
            if not isinstance(pubspec, dict):
                raise ValueError(f"pubspec.yaml must contain an object: {pubspec_path}")
            for field in ("dependencies", "dev_dependencies"):
                dependencies = pubspec.get(field, {})
                if not isinstance(dependencies, dict):
                    raise TypeError(f"pubspec.yaml {field} must be an object")
                if any(
                    isinstance(requirement, dict)
                    and requirement.get("sdk") == "flutter"
                    for requirement in dependencies.values()
                ):
                    inventory["dart"].add("sdk:flutter")
        return inventory

    @staticmethod
    def _profile_strings(
        profile: dict[str, Any], key: str, capability: str
    ) -> tuple[str, ...]:
        values = profile.get(key, [])
        if not isinstance(values, list) or not all(
            isinstance(value, str) for value in values
        ):
            raise TypeError(f"invalid {key} for project capability {capability}")
        return tuple(values)

    def detected_project_capabilities(self, root: Path) -> tuple[str, ...]:
        """Return tag-derived conditional capabilities proved by project evidence."""

        detected: list[str] = []
        dependency_inventory = self._dependency_inventory(root)
        for capability, profile in self.catalog.conditional_project_profiles().items():
            if not isinstance(profile, dict):
                raise TypeError(f"invalid project capability profile: {capability}")
            markers = self._profile_strings(profile, "markers", capability)
            marker_match = False
            for marker in markers:
                marker_path = Path(marker)
                if (
                    marker_path == Path(".")
                    or marker_path.is_absolute()
                    or ".." in marker_path.parts
                ):
                    raise ValueError(
                        f"project capability marker escapes repository: {capability}"
                    )
                candidate = root / marker_path
                symlink = self._path_symlink(candidate)
                if symlink is not None:
                    raise ValueError(
                        f"project capability marker symlink forbidden: {symlink}"
                    )
                marker_match = marker_match or candidate.exists()
            dependencies = profile.get("dependencies", {})
            if not isinstance(dependencies, dict):
                raise TypeError(
                    f"invalid dependencies for project capability {capability}"
                )
            dependency_match = False
            for ecosystem, expected_dependencies in dependencies.items():
                if ecosystem not in dependency_inventory:
                    raise ValueError(
                        "unknown dependency ecosystem for project capability "
                        f"{capability}: {ecosystem}"
                    )
                if not isinstance(expected_dependencies, list) or not all(
                    isinstance(item, str) for item in expected_dependencies
                ):
                    raise TypeError(
                        f"invalid dependencies for project capability {capability}"
                    )
                normalized = {
                    item.lower().replace("_", "-") for item in expected_dependencies
                }
                dependency_match = dependency_match or bool(
                    normalized & dependency_inventory[ecosystem]
                )

            extension_match = False
            for extension in self._profile_strings(
                profile, "owned_extensions", capability
            ):
                for candidate in root.rglob("*"):
                    relative = candidate.relative_to(root)
                    if not candidate.name.endswith(extension) or relative.parts[0] in {
                        ".agents",
                        ".git",
                    }:
                        continue
                    symlink = self._path_symlink(candidate)
                    if symlink is not None:
                        raise ValueError(
                            f"project capability evidence symlink forbidden: {symlink}"
                        )
                    if candidate.is_file():
                        extension_match = True
                        break
                if extension_match:
                    break

            glob_match = False
            for pattern in self._profile_strings(profile, "owned_globs", capability):
                pattern_path = Path(pattern)
                if (
                    pattern_path == Path(".")
                    or pattern_path.is_absolute()
                    or ".." in pattern_path.parts
                ):
                    raise ValueError(
                        f"project capability glob escapes repository: {capability}"
                    )
                for candidate in root.glob(pattern):
                    relative = candidate.relative_to(root)
                    if not relative.parts or relative.parts[0] in {".agents", ".git"}:
                        continue
                    symlink = self._path_symlink(candidate)
                    if symlink is not None:
                        raise ValueError(
                            f"project capability evidence symlink forbidden: {symlink}"
                        )
                    if candidate.exists():
                        glob_match = True
                        break
                if glob_match:
                    break

            self._profile_strings(profile, "opt_ins", capability)
            self._profile_strings(profile, "selected_tags", capability)
            if marker_match or dependency_match or extension_match or glob_match:
                detected.append(capability)
        return tuple(sorted(detected))

    def _confined_project_path(self, root: Path, configured: object) -> Path:
        if not isinstance(configured, str):
            raise TypeError("project projection path must be a string")
        relative = Path(configured)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("project projection path escapes repository")
        destination = self._absolute(root / relative)
        try:
            destination.relative_to(root)
        except ValueError as error:
            raise ValueError("project projection path escapes repository") from error
        return destination

    def project_sources(self, root: Path) -> tuple[SourceSkill, ...]:
        selected = list(self._catalog_sources("project-generic"))
        for capability in self.detected_project_capabilities(root):
            selected.extend(self._catalog_sources(f"project-capability:{capability}"))
        by_name: dict[str, SourceSkill] = {}
        for source in selected:
            previous = by_name.get(source.name)
            if previous is not None:
                if (
                    previous.digest != source.digest
                    or previous.physical_digest != source.physical_digest
                ):
                    raise RuntimeError(f"conflicting sources for skill {source.name}")
                continue
            by_name[source.name] = source
        return tuple(by_name[name] for name in sorted(by_name))

    def _source_findings(
        self, label: str, source: SourceSkill
    ) -> list[ProjectionFinding]:
        findings: list[ProjectionFinding] = []
        if source.problem is not None:
            message = (
                "source symlink forbidden"
                if source.problem == "symlink"
                else f"invalid source: {source.problem}"
            )
            return [ProjectionFinding(label, str(source.directory), message)]
        if source.rendered_content is not None:
            if source.portable and NON_PORTABLE_PROJECT_REFERENCE.search(
                source.rendered_content
            ):
                findings.append(
                    ProjectionFinding(
                        label,
                        source.name,
                        "cross-repository local path",
                    )
                )
            return findings
        paths = (
            (source.directory,)
            if source.directory.is_file()
            else source.directory.rglob("*")
        )
        for path in paths:
            relative = (
                path.name
                if source.directory.is_file()
                else path.relative_to(source.directory).as_posix()
            )
            if path.is_symlink():
                findings.append(
                    ProjectionFinding(
                        label, f"{source.name}/{relative}", "source symlink forbidden"
                    )
                )
            elif path.is_file():
                text = path.read_text(encoding="utf-8", errors="replace")
                if source.portable and NON_PORTABLE_PROJECT_REFERENCE.search(text):
                    findings.append(
                        ProjectionFinding(
                            label,
                            f"{source.name}/{relative}",
                            "cross-repository local path",
                        )
                    )
                if path.suffix.lower() in {".md", ".mdx"}:
                    for target in self._MARKDOWN_LINK.findall(text):
                        if target.startswith(("http://", "https://", "#", "mailto:")):
                            continue
                        clean = target.split("#", 1)[0]
                        if not clean:
                            continue
                        if source.directory.is_file():
                            findings.append(
                                ProjectionFinding(
                                    label,
                                    f"{source.name}/{relative}",
                                    "cross-repository relative reference",
                                )
                            )
                            continue
                        candidate = self._absolute(path.parent / clean)
                        try:
                            candidate.relative_to(source.directory)
                        except ValueError:
                            findings.append(
                                ProjectionFinding(
                                    label,
                                    f"{source.name}/{relative}",
                                    "cross-repository relative reference",
                                )
                            )
        return findings

    def _preflight(self, plan: ProjectionPlan) -> list[ProjectionFinding]:
        label = plan.label
        root = plan.root
        sources = plan.sources
        findings: list[ProjectionFinding] = []
        if self._path_symlink(root) is not None:
            return [
                ProjectionFinding(label, str(root), "projection path symlink forbidden")
            ]
        if root.exists() and not root.is_dir():
            return [
                ProjectionFinding(
                    label, str(root), "projection root is not a directory"
                )
            ]
        if (root / self.MANIFEST).is_symlink():
            return [
                ProjectionFinding(
                    label,
                    str(root / self.MANIFEST),
                    "destination symlink forbidden",
                )
            ]
        try:
            previous_payload = self._manifest(root)
        except (OSError, TypeError, ValueError) as error:
            return [
                ProjectionFinding(
                    label, str(root / self.MANIFEST), f"invalid manifest: {error}"
                )
            ]
        previous = cast(
            dict[str, dict[str, object]], previous_payload.get("managed", {})
        )
        expected_payload = self._manifest_payload(plan)
        if previous_payload and any(
            previous_payload.get(field) != expected_payload[field]
            for field in (
                "context",
                "destination",
                "owner",
                "providers",
                "surface",
                "version",
            )
        ):
            findings.append(
                ProjectionFinding(
                    label, str(root / self.MANIFEST), "managed manifest update"
                )
            )
        expected = {source.name for source in sources}
        for source in sources:
            findings.extend(self._source_findings(label, source))
            destination = root / source.name
            if not destination.exists() and not destination.is_symlink():
                findings.append(ProjectionFinding(label, str(destination), "missing"))
                continue
            if destination.is_symlink():
                findings.append(
                    ProjectionFinding(
                        label, str(destination), "destination symlink forbidden"
                    )
                )
                continue
            current, current_physical, problem = self._safe_contract(destination)
            if problem == "symlink":
                findings.append(
                    ProjectionFinding(
                        label, str(destination), "destination symlink forbidden"
                    )
                )
                continue
            if problem is not None:
                findings.append(
                    ProjectionFinding(
                        label, str(destination), f"invalid destination: {problem}"
                    )
                )
                continue
            if current == source.digest:
                if current_physical != source.physical_digest:
                    findings.append(
                        ProjectionFinding(
                            label,
                            str(destination),
                            "managed physical update",
                        )
                    )
                expected_metadata = {
                    "adapter_version": source.adapter_version,
                    "destination": source.name,
                    "origin": source.origin,
                    "physical_digest": source.physical_digest,
                    "slug": source.slug or source.name,
                    "source_digest": source.digest,
                    "source_type": source.source_type,
                }
                if previous.get(source.name) != expected_metadata:
                    findings.append(
                        ProjectionFinding(
                            label,
                            str(destination),
                            "managed metadata update",
                        )
                    )
                continue
            if previous.get(source.name, {}).get("source_digest") == current:
                findings.append(
                    ProjectionFinding(label, str(destination), "managed update")
                )
            else:
                findings.append(
                    ProjectionFinding(label, str(destination), "foreign collision")
                )
        for stale, metadata in sorted(previous.items()):
            if stale in expected:
                continue
            destination = root / stale
            if destination.is_symlink() or self._tree_symlink(destination) is not None:
                findings.append(
                    ProjectionFinding(
                        label, str(destination), "destination symlink forbidden"
                    )
                )
                continue
            current, _current_physical, problem = self._safe_contract(destination)
            if problem not in {None, "missing"}:
                findings.append(
                    ProjectionFinding(
                        label, str(destination), f"invalid destination: {problem}"
                    )
                )
            elif current is not None and current != metadata.get("source_digest"):
                findings.append(
                    ProjectionFinding(
                        label, str(destination), "modified stale managed entry"
                    )
                )
            else:
                findings.append(
                    ProjectionFinding(label, str(destination), "stale managed entry")
                )
        if not (root / self.MANIFEST).is_file():
            findings.append(
                ProjectionFinding(label, str(root / self.MANIFEST), "missing manifest")
            )
        return findings

    @staticmethod
    def _remove_managed_tree(path: Path) -> None:
        """Remove a proven managed tree without following nested symlinks."""

        if path.is_symlink():
            raise RuntimeError(f"refusing recursive removal of symlink: {path}")
        for child in path.iterdir():
            if child.is_symlink():
                raise RuntimeError(f"refusing recursive removal of symlink: {child}")
            if child.is_dir():
                Projector._remove_managed_tree(child)
            else:
                child.unlink()
        path.rmdir()

    @classmethod
    def _remove_managed_path(cls, path: Path) -> None:
        """Remove one owned path without following symlinks."""

        if path.is_symlink():
            raise RuntimeError(f"refusing removal of symlink: {path}")
        if path.is_dir():
            cls._remove_managed_tree(path)
        elif path.exists():
            path.unlink()

    @staticmethod
    def _blocking(findings: list[ProjectionFinding]) -> list[ProjectionFinding]:
        reconcilable = {
            "missing",
            "missing manifest",
            "managed update",
            "managed metadata update",
            "managed manifest update",
            "managed physical update",
            "stale managed entry",
        }
        return [finding for finding in findings if finding.message not in reconcilable]

    def _apply_target(self, plan: ProjectionPlan) -> None:
        root = plan.root
        sources = plan.sources
        if self._path_symlink(root) is not None:
            raise RuntimeError(f"projection path symlink forbidden: {root}")
        root.mkdir(parents=True, exist_ok=True)
        previous = cast(
            dict[str, dict[str, object]], self._manifest(root).get("managed", {})
        )
        expected = {source.name for source in sources}
        stale_entries: list[Path] = []
        for stale, metadata in sorted(previous.items()):
            if stale in expected:
                continue
            destination = root / stale
            if destination.is_symlink():
                raise RuntimeError(f"destination symlink forbidden: {destination}")
            current, _current_physical, problem = self._safe_contract(destination)
            if problem == "symlink":
                raise RuntimeError(f"destination symlink forbidden: {destination}")
            if current is not None and current == metadata.get("source_digest"):
                stale_entries.append(destination)

        updates: list[tuple[SourceSkill, Path]] = []
        for source in sources:
            destination = root / source.name
            current, current_physical, problem = self._safe_contract(destination)
            if problem == "symlink":
                raise RuntimeError(f"destination symlink forbidden: {destination}")
            if current == source.digest and current_physical == source.physical_digest:
                continue
            if destination.is_symlink():
                raise RuntimeError(f"destination symlink forbidden: {destination}")
            updates.append((source, destination))

        payload = self._manifest_payload(plan)
        staging = Path(tempfile.mkdtemp(prefix=".agents-stage.", dir=root))
        candidates: list[tuple[Path, Path]] = []
        moved_stale: list[tuple[Path, Path]] = []
        installed: list[tuple[Path, Path | None]] = []
        manifest_destination = root / self.MANIFEST
        manifest_backup: Path | None = None
        manifest_installed = False
        preserve_staging = False
        try:
            for index, (source, destination) in enumerate(updates):
                candidate = staging / f"new-{index}"
                if source.rendered_content is None:
                    self._copy_tree(source.directory, candidate)
                else:
                    candidate.write_text(source.rendered_content, encoding="utf-8")
                    candidate.chmod(0o644)
                if (
                    self.catalog.physical_tree_contract(candidate)
                    != source.physical_digest
                ):
                    raise RuntimeError(
                        f"physical copy contract mismatch for {source.directory}"
                    )
                candidates.append((candidate, destination))

            manifest_candidate = staging / "manifest-new"
            manifest_candidate.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            try:
                for index, destination in enumerate(stale_entries):
                    stale_backup = staging / f"stale-{index}"
                    destination.replace(stale_backup)
                    moved_stale.append((destination, stale_backup))

                for index, (candidate, destination) in enumerate(candidates):
                    update_backup: Path | None = None
                    if destination.exists():
                        update_backup = staging / f"old-{index}"
                        destination.replace(update_backup)
                    try:
                        candidate.replace(destination)
                    except BaseException as failure:
                        if update_backup is not None and update_backup.exists():
                            try:
                                update_backup.replace(destination)
                            except OSError as rollback_error:
                                preserve_staging = True
                                failure.add_note(
                                    f"projection rollback failed: {rollback_error}"
                                )
                        raise
                    installed.append((destination, update_backup))

                if manifest_destination.exists():
                    manifest_backup = staging / "manifest-old"
                    manifest_destination.replace(manifest_backup)
                try:
                    manifest_candidate.replace(manifest_destination)
                    manifest_installed = True
                except BaseException as failure:
                    if manifest_backup is not None and manifest_backup.exists():
                        try:
                            manifest_backup.replace(manifest_destination)
                        except OSError as rollback_error:
                            preserve_staging = True
                            failure.add_note(
                                f"manifest rollback failed: {rollback_error}"
                            )
                    raise
            except BaseException as failure:
                if manifest_installed:
                    try:
                        self._remove_managed_path(manifest_destination)
                        if manifest_backup is not None and manifest_backup.exists():
                            manifest_backup.replace(manifest_destination)
                    except (OSError, RuntimeError) as rollback_error:
                        preserve_staging = True
                        failure.add_note(f"manifest recovery failed: {rollback_error}")
                for installed_destination, installed_backup in reversed(installed):
                    try:
                        self._remove_managed_path(installed_destination)
                        if installed_backup is not None and installed_backup.exists():
                            installed_backup.replace(installed_destination)
                    except (OSError, RuntimeError) as rollback_error:
                        preserve_staging = True
                        failure.add_note(
                            f"installed projection recovery failed: {rollback_error}"
                        )
                for stale_destination, stale_backup in reversed(moved_stale):
                    if stale_backup.exists():
                        try:
                            stale_backup.replace(stale_destination)
                        except OSError as rollback_error:
                            preserve_staging = True
                            failure.add_note(
                                f"stale projection recovery failed: {rollback_error}"
                            )
                raise
        finally:
            if staging.exists() and not preserve_staging:
                self._remove_managed_tree(staging)

    def resolve_projects(
        self, project_roots: tuple[Path, ...], selected: str | None = None
    ) -> tuple[tuple[Path, ...], list[ProjectionFinding]]:
        if not project_roots:
            return (), [
                ProjectionFinding(
                    "projects", "--project-root", "no project roots supplied"
                )
            ]
        projects: list[Path] = []
        findings: list[ProjectionFinding] = []
        seen: set[Path] = set()
        for supplied in project_roots:
            project = self._absolute(supplied)
            if self._path_symlink(project) is not None:
                findings.append(
                    ProjectionFinding(
                        str(supplied), str(project), "project root symlink forbidden"
                    )
                )
                continue
            if not project.is_dir():
                findings.append(
                    ProjectionFinding(
                        str(supplied), str(project), "project root is not a directory"
                    )
                )
                continue
            if (project / ".git").is_symlink():
                findings.append(
                    ProjectionFinding(
                        str(supplied),
                        str(project / ".git"),
                        "Git metadata symlink forbidden",
                    )
                )
                continue
            result = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "--show-toplevel"],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                findings.append(
                    ProjectionFinding(
                        str(supplied),
                        str(project),
                        "project root is not a Git repository",
                    )
                )
                continue
            top_level = self._absolute(Path(result.stdout.strip()))
            if top_level != project:
                findings.append(
                    ProjectionFinding(
                        str(supplied),
                        str(project),
                        "project root is not the exact Git top-level",
                    )
                )
                continue
            if project in seen:
                findings.append(
                    ProjectionFinding(
                        str(supplied), str(project), "duplicate project root"
                    )
                )
                continue
            seen.add(project)
            projects.append(project)
        if findings:
            return (), findings
        if selected is None:
            return tuple(projects), []
        matches = [
            project for project in projects if selected in {project.name, str(project)}
        ]
        if not matches:
            return (), [
                ProjectionFinding(selected, "", "unknown project projection target")
            ]
        if len(matches) != 1:
            return (), [
                ProjectionFinding(selected, "", "ambiguous project projection target")
            ]
        return (matches[0],), []

    def check(
        self,
        scope: str,
        selected: str | None = None,
        surface: str = "skills",
        project_roots: tuple[Path, ...] = (),
        *,
        provider: str | None = None,
    ) -> list[ProjectionFinding]:
        if surface == "all":
            return [
                item
                for name in ("skills", "commands", "agents", "rules")
                for item in self.check(
                    scope,
                    selected,
                    name,
                    project_roots,
                    provider=provider,
                )
            ]
        try:
            selected_surface = ProjectionSurface(surface)
        except ValueError:
            raise ValueError(f"unknown projection surface: {surface}")
        findings: list[ProjectionFinding] = []
        if scope == "personal":
            if project_roots:
                return [
                    ProjectionFinding(
                        "", "", "project roots are invalid for personal scope"
                    )
                ]
            if selected is not None and provider is not None and selected != provider:
                return [
                    ProjectionFinding(
                        selected,
                        "",
                        "personal --target and --provider must select the same provider",
                    )
                ]
            selected_provider = provider or selected
            try:
                plans, plan_findings = self._plans_for_context(
                    ProjectionContext.PERSONAL,
                    selected_surface,
                    (),
                    selected_provider,
                )
            except ValueError as error:
                return [
                    ProjectionFinding(selected_provider or "personal", "", str(error))
                ]
            findings.extend(plan_findings)
            for plan in plans:
                findings.extend(self._preflight(plan))
            return findings
        if scope != "projects":
            raise ValueError(f"unknown projection scope: {scope}")
        projects, project_findings = self.resolve_projects(project_roots, selected)
        if project_findings:
            return project_findings
        try:
            plans, plan_findings = self._plans_for_context(
                ProjectionContext.PROJECT,
                selected_surface,
                projects,
                provider,
            )
        except ValueError as error:
            return [ProjectionFinding(provider or "projects", "", str(error))]
        findings.extend(plan_findings)
        for plan in plans:
            findings.extend(self._preflight(plan))
        return findings

    def apply(
        self,
        scope: str,
        selected: str | None = None,
        surface: str = "skills",
        project_roots: tuple[Path, ...] = (),
        *,
        provider: str | None = None,
    ) -> list[ProjectionFinding]:
        if surface == "all":
            findings = self.check(
                scope, selected, surface, project_roots, provider=provider
            )
            blocking = self._blocking(findings)
            if blocking:
                return blocking
            for name in ("skills", "commands", "agents", "rules"):
                child_findings = self.apply(
                    scope,
                    selected,
                    name,
                    project_roots,
                    provider=provider,
                )
                if child_findings:
                    return child_findings
            return []
        findings = self.check(
            scope, selected, surface, project_roots, provider=provider
        )
        blocking = self._blocking(findings)
        if blocking:
            return blocking
        selected_surface = ProjectionSurface(surface)
        if scope == "personal":
            selected_provider = provider or selected
            plans, plan_findings = self._plans_for_context(
                ProjectionContext.PERSONAL,
                selected_surface,
                (),
                selected_provider,
            )
        else:
            projects, project_findings = self.resolve_projects(project_roots, selected)
            if project_findings:
                return project_findings
            plans, plan_findings = self._plans_for_context(
                ProjectionContext.PROJECT,
                selected_surface,
                projects,
                provider,
            )
        if plan_findings:
            return plan_findings
        for plan in plans:
            self._apply_target(plan)
        return []
