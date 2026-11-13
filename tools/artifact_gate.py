"""Build and validate the exact immutable distribution artifacts."""

from __future__ import annotations

import cProfile
import fcntl
import hashlib
import inspect
import json
import os
import pstats
import signal
import sys
import tempfile
import time
import tomllib
import traceback
from collections.abc import Callable, Mapping
from contextlib import nullcontext
from pathlib import Path
from textwrap import indent
from types import FrameType, TracebackType
from typing import Literal, Self, cast

from strict_subprocess import run_strict

from agents_governance import GovernanceBundle, catalog_resources

_IGNORED_DIST_FILES = frozenset({".gitignore"})


class _ArtifactProfile:
    """Checkpoint one native profile without replacing operation failures."""

    def __init__(self, output: Path) -> None:
        self.output = output
        self.profile = cProfile.Profile()
        self.captured = False
        previous = signal.getsignal(signal.SIGTERM)
        if previous is None:
            raise ValueError(
                "artifact profiling cannot preserve an unknown SIGTERM handler"
            )
        self.previous = previous
        self.handler: Callable[[int, FrameType | None], None] = self._on_signal

    def __enter__(self) -> Self:
        print(
            f"ARTIFACT profile start={self.output} epoch={time.time():.6f} "
            f"pid={os.getpid()}",
            file=sys.stderr,
            flush=True,
        )
        signal.signal(signal.SIGTERM, self.handler)
        try:
            self.profile.enable()
        except BaseException as primary:
            self._restore(primary)
            raise
        return self

    def __exit__(
        self,
        _kind: type[BaseException] | None,
        primary: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        try:
            self._capture(primary)
        except BaseException as capture_failure:
            self._restore(capture_failure)
            raise
        self._restore(primary)

    def _restore(self, primary: BaseException | None) -> None:
        try:
            if signal.getsignal(signal.SIGTERM) is self.handler:
                signal.signal(signal.SIGTERM, self.previous)
        except BaseException as restore_failure:
            if primary is None:
                raise
            primary.add_note(
                f"artifact profile handler restoration failed: {restore_failure!r}"
            )

    def _capture(
        self, primary: BaseException | None, *, termination: bool = False
    ) -> None:
        if self.captured:
            return
        self.captured = True
        try:
            self.profile.disable()
            descriptor, temporary = tempfile.mkstemp(
                prefix=".profile-", dir=self.output.parent
            )
            os.close(descriptor)
            staged = Path(temporary)
            try:
                self.profile.dump_stats(str(staged))
                with staged.open("rb") as stream:
                    os.fsync(stream.fileno())
                os.link(staged, self.output)
            except BaseException as capture_failure:
                try:
                    staged.unlink()
                except BaseException as cleanup_failure:
                    capture_failure.add_note(
                        f"profile staging cleanup failed: {cleanup_failure!r}"
                    )
                    raise capture_failure from cleanup_failure
                raise
            staged.unlink()
            reason = "termination" if termination else "completed"
            if primary is not None and not termination:
                reason = "exception"
            report_path = self.output.with_suffix(".pstats.txt")
            with report_path.open("x", encoding="utf-8") as report:
                report.write(
                    f"Native artifact profile: pid={os.getpid()} "
                    f"executable={sys.executable}\n"
                    f"capture={reason}\n"
                    "Parent profiles measure coordination/waits; isolated public-load "
                    "profiles measure their own package import and contract.\n\n"
                )
                stats = pstats.Stats(str(self.output), stream=report)
                stats.sort_stats("cumtime").print_stats()
            print(
                f"ARTIFACT profile {self.output} pid={os.getpid()}",
                file=sys.stderr,
                flush=True,
            )
        except BaseException as capture_failure:
            if primary is None:
                raise
            primary.add_note(f"artifact profile capture failed: {capture_failure!r}")

    def _on_signal(self, signum: int, frame: FrameType | None) -> None:
        try:
            traceback.print_stack(frame)
            self._capture(sys.exception(), termination=True)
        finally:
            primary = sys.exception()
            try:
                signal.signal(signum, self.previous)
                if callable(self.previous):
                    self.previous(signum, frame)
                elif self.previous != signal.SIG_IGN:
                    signal.raise_signal(signum)
            except BaseException as action_failure:
                if primary is None:
                    raise
                primary.add_note(
                    f"native artifact signal action failed: {action_failure!r}"
                )
                raise primary from action_failure


def _profiled_proof(proof: str, output: Path) -> str:
    """Use this same capture owner inside the isolated public-load process."""
    imports = (
        "from __future__ import annotations\n"
        "import cProfile, os, pstats, signal, sys, tempfile, time, traceback\n"
        "from collections.abc import Callable\n"
        "from pathlib import Path\n"
        "from types import FrameType, TracebackType\n"
        "from typing import Self\n"
    )
    return (
        imports
        + inspect.getsource(_ArtifactProfile)
        + f"\nwith _ArtifactProfile(Path({str(output)!r})):\n"
        + indent(proof, "    ")
    )


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


def _build(repository: Path, *, profile_root: Path | None = None) -> tuple[Path, Path]:
    dist = _dist(repository)
    for entry in tuple(dist.iterdir()):
        if entry.name in _IGNORED_DIST_FILES:
            if entry.is_symlink() or not entry.is_file():
                raise ValueError(f"distribution marker must be physical: {entry}")
            continue
        if entry.is_symlink() or not entry.is_file():
            raise ValueError(f"refusing unsupported distribution residue: {entry}")
        entry.unlink()
    run_strict(
        ("uv", "build"), repository, "ARTIFACT build", timing=profile_root is not None
    )
    return _artifacts(dist)


def _smoke_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for variable in ("PYTHONPATH", "UV_PROJECT_ENVIRONMENT", "VIRTUAL_ENV"):
        environment.pop(variable, None)
    return environment


def _smoke(
    artifact: Path,
    cache_root: Path,
    version: str,
    resources: Mapping[str, tuple[str, int, str]],
    catalog: Mapping[str, tuple[str, int]],
    *,
    profile_root: Path | None = None,
) -> None:
    environment = _smoke_environment()
    environment["ARTIFACT_RESOURCE_EXPECTATIONS"] = json.dumps(resources)
    with tempfile.TemporaryDirectory(
        prefix=f"{artifact.name}-", dir=cache_root
    ) as temporary:
        smoke = Path(temporary)
        catalog_expectations = smoke / "catalog-expectations.json"
        catalog_expectations.write_text(json.dumps(catalog), encoding="utf-8")
        environment["ARTIFACT_CATALOG_EXPECTATIONS"] = str(catalog_expectations)
        environment_path = smoke / "venv"
        run_strict(
            ("uv", "venv", str(environment_path)),
            smoke,
            f"ARTIFACT create environment for {artifact.name}",
            environment,
            timing=profile_root is not None,
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
            timing=profile_root is not None,
        )
        proof = "\n".join(
            (
                "from agents_governance import GovernanceBundle, catalog_resources, __version__",
                "from importlib.resources import files",
                "from pathlib import Path",
                "import hashlib, json, os, stat",
                "if not files('agents_governance').joinpath('py.typed').is_file():",
                "    raise ValueError('installed PEP 561 marker missing')",
                f"expected = {version!r}",
                "bundle = GovernanceBundle.load()",
                "if __version__ != expected or bundle.distribution_version != expected:",
                "    raise ValueError('installed version mismatch')",
                "expected_resources = json.loads(os.environ['ARTIFACT_RESOURCE_EXPECTATIONS'])",
                "actual_resources = {}",
                "for skill in bundle.skills:",
                "    for resource in skill.resources:",
                "        identity = resource.path.relative_to(bundle.root).as_posix()",
                "        actual_resources[identity] = [",
                "            hashlib.sha256(resource.path.read_bytes()).hexdigest(),",
                "            stat.S_IMODE(resource.path.stat().st_mode), resource.format]",
                "if actual_resources != expected_resources:",
                "    raise ValueError('installed resource inventory, bytes, mode or format mismatch')",
                "print('ARTIFACT resources', len(actual_resources), 'exact bytes/modes/formats')",
                "expected_catalog = json.loads(Path(os.environ['ARTIFACT_CATALOG_EXPECTATIONS']).read_text(encoding='utf-8'))",
                "actual_catalog = {}",
                "for resource in catalog_resources(bundle):",
                "    digest = hashlib.sha256(resource.content).hexdigest()",
                "    if digest != resource.sha256:",
                "        raise ValueError('installed catalog digest disagrees with its bytes')",
                "    actual_catalog[resource.relative_path] = [digest, resource.mode]",
                "if actual_catalog != expected_catalog:",
                "    raise ValueError('installed neutral catalog inventory, bytes or mode mismatch')",
                "print('ARTIFACT neutral catalog', len(actual_catalog), 'exact bytes/modes/digests')",
                "print('ARTIFACT', __version__, bundle.schema_version, len(bundle.skills))",
            )
        )
        if profile_root is not None:
            proof = _profiled_proof(
                proof, profile_root / f"{artifact.name}.public-load.pstats"
            )
        run_strict(
            (str(environment_path / "bin" / "python"), "-c", proof),
            smoke,
            f"ARTIFACT public load {artifact.name}",
            environment,
            timing=profile_root is not None,
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
                    "from agents_governance import GovernanceBundle, CatalogResource, catalog_resources\n"
                    "from agents_governance import agent_profiles, catalog, commands, rules\n"
                    "bundle: GovernanceBundle = GovernanceBundle.load()\n"
                    "resources: tuple[CatalogResource, ...] = catalog_resources(bundle)\n"
                ),
            ),
            smoke,
            f"ARTIFACT typed public imports {artifact.name}",
            environment,
            timing=profile_root is not None,
        )


def _validate(
    repository: Path, cache_root: Path, *, profile_root: Path | None = None
) -> tuple[Path, Path]:
    artifacts = _artifacts(_dist(repository))
    version = _project_version(repository)
    bundle = GovernanceBundle.load(repository)
    catalog: dict[str, tuple[str, int]] = {}
    for resource in catalog_resources(bundle):
        digest = hashlib.sha256(resource.content).hexdigest()
        if digest != resource.sha256:
            raise ValueError("source catalog digest disagrees with its bytes")
        catalog[resource.relative_path] = (digest, resource.mode)
    resources = {
        resource.path.relative_to(bundle.root).as_posix(): (
            resource.sha256,
            resource.mode,
            resource.format,
        )
        for skill in bundle.skills
        for resource in skill.resources
    }
    for artifact in artifacts:
        _smoke(
            artifact, cache_root, version, resources, catalog, profile_root=profile_root
        )
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
    *,
    profile_root: Path | None = None,
) -> None:
    if mode == "build":
        _build(repository)
    elif mode == "validate":
        _validate(repository, cache_root)
    elif mode == "runtime":
        _build(repository, profile_root=profile_root)
        _validate(repository, cache_root, profile_root=profile_root)
    else:
        _publish(repository, cache_root)


def main() -> None:
    mode = os.environ.get("ARTIFACT_MODE")
    if mode not in {"build", "publish", "runtime", "validate"}:
        raise ValueError(
            "ARTIFACT_MODE must select build, publish, runtime, or validate"
        )
    mode = cast(Literal["build", "publish", "runtime", "validate"], mode)
    profile = os.environ.get("ARTIFACT_PROFILE")
    if profile not in {None, "", "0", "1"}:
        raise ValueError("ARTIFACT_PROFILE must be unset, 0, or 1")
    if profile == "1" and mode != "runtime":
        raise ValueError("ARTIFACT_PROFILE=1 requires the existing runtime operation")
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
    profile_root = (
        Path(tempfile.mkdtemp(prefix="runtime-profile-", dir=cache_root))
        if profile == "1"
        else None
    )
    if profile_root is not None:
        print(f"ARTIFACT profiling root={profile_root}", flush=True)
    with (
        (
            _ArtifactProfile(profile_root / "parent.pstats")
            if profile_root is not None
            else nullcontext()
        ),
        lock_path.open("a+b") as lock,
    ):
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _execute(mode, repository, cache_root, profile_root=profile_root)


if __name__ == "__main__":
    main()
