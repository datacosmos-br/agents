"""Strict dependency-scanner inventory and triage evidence validation."""

from __future__ import annotations

import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from .frontmatter import cast_mapping

_SECTION = re.compile(r"^###\s+(.+)$", re.MULTILINE)
_DECISION = re.compile(
    r"^\*\*Decis(?:ão|ao)\*\*:\s*(.*)$", re.MULTILINE | re.IGNORECASE
)
_EVIDENCE = re.compile(
    r"^\*\*(?:Evidência|Evidencia|Evidence)\*\*:\s*(.*)$",
    re.MULTILINE | re.IGNORECASE,
)
_ALLOWED_DECISIONS = ("corrigir", "corrigido", "falso-positivo")
_DEPENDENCY_MANIFESTS = frozenset(
    {
        "Cargo.toml",
        "Gemfile",
        "build.gradle",
        "build.gradle.kts",
        "go.mod",
        "package.json",
        "pom.xml",
        "pyproject.toml",
        "requirements.txt",
    }
)


@dataclass(frozen=True)
class ScannerRoute:
    """One validated dependency manifest and its native scanner command."""

    root: Path
    manifest: Path
    scanner_input: Path

    @property
    def command(self) -> tuple[str, ...]:
        scanner_input = self.scanner_input.relative_to(self.root).as_posix()
        return (
            "snyk",
            "test",
            f"--file={scanner_input}",
            "--dev",
            "--severity-threshold=low",
        )


def _repository_root(root: Path) -> Path:
    resolved = root.resolve(strict=True)
    if not resolved.is_dir():
        raise NotADirectoryError(resolved)
    process = subprocess.run(
        ("git", "-C", str(resolved), "rev-parse", "--show-toplevel"),
        check=True,
        capture_output=True,
        text=True,
    )
    top_level = Path(process.stdout.rstrip("\n")).resolve(strict=True)
    if top_level != resolved:
        raise ValueError(
            f"repository root must be explicit: {resolved} resolves to {top_level}"
        )
    return resolved


def _tracked_files(root: Path) -> dict[Path, str]:
    process = subprocess.run(
        ("git", "-C", str(root), "ls-files", "--stage", "-z"),
        check=True,
        capture_output=True,
        text=True,
    )
    tracked: dict[Path, str] = {}
    for record in process.stdout.split("\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition("\t")
        fields = metadata.split()
        if not separator or len(fields) != 3 or fields[2] != "0":
            raise ValueError(f"unexpected git ls-files record in {root}: {record!r}")
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(
                f"tracked path escapes repository root {root}: {raw_path!r}"
            )
        if relative in tracked:
            raise ValueError(f"duplicate tracked path in {root}: {raw_path!r}")
        tracked[relative] = fields[0]
    return tracked


def _fixture_roots(root: Path) -> tuple[Path, ...]:
    configuration = root / "pyproject.toml"
    parsed = tomllib.loads(configuration.read_text(encoding="utf-8"))
    tool = cast_mapping(parsed["tool"], f"{configuration}: tool")
    governance = cast_mapping(
        tool["agents-governance"], f"{configuration}: tool.agents-governance"
    )
    security = cast_mapping(
        governance["security"],
        f"{configuration}: tool.agents-governance.security",
    )
    if frozenset(security) != {"fixture-roots"}:
        raise ValueError(f"{configuration}: security fields must equal fixture-roots")
    raw_roots = security["fixture-roots"]
    if not isinstance(raw_roots, list) or any(
        not isinstance(item, str) or not item for item in raw_roots
    ):
        raise TypeError(
            f"{configuration}: fixture-roots must be a list of non-empty paths"
        )
    fixture_roots: list[Path] = []
    for item in cast(list[str], raw_roots):
        candidate = Path(item)
        if candidate.is_absolute() or candidate == Path(".") or ".." in candidate.parts:
            raise ValueError(f"{configuration}: invalid fixture root {item!r}")
        if candidate in fixture_roots:
            raise ValueError(f"{configuration}: duplicate fixture root {item!r}")
        fixture_roots.append(candidate)
    return tuple(sorted(fixture_roots, key=Path.as_posix))


def _is_fixture(path: Path, fixture_roots: tuple[Path, ...]) -> bool:
    return any(path == root or root in path.parents for root in fixture_roots)


def _python_route(root: Path, manifest: Path, tracked: dict[Path, str]) -> ScannerRoute:
    scanner_input = manifest.parent / "uv.lock"
    if scanner_input not in tracked:
        raise ValueError(
            f"{root / manifest}: tracked pyproject.toml requires tracked uv.lock"
        )
    for relative in (manifest, scanner_input):
        destination = root / relative
        if tracked[relative] not in {"100644", "100755"}:
            raise ValueError(f"scanner input has invalid tracked mode: {destination}")
        if destination.is_symlink() or not destination.is_file():
            raise ValueError(f"scanner input must be a physical file: {destination}")
    return ScannerRoute(root, root / manifest, root / scanner_input)


def inventory(roots: tuple[Path, ...]) -> tuple[ScannerRoute, ...]:
    """Return every scanner route or raise on the first inventory defect."""

    if not roots:
        raise ValueError("at least one explicit repository root is required")
    resolved_roots = tuple(_repository_root(root) for root in roots)
    if len(set(resolved_roots)) != len(resolved_roots):
        raise ValueError("repository roots must be unique")

    routes: list[ScannerRoute] = []
    for root in sorted(resolved_roots, key=str):
        tracked = _tracked_files(root)
        fixture_roots = _fixture_roots(root)
        manifests = tuple(
            sorted(
                (
                    relative
                    for relative in tracked
                    if relative.name in _DEPENDENCY_MANIFESTS
                    and not _is_fixture(relative, fixture_roots)
                ),
                key=Path.as_posix,
            )
        )
        if not manifests:
            raise ValueError(f"repository has no tracked dependency manifest: {root}")
        for manifest in manifests:
            if manifest.name != "pyproject.toml":
                raise ValueError(
                    f"tracked manifest has no scanner route: {root / manifest}"
                )
            routes.append(_python_route(root, manifest, tracked))
    return tuple(sorted(routes, key=lambda route: str(route.manifest)))


def discover(roots: tuple[Path, ...]) -> tuple[Path, ...]:
    """Discover every physical security-triage document."""

    documents = tuple(
        sorted(
            path
            for root in roots
            for path in (root.resolve(strict=True) / "docs" / "security").glob(
                "*-triage.md"
            )
        )
    )
    if not documents:
        raise FileNotFoundError("no docs/security/*-triage.md document exists")
    for path in documents:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"security triage must be a physical file: {path}")
    return documents


def _sections(text: str) -> tuple[tuple[str, str], ...]:
    matches = tuple(_SECTION.finditer(text))
    if not matches:
        raise ValueError("security report has no numbered section")
    return tuple(
        (
            match.group(1).strip(),
            text[
                match.end() : matches[index + 1].start()
                if index + 1 < len(matches)
                else len(text)
            ],
        )
        for index, match in enumerate(matches)
    )


def validate_document(path: Path) -> None:
    """Raise on the first incomplete security decision or evidence field."""

    for title, body in _sections(path.read_text(encoding="utf-8")):
        decisions = _DECISION.findall(body)
        if len(decisions) != 1 or not decisions[0].strip():
            raise ValueError(f"{path}#{title}: finding decision is missing or empty")
        decision = decisions[0].strip().lower()
        if not any(decision.startswith(value) for value in _ALLOWED_DECISIONS):
            raise ValueError(f"{path}#{title}: unsupported decision: {decision}")
        evidence = _EVIDENCE.findall(body)
        if len(evidence) != 1 or not evidence[0].strip():
            raise ValueError(f"{path}#{title}: reproducible evidence is required")


def audit(roots: tuple[Path, ...]) -> tuple[Path, ...]:
    """Validate every security-triage document and return its exact inventory."""

    documents = discover(roots)
    for path in documents:
        validate_document(path)
    return documents


__all__ = ("ScannerRoute", "audit", "discover", "inventory", "validate_document")
