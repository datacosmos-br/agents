"""Build and validate the exact immutable distribution artifacts."""

from __future__ import annotations

import fcntl
import hashlib
import os
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Literal, cast

from strict_subprocess import run_strict

_IGNORED_DIST_FILES = frozenset({".gitignore"})


def _project_version(repository: Path) -> str:
    document = tomllib.loads(
        (repository / "pyproject.toml").read_text(encoding="utf-8")
    )
    project = document.get("project")
    if not isinstance(project, dict):
        raise TypeError("pyproject.toml project must be a mapping")
    version = project.get("version")
    if not isinstance(version, str) or not version.strip():
        raise TypeError("pyproject.toml project.version must be non-empty text")
    return version


def _dist(repository: Path) -> Path:
    dist = repository / "dist"
    if dist.is_symlink() or (dist.exists() and not dist.is_dir()):
        raise ValueError(f"distribution root must be a physical directory: {dist}")
    dist.mkdir(exist_ok=True)
    return dist


def _artifacts(dist: Path) -> tuple[Path, Path]:
    entries = tuple(sorted(dist.iterdir()))
    for entry in entries:
        if entry.is_symlink() or not entry.is_file():
            raise ValueError(f"distribution entry must be a physical file: {entry}")
    unexpected = tuple(
        entry for entry in entries if entry.name not in _IGNORED_DIST_FILES
    )
    wheels = tuple(entry for entry in unexpected if entry.suffix == ".whl")
    sdists = tuple(entry for entry in unexpected if entry.name.endswith(".tar.gz"))
    if len(unexpected) != 2 or len(wheels) != 1 or len(sdists) != 1:
        raise ValueError(
            "dist must contain exactly one wheel and one sdist: "
            f"{[entry.name for entry in unexpected]}"
        )
    return sdists[0], wheels[0]


def _build(repository: Path) -> tuple[Path, Path]:
    dist = _dist(repository)
    for entry in tuple(dist.iterdir()):
        if entry.name in _IGNORED_DIST_FILES:
            if entry.is_symlink() or not entry.is_file():
                raise ValueError(f"distribution marker must be physical: {entry}")
            continue
        if entry.is_symlink() or not entry.is_file():
            raise ValueError(f"refusing unsupported distribution residue: {entry}")
        entry.unlink()
    run_strict(("uv", "build"), repository, "ARTIFACT build")
    return _artifacts(dist)


def _smoke_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for variable in ("PYTHONPATH", "UV_PROJECT_ENVIRONMENT", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    return environment


def _smoke(artifact: Path, cache_root: Path, version: str) -> None:
    environment = _smoke_environment()
    with tempfile.TemporaryDirectory(
        prefix=f"{artifact.name}-", dir=cache_root
    ) as temporary:
        smoke = Path(temporary)
        environment_path = smoke / "venv"
        run_strict(
            ("uv", "venv", str(environment_path)),
            smoke,
            f"ARTIFACT create environment for {artifact.name}",
            environment,
        )
        run_strict(
            (
                "uv",
                "pip",
                "install",
                "--python",
                str(environment_path / "bin" / "python"),
                str(artifact),
            ),
            smoke,
            f"ARTIFACT install {artifact.name}",
            environment,
        )
        proof = "\n".join(
            (
                "from agents_governance import GovernanceBundle, __version__",
                "from importlib.resources import files",
                "if not files('agents_governance').joinpath('py.typed').is_file():",
                "    raise ValueError('installed PEP 561 marker missing')",
                f"expected = {version!r}",
                "bundle = GovernanceBundle.load()",
                "if __version__ != expected or bundle.distribution_version != expected:",
                "    raise ValueError('installed version mismatch')",
                "print('ARTIFACT', __version__, bundle.schema_version, len(bundle.skills))",
            )
        )
        run_strict(
            (str(environment_path / "bin" / "python"), "-c", proof),
            smoke,
            f"ARTIFACT public load {artifact.name}",
            environment,
        )
        run_strict(
            (
                sys.executable,
                "-m",
                "mypy",
                "--python-executable",
                str(environment_path / "bin" / "python"),
                "--cache-dir",
                str(smoke / "mypy"),
                "--strict",
                "-c",
                (
                    "from agents_governance import GovernanceBundle\n"
                    "from agents_governance import agent_profiles, catalog, commands, rules\n"
                    "bundle: GovernanceBundle = GovernanceBundle.load()\n"
                ),
            ),
            smoke,
            f"ARTIFACT typed public imports {artifact.name}",
            environment,
        )


def _validate(repository: Path, cache_root: Path) -> tuple[Path, Path]:
    artifacts = _artifacts(_dist(repository))
    version = _project_version(repository)
    for artifact in artifacts:
        _smoke(artifact, cache_root, version)
    return artifacts


def _manifest(dist: Path, artifacts: tuple[Path, Path]) -> Path:
    lines = tuple(
        f"{hashlib.sha256(artifact.read_bytes()).hexdigest()}  {artifact.name}"
        for artifact in sorted(artifacts)
    )
    target = dist / "SHA256SUMS"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix=".SHA256SUMS-",
        dir=dist,
        delete=False,
    ) as staged:
        staged.write("\n".join(lines) + "\n")
        staged.flush()
        os.fsync(staged.fileno())
        staged_path = Path(staged.name)
    staged_path.replace(target)
    return target


def _publish(repository: Path, cache_root: Path) -> None:
    tag = os.environ.get("GITHUB_REF_NAME")
    token = os.environ.get("GH_TOKEN")
    if tag is None or not tag.strip():
        raise ValueError("GITHUB_REF_NAME is required")
    if token is None or not token.strip():
        raise ValueError("GH_TOKEN is required")
    version = _project_version(repository)
    if tag != f"v{version}":
        raise ValueError(f"release tag {tag} does not equal v{version}")
    artifacts = _build(repository)
    _validate(repository, cache_root)
    manifest = _manifest(repository / "dist", artifacts)
    run_strict(
        (
            "gh",
            "release",
            "create",
            tag,
            "--verify-tag",
            "--generate-notes",
            *(str(path) for path in (*artifacts, manifest)),
        ),
        repository,
        f"ARTIFACT publish {tag}",
    )


def _execute(
    mode: Literal["build", "publish", "runtime", "validate"],
    repository: Path,
    cache_root: Path,
) -> None:
    if mode == "build":
        _build(repository)
    elif mode == "validate":
        _validate(repository, cache_root)
    elif mode == "runtime":
        _build(repository)
        _validate(repository, cache_root)
    else:
        _publish(repository, cache_root)


def main() -> None:
    mode = os.environ.get("ARTIFACT_MODE")
    if mode not in {"build", "publish", "runtime", "validate"}:
        raise ValueError(
            "ARTIFACT_MODE must select build, publish, runtime, or validate"
        )
    mode = cast(Literal["build", "publish", "runtime", "validate"], mode)
    repository = Path(__file__).resolve().parents[1]
    configured = os.environ.get("ARTIFACT_STATE_ROOT")
    if configured is None:
        raise ValueError("ARTIFACT_STATE_ROOT is required")
    cache_root = Path(configured)
    if not cache_root.is_absolute() or cache_root.is_relative_to(repository):
        raise ValueError("ARTIFACT_STATE_ROOT must be an absolute external path")
    for ancestor in (cache_root, *cache_root.parents):
        if ancestor.exists() and ancestor.is_symlink():
            raise ValueError(f"artifact state ancestry must be physical: {ancestor}")
    cache_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = cache_root / "artifacts.lock"
    if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
        raise ValueError(f"artifact lock must be a physical file: {lock_path}")
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _execute(mode, repository, cache_root)


if __name__ == "__main__":
    main()
