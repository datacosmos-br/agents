"""Provider-native hook projection owned exclusively by optionless sync."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import stat
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import cast

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
from .projection_authorization import project_projection_authorized
from .projection_config import (
    ProjectionConfig,
    ProjectionContext,
    ProjectionStatus,
    ProjectionSurface,
    RuleLayout,
)
from .rules import RuleSpec

_MANIFEST_VERSION = 2
_OWNER = "agents-governance"
_INSTRUCTIONS_BEGIN = "<!-- AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN -->"
_INSTRUCTIONS_END = "<!-- AIHUB-GOVERNANCE-INSTRUCTIONS-END -->"
_CAPSULE_PREFIX = "<!-- AIHUB-GOVERNANCE-CAPSULE v1 sha256:"


class HookProjectionDriftError(RuntimeError):
    """A provider hook projection differs from the canonical capsule."""


@dataclass(frozen=True)
class HookPlan:
    provider: AgentProvider
    context: ProjectionContext
    boundary: Path
    config: Path
    desired: dict[Path, tuple[str, int]]


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


def _mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{label} must be an object with string keys")
    return cast(dict[str, object], value)


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
            raise ValueError(f"hook projection path symlink forbidden: {cursor}")
        if not cursor.exists():
            break
    return target


def _capsule(
    governance: GovernanceConfig,
    commands: tuple[CommandSpec, ...],
    rules: tuple[RuleSpec, ...],
) -> str:
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
            ("", f"## Rule `{identity}`", "", by_identity[identity].body.strip())
        )
    sections.extend(("", "## Capability indexes", ""))
    sections.append("Skills: " + ", ".join(governance.bootstrap_skills))
    sections.append("Commands: " + ", ".join(command.name for command in commands))
    body = "\n".join(sections).rstrip()
    digest = _digest_text(body)
    rendered = f"<!-- AIHUB-GOVERNANCE-CAPSULE v1 sha256:{digest} -->\n{body}\n"
    if len(rendered) > 10_000:
        raise ValueError(
            f"governance capsule exceeds provider hook limit: {len(rendered)} characters"
        )
    return rendered


def _script_response(provider: AgentProvider, event: str, capsule: str) -> object:
    if provider in {AgentProvider.CLAUDE, AgentProvider.CODEX}:
        inject = event in {"SessionStart", "UserPromptSubmit", "SubagentStart"}
        return (
            {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "additionalContext": capsule,
                }
            }
            if inject
            else {}
        )
    if provider is AgentProvider.GEMINI:
        inject = event in {"SessionStart", "BeforeAgent"}
        return (
            {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "additionalContext": capsule,
                }
            }
            if inject
            else {}
        )
    if provider is AgentProvider.CURSOR:
        if event == "sessionStart":
            return {"additional_context": capsule}
        if event == "beforeSubmitPrompt":
            return {"continue": True}
        if event == "subagentStart":
            return {"permission": "allow"}
        return {}
    if provider is AgentProvider.COPILOT:
        return (
            {"additionalContext": capsule}
            if event in {"sessionStart", "subagentStart"}
            else {}
        )
    if provider is AgentProvider.ANTIGRAVITY:
        return {"injectSteps": [{"ephemeralMessage": capsule}]}
    raise ValueError(f"provider does not use command hook scripts: {provider.value}")


def _script(provider: AgentProvider, event: str, capsule: str) -> str:
    response = json.dumps(
        _script_response(provider, event, capsule),
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return (
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n\n"
        "payload = json.load(sys.stdin)\n"
        "if not isinstance(payload, dict):\n"
        "    raise TypeError('hook input must be a JSON object')\n"
        f"response = json.loads({response!r})\n"
        "json.dump(response, sys.stdout, ensure_ascii=False, separators=(',', ':'))\n"
        "sys.stdout.write('\\n')\n"
    )


def _event_names(cell_events: object) -> tuple[str, ...]:
    if cell_events is None:
        raise ValueError("supported hook cell has no event contract")
    events = cast(dict[str, tuple[str, ...]], cell_events)
    return tuple(sorted({event for values in events.values() for event in values}))


def _command(path: Path) -> str:
    return f"python3 {shlex.quote(str(path))}"


def _managed_command(value: object, script_root: Path) -> bool:
    if not isinstance(value, dict):
        return False
    command = value.get("command")
    return isinstance(command, str) and str(script_root) in command


def _nested_config(
    provider: AgentProvider,
    current: dict[str, object],
    events: tuple[str, ...],
    scripts: dict[str, Path],
) -> tuple[dict[str, object], dict[str, object]]:
    result = dict(current)
    hooks = _mapping(result.get("hooks", {}), f"{provider.value} hooks")
    merged: dict[str, object] = dict(hooks)
    managed: dict[str, object] = {}
    for event in events:
        existing = merged.get(event, [])
        if not isinstance(existing, list):
            raise TypeError(f"{provider.value} hooks.{event} must be an array")
        kept: list[object] = []
        for raw_group in existing:
            group = _mapping(raw_group, f"{provider.value} hooks.{event} group")
            handlers = group.get("hooks")
            if not isinstance(handlers, list):
                raise TypeError(
                    f"{provider.value} hooks.{event}.hooks must be an array"
                )
            remaining = [
                handler
                for handler in handlers
                if not _managed_command(handler, scripts[event].parent)
            ]
            if remaining:
                retained = dict(group)
                retained["hooks"] = remaining
                kept.append(retained)
        handler: dict[str, object] = {
            "type": "command",
            "command": _command(scripts[event]),
        }
        if provider is AgentProvider.CODEX:
            handler["statusMessage"] = "Applying synchronized governance"
        elif provider is AgentProvider.CLAUDE:
            handler["statusMessage"] = "Applying synchronized governance"
            handler["timeout"] = 10
        else:
            handler["name"] = f"aihub-governance-{event.lower()}"
            handler["timeout"] = 10_000
        managed_group: dict[str, object] = {"hooks": [handler]}
        matchers = {
            "SessionStart": "startup|resume|clear|compact",
            "BeforeAgent": "*",
        }
        if event in matchers:
            managed_group["matcher"] = matchers[event]
        kept.append(managed_group)
        managed[event] = managed_group
        merged[event] = kept
    result["hooks"] = merged
    return result, managed


def _cursor_config(
    current: dict[str, object], events: tuple[str, ...], scripts: dict[str, Path]
) -> tuple[dict[str, object], dict[str, object]]:
    result = dict(current)
    version = result.get("version", 1)
    if version != 1:
        raise ValueError("Cursor hooks version must equal 1")
    result["version"] = 1
    hooks = _mapping(result.get("hooks", {}), "Cursor hooks")
    merged: dict[str, object] = dict(hooks)
    managed: dict[str, object] = {}
    for event in events:
        existing = merged.get(event, [])
        if not isinstance(existing, list):
            raise TypeError(f"Cursor hooks.{event} must be an array")
        kept = [
            entry
            for entry in existing
            if not _managed_command(entry, scripts[event].parent)
        ]
        entry = {
            "command": _command(scripts[event]),
            "failClosed": True,
            "timeout": 10,
        }
        kept.append(entry)
        managed[event] = entry
        merged[event] = kept
    result["hooks"] = merged
    return result, managed


def _owned_json(
    provider: AgentProvider, events: tuple[str, ...], scripts: dict[str, Path]
) -> dict[str, object]:
    if provider is AgentProvider.COPILOT:
        return {
            "version": 1,
            "hooks": {
                event: [
                    {
                        "type": "command",
                        "bash": _command(scripts[event]),
                        "timeoutSec": 10,
                    }
                ]
                for event in events
            },
        }
    if provider is AgentProvider.ANTIGRAVITY:
        return {
            "aihub-governance": {
                "PreInvocation": [
                    {
                        "type": "command",
                        "command": _command(scripts["PreInvocation"]),
                        "timeout": 10,
                    }
                ]
            }
        }
    raise ValueError(f"provider does not own a standalone hook JSON: {provider.value}")


def _opencode_plugin(capsule: str) -> str:
    encoded = json.dumps(capsule, ensure_ascii=False)
    digest = _digest_text(capsule)
    return f'''const CAPSULE = {encoded};
const DIGEST = "{digest}";

export const AiHubGovernance = async () => ({{
  "experimental.chat.system.transform": async (_input, output) => {{
    const block = `<!-- AIHUB-GOVERNANCE ${{DIGEST}} -->\\n${{CAPSULE}}`;
    if (!output.system.some((entry) => entry.includes(DIGEST))) {{
      if (output.system.length === 0) output.system.push(block);
      else output.system[0] = `${{output.system[0]}}\\n\\n${{block}}`;
    }}
  }},
  "experimental.session.compacting": async (_input, output) => {{
    if (!output.context.some((entry) => entry.includes(DIGEST))) {{
      output.context.push(`<!-- AIHUB-GOVERNANCE ${{DIGEST}} -->\\n${{CAPSULE}}`);
    }}
  }},
}});
'''


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists() and not path.is_symlink():
        return {}
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"hook config must be a physical file: {path}")
    return _mapping(json.loads(path.read_text(encoding="utf-8")), str(path))


def _manifest_path(config: Path) -> Path:
    return config.with_name(f".{config.name}.agents-governance.json")


def _read_manifest(path: Path) -> dict[str, object] | None:
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"hook manifest must be a physical file: {path}")
    payload = _mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
    expected = {
        "config",
        "context",
        "coverage",
        "entries",
        "managed",
        "owner",
        "provider",
        "version",
    }
    if set(payload) != expected:
        raise ValueError(f"hook manifest fields are invalid: {path}")
    if payload["version"] != _MANIFEST_VERSION or payload["owner"] != _OWNER:
        raise ValueError(f"hook manifest owner/version is invalid: {path}")
    _mapping(payload["coverage"], f"{path}: coverage")
    _mapping(payload["entries"], f"{path}: entries")
    managed = _mapping(payload["managed"], f"{path}: managed")
    for relative, raw in managed.items():
        entry = _mapping(raw, f"{path}: managed.{relative}")
        if set(entry) != {"digest", "mode"}:
            raise ValueError(f"hook manifest managed fields are invalid: {relative}")
        digest = entry["digest"]
        mode = entry["mode"]
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(f"hook manifest digest is invalid: {relative}")
        if not isinstance(mode, str) or len(mode) != 4:
            raise ValueError(f"hook manifest mode is invalid: {relative}")
    return payload


def _validate_previous(
    manifest: dict[str, object] | None,
    *,
    boundary: Path,
    config: Path,
    provider: AgentProvider,
    context: ProjectionContext,
    current: dict[str, object] | None,
) -> None:
    if manifest is None:
        return
    identity = {
        "config": config.name,
        "context": context.value,
        "provider": provider.value,
    }
    for field, expected in identity.items():
        if manifest[field] != expected:
            raise ValueError(f"hook manifest authority differs at {config}: {field}")
    for relative, raw in _mapping(manifest["managed"], "hook managed files").items():
        path = _destination(boundary, relative, ProjectionContext.PROJECT)
        if path.is_symlink() or not path.is_file():
            raise ValueError(
                f"managed hook artifact is missing or non-physical: {path}"
            )
        entry = _mapping(raw, f"managed hook artifact {relative}")
        actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        actual_mode = f"{stat.S_IMODE(path.lstat().st_mode):04o}"
        if actual_digest != entry["digest"] or actual_mode != entry["mode"]:
            raise ValueError(f"managed hook artifact was modified: {path}")
    entries = _mapping(manifest["entries"], "hook managed entries")
    if entries:
        if current is None:
            raise ValueError(f"managed hook config is missing: {config}")
        hooks = _mapping(current.get("hooks", {}), f"{config}: hooks")
        for event, managed_entry in entries.items():
            existing = hooks.get(event)
            if not isinstance(existing, list) or existing.count(managed_entry) != 1:
                raise ValueError(f"managed hook entry was modified: {config}:{event}")


def _render_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _reject_unowned_exact(
    manifest: dict[str, object] | None, paths: Mapping[Path, tuple[str, int]]
) -> None:
    if manifest is not None:
        return
    for path in paths:
        if path.exists() or path.is_symlink():
            raise ValueError(f"foreign hook projection collision: {path}")


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


def _merge_instruction(path: Path, capsule: str) -> str:
    current = _read_instruction(path)
    begin_count = current.count(_INSTRUCTIONS_BEGIN)
    end_count = current.count(_INSTRUCTIONS_END)
    if begin_count != end_count or begin_count > 1:
        raise ValueError(f"managed instruction region is malformed: {path}")
    block = f"{_INSTRUCTIONS_BEGIN}\n{capsule.rstrip()}\n{_INSTRUCTIONS_END}"
    if begin_count == 0:
        if not current:
            return f"{block}\n"
        separator = "\n" if current.endswith("\n") else "\n\n"
        return f"{current}{separator}{block}\n"
    before, remainder = current.split(_INSTRUCTIONS_BEGIN, 1)
    owned, after = remainder.split(_INSTRUCTIONS_END, 1)
    _validate_capsule(owned.strip(), path)
    return f"{before}{block}{after}"


class HookProjector:
    """Compile and atomically publish native hook artifacts for seven providers."""

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

    def _plan(
        self,
        provider: AgentProvider,
        context: ProjectionContext,
        boundary: Path,
        capsule: str,
    ) -> HookPlan:
        cell = self.config.cell(provider, context, ProjectionSurface.HOOKS)
        if cell.status is ProjectionStatus.UNSUPPORTED:
            raise ValueError(
                f"hook support is required for {provider.value}/{context.value}"
            )
        assert cell.path is not None
        assert cell.coverage is not None
        config = _destination(boundary, cell.path, context)
        manifest_path = _manifest_path(config)
        previous_manifest = _read_manifest(manifest_path)
        events = _event_names(cell.events)
        if provider is AgentProvider.OPENCODE:
            _validate_previous(
                previous_manifest,
                boundary=boundary,
                config=config,
                provider=provider,
                context=context,
                current=None,
            )
            desired: dict[Path, tuple[str, int]] = {
                config: (_opencode_plugin(capsule), 0o644)
            }
            exact = dict(desired)
            _reject_unowned_exact(previous_manifest, exact)
            entries: dict[str, object] = {}
        else:
            script_root = config.parent / "aihub-hooks"
            scripts = {
                event: script_root
                / f"{provider.value}-{event.lower().replace('.', '-')}.py"
                for event in events
            }
            desired = {
                path: (_script(provider, event, capsule), 0o755)
                for event, path in scripts.items()
            }
            exact = dict(desired)
            entries = {}
            merged_provider = provider in {
                AgentProvider.CLAUDE,
                AgentProvider.CODEX,
                AgentProvider.GEMINI,
                AgentProvider.CURSOR,
            }
            current = _read_json(config) if merged_provider else None
            _validate_previous(
                previous_manifest,
                boundary=boundary,
                config=config,
                provider=provider,
                context=context,
                current=current,
            )
            if provider in {
                AgentProvider.CLAUDE,
                AgentProvider.CODEX,
                AgentProvider.GEMINI,
            }:
                assert current is not None
                rendered, entries = _nested_config(provider, current, events, scripts)
            elif provider is AgentProvider.CURSOR:
                assert current is not None
                rendered, entries = _cursor_config(current, events, scripts)
            else:
                rendered = _owned_json(provider, events, scripts)
            desired[config] = (_render_json(rendered), 0o644)
            if not merged_provider:
                exact[config] = desired[config]
            if provider is AgentProvider.ANTIGRAVITY:
                marker = config.parent / "plugin.json"
                desired[marker] = (_render_json({"name": "aihub-governance"}), 0o644)
                exact[marker] = desired[marker]
            _reject_unowned_exact(previous_manifest, exact)
        manifest_payload = {
            "version": _MANIFEST_VERSION,
            "owner": _OWNER,
            "provider": provider.value,
            "context": context.value,
            "config": config.name,
            "coverage": {
                logical_event: coverage.value
                for logical_event, coverage in sorted(cell.coverage.items())
            },
            "entries": entries,
            "managed": {
                path.relative_to(boundary).as_posix(): {
                    "digest": _digest_text(text),
                    "mode": f"{mode:04o}",
                }
                for path, (text, mode) in sorted(
                    exact.items(), key=lambda item: str(item[0])
                )
            },
        }
        desired[manifest_path] = (_render_json(manifest_payload), 0o644)
        return HookPlan(provider, context, boundary, config, desired)

    def _plans(self, project: Path) -> tuple[HookPlan, ...]:
        home = _physical_boundary(Path.home(), "personal home")
        repository = _physical_boundary(project, "project root")
        project_authorized = project_projection_authorized(repository)
        capsule = _capsule(self.governance, self.commands, self.rules)
        hooks = tuple(
            self._plan(
                provider,
                context,
                home if context is ProjectionContext.PERSONAL else repository,
                capsule,
            )
            for provider in AgentProvider
            for context in ProjectionContext
            if context is ProjectionContext.PERSONAL or project_authorized
        )
        instructions: list[HookPlan] = []
        for provider in AgentProvider:
            for context in ProjectionContext:
                if context is ProjectionContext.PROJECT and not project_authorized:
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
                instructions.append(
                    HookPlan(
                        provider,
                        context,
                        boundary,
                        destination,
                        {
                            destination: (
                                _merge_instruction(destination, capsule),
                                0o644,
                            )
                        },
                    )
                )
        return (*hooks, *instructions)

    @staticmethod
    def _state(destination: Path, desired: str, mode: int) -> _FileState:
        if destination.is_symlink():
            raise ValueError(f"hook projection symlink forbidden: {destination}")
        if destination.exists():
            metadata = destination.lstat()
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError(
                    f"hook projection target must be a regular file: {destination}"
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

    def _states(self, project: Path) -> tuple[_FileState, ...]:
        desired: dict[Path, tuple[str, int]] = {}
        for plan in self._plans(project):
            for destination, rendered in plan.desired.items():
                previous = desired.get(destination)
                if previous is not None and previous != rendered:
                    raise ValueError(f"conflicting hook projection: {destination}")
                desired[destination] = rendered
        return tuple(
            self._state(destination, text, mode)
            for destination, (text, mode) in sorted(
                desired.items(), key=lambda item: str(item[0])
            )
        )

    @staticmethod
    def _stage(state: _FileState) -> _StagedFile:
        ancestor = state.destination.parent
        while not ancestor.exists():
            ancestor = ancestor.parent
        if ancestor.is_symlink() or not ancestor.is_dir():
            raise ValueError(f"hook staging ancestor must be physical: {ancestor}")
        stage = Path(tempfile.mkdtemp(prefix=".agents-hook-stage.", dir=ancestor))
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
        if not destination.exists():
            return None, None
        if destination.is_symlink() or not destination.is_file():
            raise RuntimeError(
                f"hook projection changed type after preflight: {destination}"
            )
        return destination.read_bytes(), stat.S_IMODE(destination.lstat().st_mode)

    @staticmethod
    def _publish(staged: _StagedFile) -> None:
        state = staged.state
        if HookProjector._current(state) != (state.previous, state.previous_mode):
            raise RuntimeError(
                f"hook projection changed after preflight: {state.destination}"
            )
        missing: list[Path] = []
        cursor = state.destination.parent
        while not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        if cursor.is_symlink() or not cursor.is_dir():
            raise ValueError(f"hook projection parent must be physical: {cursor}")
        for directory in reversed(missing):
            directory.mkdir()
            staged.created_parents = (*staged.created_parents, directory)
        if state.destination.exists():
            state.destination.unlink()
        staged.candidate.replace(state.destination)
        staged.installed = True

    @staticmethod
    def _rollback(staged: _StagedFile) -> None:
        destination = staged.state.destination
        if staged.installed and destination.exists():
            destination.unlink()
            staged.installed = False
        if staged.backup.exists():
            staged.backup.replace(destination)
        for directory in reversed(staged.created_parents):
            directory.rmdir()

    @staticmethod
    def _cleanup(staged: _StagedFile) -> None:
        if staged.stage.exists():
            remove_physical(staged.stage)

    def check(self, project: Path) -> None:
        for state in self._states(project):
            if state.drift:
                raise HookProjectionDriftError(
                    f"hook projection differs: {state.destination}"
                )

    def _prepare_publication(self, state: _FileState) -> PreparedPublication:
        staged = self._stage(state)
        return PreparedPublication(
            lambda: self._publish(staged),
            lambda: self._rollback(staged),
            lambda: self._cleanup(staged),
        )

    def publications(self, project: Path) -> tuple[Publication, ...]:
        """Preflight and defer every changed provider-hook publication."""

        return tuple(
            Publication(partial(self._prepare_publication, state))
            for state in self._states(project)
            if state.drift
        )

    def apply(self, project: Path) -> None:
        run_atomic_publications(self.publications(project))


__all__ = ("HookProjectionDriftError", "HookProjector")
