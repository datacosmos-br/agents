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
from typing import Any

import yaml

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


class Projector:
    """Materialize validated copies while rejecting foreign modifications."""

    MANIFEST = ".agents-governance.json"
    _MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog
        config = catalog.root / "config" / "projections.json"
        self.config: dict[str, Any] = json.loads(config.read_text(encoding="utf-8"))

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
        names = tuple(sorted(self.config["personal_targets"]))
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

    def _surface_sources(
        self, surface: str, distribution: str
    ) -> tuple[SourceSkill, ...]:
        if surface == "skills":
            return self._catalog_sources(distribution)
        if surface == "commands":
            raise ValueError("commands require a provider-native adapter")
        root = self.catalog.root / surface
        distribution_key = distribution.replace("-", "_")
        entries = self.config["surfaces"][surface][distribution_key]["entries"]
        if not isinstance(entries, list) or not all(
            isinstance(entry, str) for entry in entries
        ):
            raise TypeError(
                f"invalid {surface} entries for distribution {distribution_key}"
            )
        return tuple(
            self._source(
                root / name,
                f"agents:{surface}",
                portable=distribution != "personal",
            )
            for name in entries
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

    @staticmethod
    def _command_adapter_identity(provider: CommandProvider) -> CommandProvider:
        if provider is CommandProvider.COPILOT:
            return CommandProvider.CLAUDE
        return provider

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
        adapter = self._command_adapter_identity(artifact.provider)
        return SourceSkill(
            name=name,
            directory=spec.path,
            origin=f"agents:commands:{adapter.value}",
            digest=self._rendered_content_digest(name, artifact.content),
            physical_digest=self._rendered_physical_digest(artifact.content),
            portable=portable,
            rendered_content=artifact.content,
        )

    @staticmethod
    def _native_command_target(target: Path, artifact: CommandArtifact) -> bool:
        native_parts = artifact.destination.parent.parts
        return not native_parts or target.parts[-len(native_parts) :] == native_parts

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
    def _merge_command_sources(
        grouped: dict[Path, dict[str, SourceSkill]],
        target: Path,
        sources: tuple[SourceSkill, ...],
    ) -> None:
        bucket = grouped.setdefault(target, {})
        for source in sources:
            previous = bucket.get(source.name)
            if previous is not None and previous != source:
                raise RuntimeError(
                    f"conflicting provider command render: {target / source.name}"
                )
            bucket[source.name] = source

    def _personal_command_projections(
        self, selected: str | None
    ) -> tuple[
        tuple[tuple[str, Path, tuple[SourceSkill, ...]], ...],
        list[ProjectionFinding],
    ]:
        specs, findings = self._command_specs("commands")
        if findings:
            return (), findings
        grouped: dict[Path, dict[str, SourceSkill]] = {}
        labels: dict[Path, set[str]] = {}
        for name in self.personal_names(selected):
            configured = self.config["personal_targets"][name]
            raw_commands = configured.get("commands")
            raw_provider: object = name
            raw_path: object | None = None
            raw_max_tokens: object = None
            if raw_commands is not None:
                if (
                    not isinstance(raw_commands, dict)
                    or not {"path", "provider"}.issubset(raw_commands)
                    or set(raw_commands) - {"max_tokens", "path", "provider"}
                ):
                    raise TypeError(
                        f"invalid personal command target configuration: {name}"
                    )
                raw_provider = raw_commands["provider"]
                raw_path = raw_commands["path"]
                raw_max_tokens = raw_commands.get("max_tokens")
            if not isinstance(raw_provider, str):
                findings.append(
                    ProjectionFinding(
                        name,
                        "",
                        f"UNSUPPORTED: unknown command provider {raw_provider!r}",
                    )
                )
                continue
            try:
                provider = CommandProvider(raw_provider)
            except ValueError:
                findings.append(
                    ProjectionFinding(
                        name,
                        "",
                        f"UNSUPPORTED: unknown command provider {raw_provider!r}",
                    )
                )
                continue
            token_budget = self._configured_command_budget(raw_max_tokens, name)
            rendered, provider_findings = self._render_commands(
                specs,
                provider,
                CommandRoute.AGENT,
                name,
                token_budget,
            )
            findings.extend(provider_findings)
            if raw_path is None:
                if rendered:
                    findings.append(
                        ProjectionFinding(
                            name,
                            "",
                            "UNSUPPORTED: personal command destination is not configured",
                        )
                    )
                continue
            if not isinstance(raw_path, str):
                raise TypeError(f"invalid personal command target path: {name}")
            target = self._expand(raw_path)
            for _spec, artifact in rendered:
                if not self._native_command_target(target, artifact):
                    raise ValueError(
                        f"personal command target is not provider-native: {name}"
                    )
            sources = tuple(
                self._rendered_command_source(spec, artifact, portable=False)
                for spec, artifact in rendered
            )
            self._merge_command_sources(grouped, target, sources)
            labels.setdefault(target, set()).add(name)
        projections = tuple(
            (
                "+".join(sorted(labels[target])),
                target,
                tuple(grouped[target][name] for name in sorted(grouped[target])),
            )
            for target in sorted(grouped, key=str)
        )
        return projections, findings

    def _project_command_projections(
        self, project: Path
    ) -> tuple[
        tuple[tuple[str, Path, tuple[SourceSkill, ...]], ...],
        list[ProjectionFinding],
    ]:
        label = str(project)
        specs, findings = self._command_specs(label)
        if findings:
            return (), findings
        configured = self.config["projects"].get("command_targets")
        if not isinstance(configured, dict) or not configured:
            raise TypeError("project command_targets must be a non-empty object")
        grouped: dict[Path, dict[str, SourceSkill]] = {}
        labels: dict[Path, set[str]] = {}
        for raw_provider, raw_target in sorted(configured.items()):
            try:
                provider = CommandProvider(raw_provider)
            except (TypeError, ValueError):
                findings.append(
                    ProjectionFinding(
                        label,
                        "",
                        f"UNSUPPORTED: unknown command provider {raw_provider!r}",
                    )
                )
                continue
            if (
                not isinstance(raw_target, dict)
                or "path" not in raw_target
                or set(raw_target) - {"max_tokens", "path"}
            ):
                raise TypeError(
                    f"invalid project command target configuration: {raw_provider}"
                )
            raw_path = raw_target["path"]
            if not isinstance(raw_path, str):
                raise TypeError(f"invalid project command target path: {raw_provider}")
            target = self._confined_project_path(project, raw_path)
            token_budget = self._configured_command_budget(
                raw_target.get("max_tokens"), str(raw_provider)
            )
            rendered, provider_findings = self._render_commands(
                specs,
                provider,
                CommandRoute.PROJECT,
                label,
                token_budget,
            )
            findings.extend(provider_findings)
            for _spec, artifact in rendered:
                if not self._native_command_target(target, artifact):
                    raise ValueError(
                        f"project command target is not provider-native: {raw_provider}"
                    )
            sources = tuple(
                self._rendered_command_source(spec, artifact, portable=True)
                for spec, artifact in rendered
            )
            self._merge_command_sources(grouped, target, sources)
            labels.setdefault(target, set()).add(str(raw_provider))
        projections = tuple(
            (
                f"{label}:{'+'.join(sorted(labels[target]))}",
                target,
                tuple(grouped[target][name] for name in sorted(grouped[target])),
            )
            for target in sorted(grouped, key=str)
        )
        return projections, findings

    @staticmethod
    def _manifest(root: Path) -> dict[str, dict[str, str]]:
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
        if payload.get("version") != 2:
            raise ValueError("projection manifest must use version 2")
        if set(payload) != {"managed", "version"}:
            raise ValueError("projection manifest contains undocumented fields")
        managed = payload.get("managed")
        if not isinstance(managed, dict):
            raise TypeError("projection manifest managed field must be an object")
        validated: dict[str, dict[str, str]] = {}
        for raw_name, raw_metadata in managed.items():
            if (
                not isinstance(raw_name, str)
                or not raw_name
                or Path(raw_name).name != raw_name
            ):
                raise ValueError("projection manifest contains an invalid managed name")
            if not isinstance(raw_metadata, dict) or set(raw_metadata) != {
                "digest",
                "origin",
            }:
                raise ValueError(
                    f"projection manifest entry {raw_name!r} has invalid fields"
                )
            digest = raw_metadata.get("digest")
            origin = raw_metadata.get("origin")
            if (
                not isinstance(digest, str)
                or not digest
                or not isinstance(origin, str)
                or not origin
            ):
                raise ValueError(
                    f"projection manifest entry {raw_name!r} has invalid values"
                )
            validated[raw_name] = {"digest": digest, "origin": origin}
        return validated

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

    def _preflight(
        self, label: str, root: Path, sources: tuple[SourceSkill, ...]
    ) -> list[ProjectionFinding]:
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
            previous = self._manifest(root)
        except (OSError, TypeError, ValueError) as error:
            return [
                ProjectionFinding(
                    label, str(root / self.MANIFEST), f"invalid manifest: {error}"
                )
            ]
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
                    "digest": source.digest,
                    "origin": source.origin,
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
            if previous.get(source.name, {}).get("digest") == current:
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
            elif current is not None and current != metadata.get("digest"):
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
            "managed physical update",
            "stale managed entry",
        }
        return [finding for finding in findings if finding.message not in reconcilable]

    def _apply_target(self, root: Path, sources: tuple[SourceSkill, ...]) -> None:
        if self._path_symlink(root) is not None:
            raise RuntimeError(f"projection path symlink forbidden: {root}")
        root.mkdir(parents=True, exist_ok=True)
        previous = self._manifest(root)
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
            if current is not None and current == metadata.get("digest"):
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

        payload = {
            "version": 2,
            "managed": {
                source.name: {"digest": source.digest, "origin": source.origin}
                for source in sources
            },
        }
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

    def _project_target(
        self, project: Path, surface: str
    ) -> tuple[Path | None, ProjectionFinding | None]:
        try:
            target = self._confined_project_path(
                project, self.config["projects"][f"{surface}_path"]
            )
        except (KeyError, TypeError, ValueError) as error:
            return None, ProjectionFinding(str(project), str(project), str(error))
        if self._path_symlink(target) is not None:
            return None, ProjectionFinding(
                str(project), str(target), "projection path symlink forbidden"
            )
        return target, None

    def check(
        self,
        scope: str,
        selected: str | None = None,
        surface: str = "skills",
        project_roots: tuple[Path, ...] = (),
    ) -> list[ProjectionFinding]:
        findings: list[ProjectionFinding] = []
        if surface == "all":
            return [
                item
                for name in ("skills", "commands", "rules")
                for item in self.check(scope, selected, name, project_roots)
            ]
        if surface not in {"skills", "commands", "rules"}:
            raise ValueError(f"unknown projection surface: {surface}")
        if scope == "personal":
            if project_roots:
                return [
                    ProjectionFinding(
                        "", "", "project roots are invalid for personal scope"
                    )
                ]
            if surface == "commands":
                try:
                    projections, command_findings = self._personal_command_projections(
                        selected
                    )
                except (
                    KeyError,
                    OSError,
                    RuntimeError,
                    TypeError,
                    ValueError,
                ) as error:
                    return [ProjectionFinding("commands", "", str(error))]
                findings.extend(command_findings)
                for label, target, sources in projections:
                    findings.extend(self._preflight(label, target, sources))
                return findings
            for name in self.personal_names(selected):
                configured = self.config["personal_targets"][name]
                if surface not in configured:
                    continue
                target = self._expand(configured[surface])
                findings.extend(
                    self._preflight(
                        name, target, self._surface_sources(surface, "personal")
                    )
                )
            return findings
        if scope != "projects":
            raise ValueError(f"unknown projection scope: {scope}")
        projects, project_findings = self.resolve_projects(project_roots, selected)
        if project_findings:
            return project_findings
        if surface == "commands":
            for project in projects:
                try:
                    projections, command_findings = self._project_command_projections(
                        project
                    )
                except (
                    KeyError,
                    OSError,
                    RuntimeError,
                    TypeError,
                    ValueError,
                ) as error:
                    findings.append(
                        ProjectionFinding(str(project), str(project), str(error))
                    )
                    continue
                findings.extend(command_findings)
                for label, target, sources in projections:
                    findings.extend(self._preflight(label, target, sources))
            return findings
        for project in projects:
            project_target, target_finding = self._project_target(project, surface)
            if target_finding is not None or project_target is None:
                findings.append(
                    target_finding
                    or ProjectionFinding(str(project), "", "invalid target")
                )
                continue
            try:
                sources = (
                    self.project_sources(project)
                    if surface == "skills"
                    else self._surface_sources(surface, "project-generic")
                )
            except (
                KeyError,
                OSError,
                RuntimeError,
                TypeError,
                ValueError,
                tomllib.TOMLDecodeError,
            ) as error:
                findings.append(
                    ProjectionFinding(str(project), str(project), str(error))
                )
                continue
            findings.extend(self._preflight(str(project), project_target, sources))
        return findings

    def apply(
        self,
        scope: str,
        selected: str | None = None,
        surface: str = "skills",
        project_roots: tuple[Path, ...] = (),
    ) -> list[ProjectionFinding]:
        if surface == "all":
            findings = self.check(scope, selected, surface, project_roots)
            blocking = self._blocking(findings)
            if blocking:
                return blocking
            for name in ("skills", "commands", "rules"):
                child_findings = self.apply(scope, selected, name, project_roots)
                if child_findings:
                    return child_findings
            return []
        findings = self.check(scope, selected, surface, project_roots)
        blocking = self._blocking(findings)
        if blocking:
            return blocking
        if surface == "commands":
            if scope == "personal":
                projections, command_findings = self._personal_command_projections(
                    selected
                )
                if command_findings:
                    return command_findings
                for _label, target, sources in projections:
                    self._apply_target(target, sources)
                return []
            projects, project_findings = self.resolve_projects(project_roots, selected)
            if project_findings:
                return project_findings
            for project in projects:
                projections, command_findings = self._project_command_projections(
                    project
                )
                if command_findings:
                    return command_findings
                for _label, target, sources in projections:
                    self._apply_target(target, sources)
            return []
        if scope == "personal":
            for name in self.personal_names(selected):
                configured = self.config["personal_targets"][name]
                if surface not in configured:
                    continue
                target = self._expand(configured[surface])
                self._apply_target(target, self._surface_sources(surface, "personal"))
            return []
        projects, project_findings = self.resolve_projects(project_roots, selected)
        if project_findings:
            return project_findings
        for project in projects:
            project_target, target_finding = self._project_target(project, surface)
            if target_finding is not None or project_target is None:
                return [
                    target_finding
                    or ProjectionFinding(str(project), "", "invalid target")
                ]
            sources = (
                self.project_sources(project)
                if surface == "skills"
                else self._surface_sources(surface, "project-generic")
            )
            self._apply_target(project_target, sources)
        return []
