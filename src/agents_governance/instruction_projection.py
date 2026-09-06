"""Document-layout instruction projection owned exclusively by optionless sync.

`agentsctl sync` owns governance content: skills, commands, rules, and the
session capsule rendered from them. This module publishes that capsule into the
providers whose rules surface is a document (`AGENTS.md`, `GEMINI.md`) rather
than a directory, which `Projector` deliberately delegates here.

Hook delivery is not this owner's surface. A hook executes a runtime, so it
belongs to that runtime's own deploy and reaches only the agent's own home.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from .agent_profiles import AgentProvider
from .cleanup import (
    PreparedPublication,
    Publication,
    remove_physical,
    run_atomic_publications,
    run_with_cleanup,
)
from .commands import CommandSpec
from .governance_config import GovernanceConfig
from .projection_authorization import (
    ProjectAuthorization,
    load_project_authorization,
)
from .projection_config import (
    ProjectionConfig,
    ProjectionContext,
    ProjectionStatus,
    ProjectionSurface,
    RuleLayout,
)
from .rules import RuleSpec

_INSTRUCTIONS_BEGIN = "<!-- AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN -->"
_INSTRUCTIONS_END = "<!-- AIHUB-GOVERNANCE-INSTRUCTIONS-END -->"
_CAPSULE_PREFIX = "<!-- AIHUB-GOVERNANCE-CAPSULE v1 sha256:"
_MARKDOWN_LINK = re.compile(r"\[([^\]\n]+)\]\([^)]+\)")
_INSTRUCTION_MODE = 0o644


class InstructionProjectionDriftError(RuntimeError):
    """A projected instruction document differs from the canonical capsule."""


@dataclass(frozen=True)
class InstructionPlan:
    provider: AgentProvider
    context: ProjectionContext
    destination: Path
    rendered: str


@dataclass(frozen=True)
class _FileState:
    destination: Path
    desired: str
    desired_mode: int
    previous: bytes | None
    previous_mode: int | None
    drift: bool


@dataclass
class _StagedFile:
    state: _FileState
    stage: Path
    candidate: Path
    backup: Path
    created_parents: tuple[Path, ...] = ()
    installed: bool = False


def _digest_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _physical_boundary(path: Path, label: str) -> Path:
    absolute = Path(os.path.abspath(path))
    if absolute.is_symlink() or not absolute.is_dir():
        raise ValueError(f"{label} must be a physical directory: {absolute}")
    return absolute.resolve(strict=True)


def _destination(boundary: Path, configured: str, context: ProjectionContext) -> Path:
    if context is ProjectionContext.PERSONAL:
        prefix = "${HOME}/"
        relative = configured.removeprefix(prefix)
    else:
        relative = configured
    target = Path(os.path.abspath(boundary / relative))
    target.relative_to(boundary)
    cursor = Path(target.anchor)
    for part in target.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"instruction projection path symlink forbidden: {cursor}")
        if not cursor.exists():
            break
    return target


def capsule(
    governance: GovernanceConfig,
    commands: tuple[CommandSpec, ...],
    rules: tuple[RuleSpec, ...],
) -> str:
    """Render the one canonical session governance capsule.

    Content has a single owner. Every consumer that delivers the capsule -
    this module's document merge, and the runtime that owns hook delivery -
    renders it here rather than reimplementing it.
    """

    by_identity = {rule.identity: rule for rule in rules}
    missing = tuple(
        identity
        for identity in governance.bootstrap_rules
        if identity not in by_identity
    )
    if missing:
        raise ValueError(f"governance capsule owner is missing: {missing[0]}")
    sections = [
        "# Generated session governance capsule",
        "",
        (
            "This projection is derived by `agentsctl sync`; edit canonical "
            "`AGENTS.md`, `rules/`, `skills/`, or `commands/`, never this output. "
            "The operator's newest request has precedence. Provider hooks are "
            "delivery mechanisms, not policy owners."
        ),
    ]
    for identity in governance.bootstrap_rules:
        sections.extend(
            (
                "",
                f"## Rule `{identity}`",
                "",
                _MARKDOWN_LINK.sub(r"\1", by_identity[identity].body.strip()),
            )
        )
    sections.extend(("", "## Capability indexes", ""))
    sections.append("Skills: " + ", ".join(governance.bootstrap_skills))
    sections.append("Commands: " + ", ".join(command.name for command in commands))
    body = "\n".join(sections).rstrip()
    digest = _digest_text(body)
    rendered = f"<!-- AIHUB-GOVERNANCE-CAPSULE v1 sha256:{digest} -->\n{body}\n"
    if len(rendered) > 10_000:
        raise ValueError(
            f"governance capsule exceeds delivery limit: {len(rendered)} characters"
        )
    return rendered


def _read_instruction(path: Path) -> str:
    if not path.exists() and not path.is_symlink():
        return ""
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"instruction projection must be a physical file: {path}")
    return path.read_text(encoding="utf-8")


def _validate_capsule(value: str, path: Path) -> None:
    header, separator, body = value.partition("\n")
    suffix = " -->"
    if (
        not separator
        or not header.startswith(_CAPSULE_PREFIX)
        or not header.endswith(suffix)
    ):
        raise ValueError(f"managed instruction capsule header is invalid: {path}")
    digest = header.removeprefix(_CAPSULE_PREFIX).removesuffix(suffix)
    if len(digest) != 64 or digest != _digest_text(body):
        raise ValueError(f"managed instruction capsule was modified: {path}")


def _merge_instruction(path: Path, rendered_capsule: str) -> str:
    current = _read_instruction(path)
    begin_count = current.count(_INSTRUCTIONS_BEGIN)
    end_count = current.count(_INSTRUCTIONS_END)
    if begin_count != end_count or begin_count > 1:
        raise ValueError(f"managed instruction region is malformed: {path}")
    block = f"{_INSTRUCTIONS_BEGIN}\n{rendered_capsule.rstrip()}\n{_INSTRUCTIONS_END}"
    if begin_count == 0:
        if not current:
            return f"{block}\n"
        separator = "\n" if current.endswith("\n") else "\n\n"
        return f"{current}{separator}{block}\n"
    before, remainder = current.split(_INSTRUCTIONS_BEGIN, 1)
    owned, after = remainder.split(_INSTRUCTIONS_END, 1)
    _validate_capsule(owned.strip(), path)
    return f"{before}{block}{after}"


class InstructionProjector:
    """Compile and atomically publish document-layout instruction projections."""

    def __init__(
        self,
        governance: GovernanceConfig,
        config: ProjectionConfig,
        commands: tuple[CommandSpec, ...],
        rules: tuple[RuleSpec, ...],
    ) -> None:
        self.governance = governance
        self.config = config
        self.commands = commands
        self.rules = rules

    def _plans(
        self, authorization: ProjectAuthorization
    ) -> tuple[InstructionPlan, ...]:
        home = _physical_boundary(Path.home(), "personal home")
        repository = _physical_boundary(authorization.project, "project root")
        rendered_capsule = capsule(self.governance, self.commands, self.rules)
        plans: list[InstructionPlan] = []
        for provider in AgentProvider:
            for context in ProjectionContext:
                if context is ProjectionContext.PROJECT and not authorization.selected:
                    continue
                cell = self.config.cell(provider, context, ProjectionSurface.RULES)
                if (
                    cell.status is not ProjectionStatus.SUPPORTED
                    or cell.layout is not RuleLayout.DOCUMENT
                ):
                    continue
                assert cell.path is not None
                boundary = home if context is ProjectionContext.PERSONAL else repository
                destination = _destination(boundary, cell.path, context)
                plans.append(
                    InstructionPlan(
                        provider,
                        context,
                        destination,
                        _merge_instruction(destination, rendered_capsule),
                    )
                )
        return tuple(plans)

    @staticmethod
    def _state(destination: Path, desired: str, mode: int) -> _FileState:
        if destination.is_symlink():
            raise ValueError(f"instruction projection symlink forbidden: {destination}")
        if destination.exists():
            metadata = destination.lstat()
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError(
                    f"instruction projection target must be a regular file: {destination}"
                )
            previous = destination.read_bytes()
            previous_mode = stat.S_IMODE(metadata.st_mode)
        else:
            previous = None
            previous_mode = None
        encoded = desired.encode()
        return _FileState(
            destination,
            desired,
            mode,
            previous,
            previous_mode,
            previous != encoded or previous_mode != mode,
        )

    def _states(self, authorization: ProjectAuthorization) -> tuple[_FileState, ...]:
        desired: dict[Path, str] = {}
        for plan in self._plans(authorization):
            previous = desired.get(plan.destination)
            if previous is not None and previous != plan.rendered:
                raise ValueError(
                    f"conflicting instruction projection: {plan.destination}"
                )
            desired[plan.destination] = plan.rendered
        return tuple(
            self._state(destination, text, _INSTRUCTION_MODE)
            for destination, text in sorted(
                desired.items(), key=lambda item: str(item[0])
            )
        )

    @staticmethod
    def _stage(state: _FileState) -> _StagedFile:
        ancestor = state.destination.parent
        while not ancestor.exists():
            ancestor = ancestor.parent
        if ancestor.is_symlink() or not ancestor.is_dir():
            raise ValueError(
                f"instruction staging ancestor must be physical: {ancestor}"
            )
        stage = Path(
            tempfile.mkdtemp(prefix=".agents-instruction-stage.", dir=ancestor)
        )
        candidate = stage / "candidate"
        backup = stage / "previous"

        def build() -> _StagedFile:
            candidate.write_text(state.desired, encoding="utf-8")
            candidate.chmod(state.desired_mode)
            if state.previous is not None:
                backup.write_bytes(state.previous)
                assert state.previous_mode is not None
                backup.chmod(state.previous_mode)
            return _StagedFile(state, stage, candidate, backup)

        return run_with_cleanup(build, lambda: remove_physical(stage))

    @staticmethod
    def _current(state: _FileState) -> tuple[bytes | None, int | None]:
        destination = state.destination
        if destination.is_symlink():
            raise RuntimeError(
                f"instruction projection changed to symlink after preflight: {destination}"
            )
        if not destination.exists():
            return None, None
        if not destination.is_file():
            raise RuntimeError(
                f"instruction projection changed type after preflight: {destination}"
            )
        return destination.read_bytes(), stat.S_IMODE(destination.lstat().st_mode)

    @staticmethod
    def _publish(staged: _StagedFile) -> None:
        state = staged.state
        if InstructionProjector._current(state) != (
            state.previous,
            state.previous_mode,
        ):
            raise RuntimeError(
                f"instruction projection changed after preflight: {state.destination}"
            )
        missing: list[Path] = []
        cursor = state.destination.parent
        while not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        if cursor.is_symlink() or not cursor.is_dir():
            raise ValueError(
                f"instruction projection parent must be physical: {cursor}"
            )
        for directory in reversed(missing):
            directory.mkdir()
            staged.created_parents = (*staged.created_parents, directory)
        staged.candidate.replace(state.destination)
        staged.installed = True

    @staticmethod
    def _rollback(staged: _StagedFile) -> None:
        destination = staged.state.destination
        if staged.installed:
            current = InstructionProjector._current(staged.state)
            installed = (
                staged.state.desired.encode(),
                staged.state.desired_mode,
            )
            if current != installed:
                raise RuntimeError(
                    f"installed instruction projection changed before rollback: {destination}"
                )
            if staged.backup.exists():
                staged.backup.replace(destination)
            else:
                destination.unlink()
            staged.installed = False
        for directory in reversed(staged.created_parents):
            directory.rmdir()

    @staticmethod
    def _cleanup(staged: _StagedFile) -> None:
        if staged.stage.exists():
            remove_physical(staged.stage)

    def check(self, project: Path) -> None:
        authorization = load_project_authorization(project)
        for state in self._states(authorization):
            if state.drift:
                raise InstructionProjectionDriftError(
                    f"instruction projection differs: {state.destination}"
                )

    def _prepare_publication(self, state: _FileState) -> PreparedPublication:
        staged = self._stage(state)
        return PreparedPublication(
            lambda: self._publish(staged),
            lambda: self._rollback(staged),
            lambda: self._cleanup(staged),
        )

    def publications(
        self, authorization: ProjectAuthorization
    ) -> tuple[Publication, ...]:
        """Preflight and defer every changed instruction publication."""

        return tuple(
            Publication(partial(self._prepare_publication, state))
            for state in self._states(authorization)
            if state.drift
        )

    def apply(self, project: Path) -> None:
        authorization = load_project_authorization(project)
        run_atomic_publications(self.publications(authorization))


__all__ = ("InstructionProjectionDriftError", "InstructionProjector", "capsule")
