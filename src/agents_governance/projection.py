"""Copy-based, item-scoped projections with no cross-repository links."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .catalog import Catalog


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


class Projector:
    """Materialize validated local copies while preserving foreign entries."""

    MANIFEST = ".agents-governance.json"
    _LOCAL_PATH = re.compile(r"(?:~/(?:\.agents|gt)(?:/|\b)|/home/[^/\s]+/)")

    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog
        config = catalog.root / "config" / "projections.json"
        self.config: dict[str, Any] = json.loads(config.read_text(encoding="utf-8"))

    @staticmethod
    def _copy_tree(source: Path, destination: Path) -> None:
        """Copy a tree independently, requesting CoW reflinks on Linux."""

        if source.is_file():
            shutil.copy2(source, destination)
            return
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
        shutil.copytree(source, destination, symlinks=False)

    @staticmethod
    def _expand(value: str) -> Path:
        return Path(os.path.expandvars(value)).expanduser().resolve()

    def personal_names(self, selected: str | None = None) -> tuple[str, ...]:
        names = tuple(sorted(self.config["personal_targets"]))
        if selected is None:
            return names
        if selected not in names:
            raise ValueError(f"unknown personal target: {selected}")
        return (selected,)

    def _source(self, directory: Path, origin: str) -> SourceSkill:
        return SourceSkill(
            directory.name,
            directory.resolve(),
            origin,
            self.catalog.digest_tree(directory),
        )

    def _catalog_sources(self, distribution: str) -> tuple[SourceSkill, ...]:
        root = self.catalog.root / "skills"
        return tuple(
            self._source(root / name, f"agents:{distribution}")
            for name in sorted(self.catalog.names_for(distribution))
        )

    def _surface_sources(
        self, surface: str, distribution: str
    ) -> tuple[SourceSkill, ...]:
        if surface == "skills":
            return self._catalog_sources(distribution)
        root = self.catalog.root / surface
        entries = self.config["surfaces"][surface]["entries"]
        return tuple(self._source(root / name, f"agents:{surface}") for name in entries)

    @staticmethod
    def _manifest(root: Path) -> dict[str, dict[str, str]]:
        path = root / Projector.MANIFEST
        if not path.is_file():
            return {}
        managed = json.loads(path.read_text(encoding="utf-8")).get("managed", {})
        return managed if isinstance(managed, dict) else {}

    @staticmethod
    def _remote(root: Path) -> str:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def discover_projects(self) -> tuple[Path, ...]:
        policy = self.config["projects"]
        town = self._expand(policy["town_root"])
        return tuple(
            path.resolve()
            for path in sorted(town.glob(policy["checkout_glob"]))
            if (path / ".git").exists()
        )

    @staticmethod
    def _dependency_names(value: object) -> set[str]:
        names: set[str] = set()
        if isinstance(value, str):
            names.add(
                re.split(r"[\s@<>=\[;]", value, maxsplit=1)[0].lower().replace("_", "-")
            )
        elif isinstance(value, list):
            for item in value:
                names.update(Projector._dependency_names(item))
        elif isinstance(value, dict):
            for key, item in value.items():
                names.add(str(key).lower().replace("_", "-"))
                names.update(Projector._dependency_names(item))
        return names

    @classmethod
    def _pyproject(cls, root: Path) -> dict[str, Any]:
        if not (root / "pyproject.toml").is_file():
            return {}
        loaded = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        return loaded if isinstance(loaded, dict) else {}

    @classmethod
    def is_flext_project(cls, root: Path) -> bool:
        loaded = cls._pyproject(root)
        tool = loaded.get("tool", {})
        flext = tool.get("flext", {}) if isinstance(tool, dict) else {}
        return bool(
            isinstance(flext, dict) and ("project" in flext or "workspace" in flext)
        ) or "flext-core" in cls._dependency_names(loaded)

    def detected_technologies(self, root: Path) -> tuple[str, ...]:
        detected: list[str] = []
        dependency_names: set[str] = set()
        package_json = root / "package.json"
        if package_json.is_file():
            package = json.loads(package_json.read_text(encoding="utf-8"))
            for field in ("dependencies", "devDependencies", "peerDependencies"):
                values = package.get(field, {})
                if isinstance(values, dict):
                    dependency_names.update(values)
        for name, profile in self.catalog.technology_profiles().items():
            marker_match = any(
                (root / marker).exists() for marker in profile["markers"]
            )
            dependency_match = bool(
                set(profile.get("dependencies", [])) & dependency_names
            )
            if marker_match or dependency_match:
                detected.append(name)
        return tuple(sorted(detected))

    def _flext_sources(self) -> tuple[SourceSkill, ...]:
        expected = self.config["projects"]["flext_remote"]
        roots = [
            root for root in self.discover_projects() if expected in self._remote(root)
        ]
        if len(roots) != 1:
            raise RuntimeError(
                f"expected one canonical FLEXT source, found {len(roots)}"
            )
        skills = roots[0] / ".agents" / "skills"
        return tuple(
            self._source(path, "flext")
            for path in sorted(skills.iterdir())
            if (path / "SKILL.md").is_file()
        )

    def project_sources(self, root: Path) -> tuple[SourceSkill, ...]:
        selected = list(self._catalog_sources("project-generic"))
        for technology in self.detected_technologies(root):
            selected.extend(self._catalog_sources(f"technology:{technology}"))
        if self.is_flext_project(root):
            selected.extend(self._flext_sources())
        by_name: dict[str, SourceSkill] = {}
        for source in selected:
            previous = by_name.get(source.name)
            if (
                previous is not None
                and previous.digest != source.digest
                and source.origin != "flext"
            ):
                raise RuntimeError(f"conflicting sources for skill {source.name}")
            by_name[source.name] = source
        return tuple(by_name[name] for name in sorted(by_name))

    def _source_findings(
        self, label: str, source: SourceSkill
    ) -> list[ProjectionFinding]:
        findings: list[ProjectionFinding] = []
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
            elif path.is_file() and path.suffix.lower() in {
                ".md",
                ".mdx",
                ".json",
                ".toml",
                ".yaml",
                ".yml",
            }:
                text = path.read_text(encoding="utf-8", errors="replace")
                if self._LOCAL_PATH.search(text):
                    findings.append(
                        ProjectionFinding(
                            label,
                            f"{source.name}/{relative}",
                            "cross-repository local path",
                        )
                    )
        return findings

    def _preflight(
        self, label: str, root: Path, sources: tuple[SourceSkill, ...]
    ) -> list[ProjectionFinding]:
        findings: list[ProjectionFinding] = []
        previous = self._manifest(root)
        expected = {source.name for source in sources}
        for source in sources:
            findings.extend(self._source_findings(label, source))
            destination = root / source.name
            if not destination.exists() and not destination.is_symlink():
                findings.append(ProjectionFinding(label, str(destination), "missing"))
                continue
            if destination.is_symlink():
                findings.append(
                    ProjectionFinding(label, str(destination), "legacy symlink")
                )
                continue
            current = self.catalog.digest_tree(destination.resolve())
            if current == source.digest:
                continue
            if previous.get(source.name, {}).get("digest") == current:
                findings.append(
                    ProjectionFinding(label, str(destination), "managed update")
                )
            elif source.origin == "flext":
                findings.append(
                    ProjectionFinding(label, str(destination), "legacy owner copy")
                )
            else:
                findings.append(
                    ProjectionFinding(label, str(destination), "foreign collision")
                )
        for stale, metadata in sorted(previous.items()):
            if stale in expected:
                continue
            destination = root / stale
            if destination.exists() and self.catalog.digest_tree(
                destination.resolve()
            ) != metadata.get("digest"):
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
    def _blocking(findings: list[ProjectionFinding]) -> list[ProjectionFinding]:
        reconcilable = {
            "foreign collision",
            "missing",
            "missing manifest",
            "legacy symlink",
            "managed update",
            "legacy owner copy",
            "modified stale managed entry",
            "stale managed entry",
        }
        return [finding for finding in findings if finding.message not in reconcilable]

    def _apply_target(self, root: Path, sources: tuple[SourceSkill, ...]) -> None:
        root.mkdir(parents=True, exist_ok=True)
        archive = root / ".agents-archive"

        def preserve(path: Path) -> None:
            archive.mkdir(mode=0o700, exist_ok=True)
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
            path.replace(archive / f"{path.name}.{stamp}.bak")

        previous = self._manifest(root)
        expected = {source.name for source in sources}
        for stale, metadata in sorted(previous.items()):
            if stale in expected:
                continue
            destination = root / stale
            if destination.is_symlink():
                destination.unlink()
            elif destination.exists():
                preserve(destination)
        for source in sources:
            destination = root / source.name
            if (
                destination.exists()
                and not destination.is_symlink()
                and self.catalog.digest_tree(destination) == source.digest
            ):
                continue
            if destination.is_symlink():
                destination.unlink()
            elif destination.exists():
                preserve(destination)
            staging = Path(tempfile.mkdtemp(prefix=".agents-stage.", dir=root))
            temporary = staging / source.name
            self._copy_tree(source.directory, temporary)
            temporary.replace(destination)
            staging.rmdir()
        payload = {
            "version": 2,
            "managed": {
                source.name: {"digest": source.digest, "origin": source.origin}
                for source in sources
            },
        }
        temporary = root / f".{self.MANIFEST}.{os.getpid()}"
        temporary.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        temporary.replace(root / self.MANIFEST)

    def check(
        self, scope: str, selected: str | None = None, surface: str = "skills"
    ) -> list[ProjectionFinding]:
        findings: list[ProjectionFinding] = []
        if surface == "all":
            return [
                item
                for name in ("skills", "commands", "rules")
                for item in self.check(scope, selected, name)
            ]
        if surface not in {"skills", "commands", "rules"}:
            raise ValueError(f"unknown projection surface: {surface}")
        if scope == "personal":
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
        matched = selected is None
        for project in self.discover_projects():
            label = project.parent.parent.name
            if selected is not None and selected not in {label, str(project)}:
                continue
            matched = True
            target = project / self.config["projects"][f"{surface}_path"]
            sources = (
                self.project_sources(project)
                if surface == "skills"
                else self._surface_sources(surface, "project-generic")
            )
            findings.extend(self._preflight(label, target, sources))
        if not matched:
            findings.append(
                ProjectionFinding(
                    selected or "", "", "unknown project projection target"
                )
            )
        return findings

    def apply(
        self, scope: str, selected: str | None = None, surface: str = "skills"
    ) -> list[ProjectionFinding]:
        if surface == "all":
            findings = self.check(scope, selected, surface)
            blocking = self._blocking(findings)
            if blocking:
                return blocking
            for name in ("skills", "commands", "rules"):
                self.apply(scope, selected, name)
            return []
        findings = self.check(scope, selected, surface)
        blocking = self._blocking(findings)
        if blocking:
            return blocking
        if scope == "personal":
            for name in self.personal_names(selected):
                configured = self.config["personal_targets"][name]
                if surface not in configured:
                    continue
                target = self._expand(configured[surface])
                self._apply_target(target, self._surface_sources(surface, "personal"))
            return []
        for project in self.discover_projects():
            label = project.parent.parent.name
            if selected is not None and selected not in {label, str(project)}:
                continue
            target = project / self.config["projects"][f"{surface}_path"]
            sources = (
                self.project_sources(project)
                if surface == "skills"
                else self._surface_sources(surface, "project-generic")
            )
            self._apply_target(target, sources)
        return []
