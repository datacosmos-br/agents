"""Materialize and verify the global ``~/.agents`` read-only projection.

ADR-0022: the user home catalog is a materialized projection of the source
checkout's semantic trees — never a symlink and never a writable consumer
surface. ``sync`` converges the home to the declared artifact set (removing
undeclared residue with a printed receipt); ``check`` recomputes version and
per-tree digests and fails loud on any drift, missing manifest, or undeclared
entry. A home that does not exist at all passes vacuously with a notice so
machines without a provisioned projection (fresh clones, CI runners) are not
flagged; a home that exists in any other form is verified strictly.

Dev-only tooling per ADR-0008: never packaged, imports the public API only.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import NoReturn

from agents_governance import __version__

MANIFEST_NAME = ".agents-governance.json"
OWNER = "agents-governance"

ARTIFACT_TREES: tuple[str, ...] = (
    "skills",
    "rules",
    "commands",
    "agents",
    "evals",
    "docs/adr",
    "docs/research",
    "docs/security",
)
ARTIFACT_FILES: tuple[str, ...] = ("AGENTS.md", "README.md", "metadata.json")


def _tree_files(root: Path, tree: str) -> list[Path]:
    base = root / tree
    if base.is_file():
        return [base]
    return sorted(path for path in base.rglob("*") if path.is_file())


def _tree_digest(files: list[Path], root: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\n")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest(), len(files)


def _source_snapshot(root: Path) -> dict[str, tuple[str, int]]:
    snapshot: dict[str, tuple[str, int]] = {}
    for tree in ARTIFACT_TREES:
        files = _tree_files(root, tree)
        if not files:
            raise ValueError(f"declared artifact tree is empty in source: {tree}")
        snapshot[tree] = _tree_digest(files, root)
    for name in ARTIFACT_FILES:
        path = root / name
        if not path.is_file():
            raise ValueError(f"declared artifact file is missing in source: {name}")
        digest, count = _tree_digest([path], root)
        snapshot[name] = (digest, count)
    return snapshot


def _fail(message: str) -> NoReturn:
    print(f"HOME-CHECK RED: {message}", file=sys.stderr)
    raise SystemExit(1)


def sync(root: Path, target: Path) -> None:
    """Converge the home projection to the declared artifact set."""

    if target.is_symlink():
        raise ValueError(
            f"{target} is still a symlink; perform the ADR-0022 transition "
            "(backup + unlink) before materializing the projection"
        )
    if target.exists() and not target.is_dir():
        raise ValueError(f"{target} exists and is not a directory")
    target.mkdir(parents=True, exist_ok=True)
    snapshot = _source_snapshot(root)
    declared: set[str] = set()

    for tree in ARTIFACT_TREES:
        source_base = root / tree
        target_base = target / tree
        if source_base.is_file():
            declared.add(tree)
            target_base.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_base, target_base)
            continue
        for path in _tree_files(root, tree):
            relative = path.relative_to(root)
            declared.add(relative.as_posix())
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    for name in ARTIFACT_FILES:
        declared.add(name)
        shutil.copy2(root / name, target / name)

    removed: list[str] = []
    for path in sorted(target.rglob("*"), reverse=True):
        if path.name == MANIFEST_NAME:
            continue
        relative_posix = path.relative_to(target).as_posix()
        if relative_posix in declared:
            continue
        if path.is_dir():
            if not any(path.iterdir()):
                path.rmdir()
                removed.append(relative_posix + "/")
        else:
            path.unlink()
            removed.append(relative_posix)
    if removed:
        print(f"home-sync removed {len(removed)} undeclared entries (receipt above)")
        for entry in removed:
            print(f"  - {entry}")

    manifest = {
        "owner": OWNER,
        "distribution_version": __version__,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "artifacts": {
            key: {"files": count, "digest": digest}
            for key, (digest, count) in sorted(snapshot.items())
        },
    }
    (target / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    total = sum(count for _, count in snapshot.values())
    print(
        f"home-sync: materialized {total} files, "
        f"{len(snapshot)} artifact trees, version {__version__}"
    )


def check(root: Path, target: Path) -> None:
    """Fail loud on any drift between the catalog and the home projection."""

    if not target.exists():
        print(
            "home-check: no ~/.agents provisioned on this machine; "
            "ADR-0022 gate satisfied vacuously"
        )
        return
    if target.is_symlink():
        _fail(f"{target} is a symlink; the ADR-0022 transition has regressed")
    manifest_path = target / MANIFEST_NAME
    if not manifest_path.is_file():
        _fail(f"projection manifest missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("owner") != OWNER:
        _fail(f"manifest owner mismatch: {manifest.get('owner')!r}")
    if manifest.get("distribution_version") != __version__:
        _fail(
            "manifest version "
            f"{manifest.get('distribution_version')!r} != bundle {__version__!r}; "
            "run `make home-sync`"
        )
    recorded = manifest.get("artifacts")
    if not isinstance(recorded, dict):
        _fail("manifest artifacts section missing")
    snapshot = _source_snapshot(root)
    for key, (digest, count) in sorted(snapshot.items()):
        entry = recorded.get(key)
        if not isinstance(entry, dict):
            _fail(f"manifest has no entry for {key}; run `make home-sync`")
        if entry.get("digest") != digest or entry.get("files") != count:
            _fail(f"manifest digest stale for {key}; run `make home-sync`")

    source_files: set[str] = set()
    for tree in ARTIFACT_TREES:
        for path in _tree_files(root, tree):
            source_files.add(path.relative_to(root).as_posix())
    source_files.update(ARTIFACT_FILES)

    projected: set[str] = set()
    for path in sorted(target.rglob("*")):
        if not path.is_file() or path.name == MANIFEST_NAME:
            continue
        relative = path.relative_to(target).as_posix()
        projected.add(relative)
        if relative not in source_files:
            _fail(f"undeclared entry in the home projection: {relative}")
        source = root / relative
        if (
            hashlib.sha256(path.read_bytes()).hexdigest()
            != hashlib.sha256(source.read_bytes()).hexdigest()
        ):
            _fail(f"projected file diverged from the catalog: {relative}")

    missing = sorted(source_files - projected)
    if missing:
        _fail(
            f"{len(missing)} declared files missing from the projection: {missing[:5]}"
        )
    print(
        f"home-check: {len(projected)} files verified against the catalog, "
        f"{len(snapshot)} trees, version {__version__} — OK"
    )


def main(argv: list[str] | None = None) -> None:
    """Dispatch the home projection verb."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1 or arguments[0] not in {"sync", "check"}:
        raise SystemExit("usage: python tools/home_projection.py {sync|check}")
    root = Path(__file__).resolve().parents[1]
    target = Path.home() / ".agents"
    if arguments[0] == "sync":
        sync(root, target)
    else:
        check(root, target)


if __name__ == "__main__":
    main()
