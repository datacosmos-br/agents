"""Fail-closed validation for project-owned security triage documents."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

_SUBSTITUTE_TRACKER = re.compile(
    r"^(?:Manual\s+ledger|Ledger:\s*manual)\s*$", re.MULTILINE | re.IGNORECASE
)
_FINDING = re.compile(r"^###\s+(.+)$", re.MULTILINE)
_DECISION = re.compile(
    r"^\*\*Decis(?:ão|ao)\*\*:\s*(.*)$", re.MULTILINE | re.IGNORECASE
)
_EVIDENCE = re.compile(
    r"^\*\*(?:Evidência|Evidencia|Evidence)\*\*:\s*(.*)$", re.MULTILINE | re.IGNORECASE
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


class SecurityInventoryError(RuntimeError):
    """The tracked manifest inventory could not be established safely."""


@dataclass(frozen=True)
class SecurityFinding:
    """One blocking defect in a security triage document."""

    path: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ScannerRoute:
    """One dependency manifest and its exact scanner invocation."""

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


@dataclass(frozen=True)
class SecurityInventory:
    """Deterministic scanner routes and blocking inventory findings."""

    routes: tuple[ScannerRoute, ...]
    findings: tuple[SecurityFinding, ...]


def _repository_root(root: Path) -> Path:
    resolved = root.resolve()
    if not resolved.is_dir():
        raise SecurityInventoryError(f"repository root is not a directory: {resolved}")
    try:
        process = subprocess.run(
            ["git", "-C", str(resolved), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise SecurityInventoryError("git executable is unavailable") from error
    if process.returncode != 0:
        detail = process.stderr.strip() or f"git exited {process.returncode}"
        raise SecurityInventoryError(f"cannot inspect repository {resolved}: {detail}")
    top_level = Path(process.stdout.strip()).resolve()
    if top_level != resolved:
        raise SecurityInventoryError(
            f"repository root must be explicit: {resolved} resolves to {top_level}"
        )
    return resolved


def _tracked_files(root: Path) -> dict[Path, str]:
    process = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z"],
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or f"git exited {process.returncode}"
        raise SecurityInventoryError(f"cannot inventory tracked files in {root}: {detail}")
    tracked: dict[Path, str] = {}
    for record in process.stdout.split("\0"):
        if not record:
            continue
        metadata, separator, raw_path = record.partition("\t")
        fields = metadata.split()
        if not separator or len(fields) != 3 or fields[2] != "0":
            raise SecurityInventoryError(
                f"unexpected git ls-files record in {root}: {record!r}"
            )
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise SecurityInventoryError(
                f"tracked path escapes repository root {root}: {raw_path!r}"
            )
        tracked[relative] = fields[0]
    return tracked


def _fixture_roots(root: Path) -> tuple[Path, ...]:
    configuration = root / "pyproject.toml"
    try:
        parsed = tomllib.loads(configuration.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise SecurityInventoryError(f"cannot read {configuration}: {error}") from error
    tool = parsed.get("tool", {})
    governance = tool.get("agents-governance", {}) if isinstance(tool, dict) else {}
    security = governance.get("security", {}) if isinstance(governance, dict) else {}
    raw_roots = security.get("fixture-roots", []) if isinstance(security, dict) else []
    if not isinstance(raw_roots, list) or any(
        not isinstance(item, str) or not item for item in raw_roots
    ):
        raise SecurityInventoryError(
            f"{configuration}: tool.agents-governance.security.fixture-roots "
            "must be a list of non-empty relative paths"
        )
    fixture_roots: list[Path] = []
    for item in raw_roots:
        candidate = Path(item)
        if candidate.is_absolute() or candidate == Path(".") or ".." in candidate.parts:
            raise SecurityInventoryError(
                f"{configuration}: invalid fixture root {item!r}"
            )
        fixture_roots.append(candidate)
    return tuple(sorted(fixture_roots, key=lambda path: path.as_posix()))


def _is_fixture(path: Path, fixture_roots: tuple[Path, ...]) -> bool:
    return any(path == root or root in path.parents for root in fixture_roots)


def _route_for_python_manifest(
    root: Path,
    manifest: Path,
    tracked: dict[Path, str],
) -> tuple[ScannerRoute | None, SecurityFinding | None]:
    scanner_input = manifest.parent / "uv.lock"
    if scanner_input not in tracked:
        return None, SecurityFinding(
            str(root / manifest),
            "missing-scanner-route",
            "tracked pyproject.toml requires a tracked uv.lock scanner input",
        )
    for relative in (manifest, scanner_input):
        destination = root / relative
        if tracked[relative] not in {"100644", "100755"} or not destination.is_file():
            return None, SecurityFinding(
                str(destination),
                "invalid-scanner-input",
                "security manifests and scanner inputs must be physical regular files",
            )
    return ScannerRoute(root, root / manifest, root / scanner_input), None


def inventory(roots: tuple[Path, ...]) -> SecurityInventory:
    """Map every tracked dependency manifest to exactly one scanner route."""

    if not roots:
        raise SecurityInventoryError("at least one explicit repository root is required")
    resolved_roots = tuple(_repository_root(root) for root in roots)
    if len(set(resolved_roots)) != len(resolved_roots):
        raise SecurityInventoryError("repository roots must be unique")
    routes: list[ScannerRoute] = []
    findings: list[SecurityFinding] = []
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
                key=lambda path: path.as_posix(),
            )
        )
        if not manifests:
            findings.append(
                SecurityFinding(
                    str(root),
                    "missing-manifest",
                    "repository has no tracked dependency manifest",
                )
            )
            continue
        for manifest in manifests:
            if manifest.name == "pyproject.toml":
                route, finding = _route_for_python_manifest(root, manifest, tracked)
                if route is not None:
                    routes.append(route)
                if finding is not None:
                    findings.append(finding)
                continue
            findings.append(
                SecurityFinding(
                    str(root / manifest),
                    "missing-scanner-route",
                    f"tracked {manifest.name} has no declared scanner route",
                )
            )
    return SecurityInventory(
        tuple(sorted(routes, key=lambda route: str(route.manifest))),
        tuple(sorted(findings, key=lambda item: (item.path, item.code))),
    )


def discover(roots: tuple[Path, ...]) -> tuple[Path, ...]:
    """Discover scanner triage documents below explicit repository roots."""

    return tuple(
        sorted(
            path
            for root in roots
            for path in (root.resolve() / "docs" / "security").glob("*-triage.md")
            if path.is_file()
        )
    )


def _sections(text: str) -> tuple[tuple[str, str], ...]:
    matches = tuple(_FINDING.finditer(text))
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


def validate_document(path: Path) -> tuple[SecurityFinding, ...]:
    """Validate traceability and closure evidence for one Markdown report."""

    text = path.read_text(encoding="utf-8")
    findings: list[SecurityFinding] = []
    if _SUBSTITUTE_TRACKER.search(text) is not None:
        findings.append(
            SecurityFinding(
                str(path),
                "substitute-tracker",
                "security reports must not act as a manual task ledger",
            )
        )
    sections = _sections(text)
    if not sections:
        findings.append(
            SecurityFinding(
                str(path),
                "missing-findings",
                "report must contain numbered finding sections",
            )
        )
    for title, body in sections:
        decisions = _DECISION.findall(body)
        decision = decisions[-1].strip().lower() if decisions else ""
        label = f"{path}#{title}"
        if not decision:
            findings.append(
                SecurityFinding(label, "missing-decision", "finding decision is empty")
            )
            continue
        if not any(decision.startswith(value) for value in _ALLOWED_DECISIONS):
            findings.append(
                SecurityFinding(
                    label,
                    "invalid-decision",
                    f"unsupported closing decision: {decision}",
                )
            )
        evidence = _EVIDENCE.findall(body)
        if not evidence or not evidence[-1].strip():
            findings.append(
                SecurityFinding(
                    label,
                    "missing-evidence",
                    "closed finding requires reproducible evidence",
                )
            )
    return tuple(findings)


def audit(roots: tuple[Path, ...]) -> tuple[SecurityFinding, ...]:
    """Audit every discovered triage document, failing when none exist."""

    documents = discover(roots)
    if not documents:
        joined = ", ".join(str(root.resolve()) for root in roots)
        return (
            SecurityFinding(
                joined, "missing-report", "no docs/security/*-triage.md documents found"
            ),
        )
    return tuple(finding for path in documents for finding in validate_document(path))


def build_parser() -> argparse.ArgumentParser:
    """Build the security scanner command-line interface."""

    parser = argparse.ArgumentParser(prog="agents-security")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inventory", "snyk"):
        command = commands.add_parser(name)
        command.add_argument("roots", nargs="+", type=Path)
    return parser


def _print_findings(result: SecurityInventory) -> int:
    for finding in result.findings:
        print(f"{finding.path}: {finding.code}: {finding.message}", file=sys.stderr)
    if result.findings:
        print(
            f"FAIL: {len(result.findings)} blocking security inventory finding(s)",
            file=sys.stderr,
        )
        return 1
    return 0


def _inventory_command(result: SecurityInventory) -> int:
    status = _print_findings(result)
    if status != 0:
        return status
    for route in result.routes:
        scanner_input = route.scanner_input.relative_to(route.root).as_posix()
        print(f"{route.manifest}: snyk: {scanner_input}")
    print(
        f"PASS: {len(result.routes)} tracked dependency manifest(s); "
        f"{len(result.routes)} scanner route(s)"
    )
    return 0


def _snyk_command(result: SecurityInventory) -> int:
    status = _print_findings(result)
    if status != 0:
        return status
    for route in result.routes:
        try:
            process = subprocess.run(route.command, cwd=route.root, check=False)
        except FileNotFoundError:
            print("FAIL: snyk executable is unavailable", file=sys.stderr)
            return 127
        if process.returncode != 0:
            manifest = route.manifest.relative_to(route.root).as_posix()
            print(
                f"FAIL: snyk exited {process.returncode} for {manifest}",
                file=sys.stderr,
            )
            return (
                128 + abs(process.returncode)
                if process.returncode < 0
                else process.returncode
            )
    print(f"PASS: {len(result.routes)} Snyk scanner route(s) completed")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run deterministic manifest inventory or its declared Snyk routes."""

    args = build_parser().parse_args(argv)
    try:
        result = inventory(tuple(args.roots))
    except SecurityInventoryError as error:
        print(f"agents-security: {error}", file=sys.stderr)
        return 2
    if args.command == "inventory":
        return _inventory_command(result)
    if args.command == "snyk":
        return _snyk_command(result)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
