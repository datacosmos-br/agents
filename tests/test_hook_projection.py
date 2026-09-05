from __future__ import annotations

import json
import os
import stat
import subprocess
from pathlib import Path
from typing import cast

import pytest

from agents_governance.catalog import Catalog
from agents_governance.commands import audit_command_specs
from agents_governance.governance_config import (
    audit_governance_config,
    load_governance_config,
)
from agents_governance.hook_projection import HookProjector, _capsule
from agents_governance.law_surface import PRELUDE_START, LawSurface
from agents_governance.projection_authorization import (
    PROJECT_SELECTION,
    ProjectAuthorization,
)
from agents_governance.projection_config import load_projection_config
from agents_governance.rules import audit_rule_specs
from agents_governance.runtime import _inventory


def _projector(root: Path, central_root: Path | None = None) -> HookProjector:
    catalog = Catalog(root)
    commands = audit_command_specs(root, (record.name for record in catalog.records()))
    rules = audit_rule_specs(root)
    governance = load_governance_config(root)
    audit_governance_config(root, governance, catalog, commands, rules)
    return HookProjector(
        governance,
        load_projection_config(root),
        commands,
        rules,
        LawSurface.load(root),
        central_root=central_root,
    )


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _authorize(project: Path) -> None:
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir()
    selection.write_text(
        json.dumps(
            {
                "version": 1,
                "agents": [],
                "opt_ins": [],
                "selected_tags": [],
            }
        ),
        encoding="utf-8",
    )


def _hook_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    authorized: bool = True,
) -> tuple[Path, Path, Path]:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    if authorized:
        _authorize(project)
    monkeypatch.setenv("HOME", str(home))
    return root, home, project


def test_hook_projection_preserves_foreign_content_and_reaches_fixed_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _home, project = _hook_project(tmp_path, monkeypatch)
    claude = project / ".claude" / "settings.json"
    claude.parent.mkdir()
    claude.write_text(
        json.dumps(
            {
                "foreign": "preserved",
                "hooks": {
                    "SessionStart": [
                        {"hooks": [{"type": "command", "command": "foreign"}]},
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    agents = project / "AGENTS.md"
    agents.write_text("# Existing project law\n", encoding="utf-8")
    antigravity_path = project / ".agents" / "hooks.json"
    antigravity_path.write_text(
        json.dumps({"foreign-owner": {"PreInvocation": []}}), encoding="utf-8"
    )
    projector = _projector(root)

    projector.apply(project)

    assert (
        (project / "AGENTS.md")
        .read_text(encoding="utf-8")
        .startswith(PRELUDE_START + "\n")
    )
    assert (
        (project / "CLAUDE.md")
        .read_text(encoding="utf-8")
        .startswith(PRELUDE_START + "\n")
    )
    manifest = _json(project / ".agents" / "law-surface.json")
    assert manifest["owner"] == "agents-governance"
    assert manifest["prelude_start"] == PRELUDE_START
    projector.check(project)
    first_mtime = (project / ".codex" / "hooks.json").stat().st_mtime_ns
    projector.apply(project)

    assert (project / ".codex" / "hooks.json").stat().st_mtime_ns == first_mtime
    rendered_claude = _json(claude)
    assert rendered_claude["foreign"] == "preserved"
    session_groups = rendered_claude["hooks"]["SessionStart"]  # type: ignore[index]
    assert any(
        group["hooks"][0].get("command") == "foreign" for group in session_groups
    )
    rendered_agents = agents.read_text()
    assert rendered_agents.startswith(PRELUDE_START + "\n")
    assert "# Existing project law\n" in rendered_agents
    assert rendered_agents.count("AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN") == 1

    copilot = _json(project / ".github" / "hooks" / "aihub-governance.json")
    copilot_handler = copilot["hooks"]["sessionStart"][0]  # type: ignore[index]
    assert "bash" in copilot_handler
    assert "command" not in copilot_handler
    antigravity = _json(antigravity_path)
    assert set(antigravity) == {"aihub-governance", "foreign-owner"}
    assert "PreInvocation" in antigravity["aihub-governance"]  # type: ignore[operator]
    manifest = _json(project / ".agents" / ".hooks.json.agents-governance.json")
    assert manifest["version"] == 3
    assert manifest["events"]["subagent_start"]["status"] == "SUPPORTED"  # type: ignore[index]

    plugin = (project / ".opencode" / "plugins" / "aihub-governance.ts").read_text(
        encoding="utf-8"
    )
    assert "output.system[0]" in plugin
    assert "experimental.session.compacting" in plugin
    assert "chat.message" not in plugin
    assert "event: async" not in plugin


def test_foreign_hook_command_containing_managed_path_is_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, home, project = _hook_project(tmp_path, monkeypatch)
    projector = _projector(root)
    projector.apply(project)
    settings_path = home / ".claude" / "settings.json"
    settings = _json(settings_path)
    foreign = {
        "hooks": [
            {
                "type": "command",
                "command": (f"echo {home / '.claude' / 'aihub-hooks' / 'foreign.py'}"),
            }
        ]
    }
    settings["hooks"]["SessionStart"].append(foreign)  # type: ignore[index]
    settings_path.write_text(json.dumps(settings), encoding="utf-8")

    projector.apply(project)

    rendered = _json(settings_path)
    assert foreign in rendered["hooks"]["SessionStart"]  # type: ignore[index]


def test_personal_merged_configs_preserve_existing_mode_and_default_private(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, home, project = _hook_project(tmp_path, monkeypatch, authorized=False)
    claude = home / ".claude" / "settings.json"
    claude.parent.mkdir()
    claude.write_text('{"mcpServers": {}}', encoding="utf-8")
    claude.chmod(0o640)

    _projector(root).apply(project)

    assert stat.S_IMODE(claude.stat().st_mode) == 0o640
    for destination in (
        home / ".codex" / "hooks.json",
        home / ".cursor" / "hooks.json",
        home / ".gemini" / "settings.json",
    ):
        assert stat.S_IMODE(destination.stat().st_mode) == 0o600


def test_existing_hook_config_is_replaced_without_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, home, project = _hook_project(tmp_path, monkeypatch, authorized=False)
    destination = home / ".claude" / "settings.json"
    destination.parent.mkdir()
    destination.write_text("{}", encoding="utf-8")
    original_unlink = Path.unlink

    def reject_destination_unlink(path: Path, *args: object, **kwargs: object) -> None:
        if path == destination:
            raise AssertionError("existing config must have one atomic replace point")
        original_unlink(path, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "unlink", reject_destination_unlink)

    _projector(root).apply(project)

    assert _json(destination)["hooks"]


def test_broken_hook_symlink_created_after_preflight_is_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _home, project = _hook_project(tmp_path, monkeypatch)
    destination = project / "AGENTS.md"
    outside = project / "missing-external-target"
    original_current = HookProjector._current
    injected = False

    def race(state: object) -> tuple[bytes | None, int | None]:
        nonlocal injected
        if not injected and state.destination == destination:  # type: ignore[attr-defined]
            destination.symlink_to(outside)
            injected = True
        return original_current(state)  # type: ignore[arg-type]

    monkeypatch.setattr(HookProjector, "_current", staticmethod(race))

    with pytest.raises(RuntimeError, match="symlink"):
        _projector(root).apply(project)

    assert destination.is_symlink()
    assert destination.readlink() == outside
    assert not outside.exists()


def test_absent_project_authorization_projects_personal_hooks_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, home, project = _hook_project(tmp_path, monkeypatch, authorized=False)

    _projector(root).apply(project)

    assert (home / ".codex" / "hooks.json").is_file()
    assert not (project / ".codex").exists()
    assert not (project / ".claude").exists()


def test_generated_hook_executes_and_malformed_input_fails_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _home, project = _hook_project(tmp_path, monkeypatch)
    projector = _projector(root)
    projector.apply(project)
    settings = _json(_home / ".claude" / "settings.json")
    command = settings["hooks"]["SessionStart"][-1]["hooks"][0]["command"]  # type: ignore[index]
    # Why (ag-o08): the personal command anchors on the ${HOME} placeholder the
    # projection config already emits; the physical home never appears.
    assert command == 'python3 "${HOME}/.claude/aihub-hooks/claude-sessionstart.py"'
    assert str(_home) not in command

    accepted = subprocess.run(
        command,
        shell=True,
        env=os.environ,
        input="{}",
        text=True,
        capture_output=True,
        check=True,
    )
    output = json.loads(accepted.stdout)
    assert "additionalContext" in output["hookSpecificOutput"]

    rejected = subprocess.run(
        command,
        shell=True,
        env=os.environ,
        input="[]",
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode != 0
    assert "TypeError: hook input must be a JSON object" in rejected.stderr


def test_project_claude_hooks_are_retired_while_foreign_settings_survive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _home, project = _hook_project(tmp_path, monkeypatch)
    projector = _projector(root)
    from agents_governance.agent_profiles import AgentProvider
    from agents_governance.projection_config import ProjectionContext

    legacy = projector._plan(
        AgentProvider.CLAUDE,
        ProjectionContext.PROJECT,
        project,
        _capsule(projector.governance, projector.commands, projector.rules),
    )
    for path, (content, mode) in legacy.desired.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        path.chmod(mode)
    settings_path = project / ".claude" / "settings.json"
    settings = _json(settings_path)
    settings["foreign"] = "preserved"
    settings_path.write_text(json.dumps(settings), encoding="utf-8")

    _projector(root).apply(project)

    assert _json(settings_path) == {"foreign": "preserved"}
    assert not tuple((project / ".claude" / "aihub-hooks").glob("*"))
    assert not (project / ".claude" / ".settings.json.agents-governance.json").exists()


def test_modified_managed_hook_and_instruction_region_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _home, project = _hook_project(tmp_path, monkeypatch)
    projector = _projector(root)
    projector.apply(project)
    script = next((project / ".codex" / "aihub-hooks").glob("*.py"))
    script.write_text(script.read_text() + "# local edit\n", encoding="utf-8")

    with pytest.raises(ValueError, match="managed hook artifact was modified"):
        projector.apply(project)

    script.write_text(
        script.read_text().removesuffix("# local edit\n"), encoding="utf-8"
    )
    agents = project / "AGENTS.md"
    agents.write_text(
        agents.read_text().replace("The operator's newest", "Modified newest"),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="instruction capsule was modified"):
        projector.apply(project)


def _projector_without_codex_prompt(root: Path) -> HookProjector:
    import dataclasses
    from types import MappingProxyType

    from agents_governance.agent_profiles import AgentProvider
    from agents_governance.projection_config import (
        ProjectionContext,
        ProjectionStatus,
        ProjectionSurface,
    )

    base = _projector(root)
    key = (
        AgentProvider.CODEX,
        ProjectionContext.PROJECT,
        ProjectionSurface.HOOKS,
    )
    cell = base.config.cells[key]
    source_events = cell.events
    if source_events is None:
        raise AssertionError("projection cell declares no events")
    events = {
        name: (
            dataclasses.replace(
                event, status=ProjectionStatus.UNSUPPORTED, native=(), coverage=None
            )
            if name == "prompt_submit"
            else event
        )
        for name, event in source_events.items()
    }
    mutated = dataclasses.replace(cell, events=MappingProxyType(events))
    cells = dict(base.config.cells)
    cells[key] = mutated
    config = dataclasses.replace(base.config, cells=MappingProxyType(cells))
    return HookProjector(
        base.governance,
        config,
        base.commands,
        base.rules,
        LawSurface.load(root),
    )


def test_retired_hook_event_script_is_removed_and_foreign_survives(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _home, project = _hook_project(tmp_path, monkeypatch)
    projector = _projector(root)
    projector.apply(project)
    hooks_dir = project / ".codex" / "aihub-hooks"
    retired = hooks_dir / "codex-userpromptsubmit.py"
    assert retired.is_file()
    foreign = hooks_dir / "foreign-tool.py"
    foreign.write_text("# foreign authored\n", encoding="utf-8")

    retired_projector = _projector_without_codex_prompt(root)
    retired_projector.apply(project)

    assert not retired.exists()
    assert foreign.is_file()
    manifest = _json(project / ".codex" / ".hooks.json.agents-governance.json")
    assert all(
        "userpromptsubmit" not in key
        for key in cast("dict[str, object]", manifest["managed"])
    )
    retired_projector.check(project)


def test_modified_retired_artifact_fails_loud_and_preserves_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _home, project = _hook_project(tmp_path, monkeypatch)
    projector = _projector(root)
    projector.apply(project)
    retired = project / ".codex" / "aihub-hooks" / "codex-userpromptsubmit.py"

    retired_projector = _projector_without_codex_prompt(root)
    retired.write_text(retired.read_text() + "# tampered\n", encoding="utf-8")

    with pytest.raises(ValueError, match="retired managed hook artifact was modified"):
        retired_projector.apply(project)

    assert "# tampered" in retired.read_text()


def test_config_path_change_retires_artifacts_managed_at_the_old_location(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _home, project = _hook_project(tmp_path, monkeypatch)
    projector = _projector(root)
    projector.apply(project)
    manifest_path = project / ".codex" / ".hooks.json.agents-governance.json"
    manifest = _json(manifest_path)
    canonical = ".codex/aihub-hooks/codex-userpromptsubmit.py"
    relocated = ".codex/aihub-hooks/old-location-codex-userpromptsubmit.py"
    managed = dict(cast("dict[str, object]", manifest["managed"]))
    managed[relocated] = managed.pop(canonical)
    manifest["managed"] = managed
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    hooks_dir = project / ".codex" / "aihub-hooks"
    (hooks_dir / Path(canonical).name).rename(hooks_dir / Path(relocated).name)

    projector.apply(project)

    assert not (hooks_dir / Path(relocated).name).exists()
    assert (hooks_dir / Path(canonical).name).is_file()
    converged = _json(manifest_path)
    assert canonical in converged["managed"]  # type: ignore[operator]
    assert relocated not in converged["managed"]  # type: ignore[operator]
    projector.check(project)


def test_capsule_carries_approval_provenance_for_every_bootstrap_rule() -> None:
    """The per-turn delivery surface must let a reader order rules by recency.

    The capsule is what reaches the model at session start and on every
    prompt. Approval provenance written only into the on-disk projections
    never arrives there, so recency stays unresolvable at the point of use.
    """

    root = Path(__file__).resolve().parent.parent
    inventory = _inventory(root)
    capsule = _capsule(inventory.governance, inventory.commands, inventory.rules)

    assert capsule.count("<!-- aihub.approval: ") == len(
        inventory.governance.bootstrap_rules
    )
    for identity in inventory.governance.bootstrap_rules:
        assert f"## Rule `{identity}`" in capsule


def test_central_source_never_merges_capsules_into_its_own_law(
    tmp_path: Path,
) -> None:
    root = Path(__file__).resolve().parents[1]
    consumer_project = tmp_path / "consumer"
    consumer_project.mkdir()
    selection = b'{"version": 1, "agents": [], "opt_ins": [], "selected_tags": []}'
    consumer = _projector(root)
    consumer_plans = consumer._plans(
        ProjectAuthorization(
            consumer_project,
            consumer_project / PROJECT_SELECTION,
            selection,
        )
    )
    assert any(plan.config == consumer_project / "AGENTS.md" for plan in consumer_plans)
    assert any(plan.config == consumer_project / "CLAUDE.md" for plan in consumer_plans)

    central = _projector(root, central_root=root)
    central_plans = central._plans(
        ProjectAuthorization(root, root / PROJECT_SELECTION, selection)
    )
    assert central_plans
    assert all(
        plan.config not in {root / "AGENTS.md", root / "CLAUDE.md"}
        for plan in central_plans
    )
    assert any(
        root / ".agents" / "law-surface.json" in plan.desired for plan in central_plans
    )


def _first_command(config: Path, *keys: str | int) -> str:
    node = cast(object, _json(config))
    for key in keys:
        if isinstance(key, int):
            assert isinstance(node, list)
            node = node[key]
        else:
            assert isinstance(node, dict)
            node = node[key]
    assert isinstance(node, str)
    return node


def _run_hook(command: str, *, env: dict[str, str], cwd: Path) -> dict[str, object]:
    completed = subprocess.run(
        command,
        shell=True,
        env=env,
        cwd=cwd,
        input="{}",
        text=True,
        capture_output=True,
        check=True,
    )
    return cast(dict[str, object], json.loads(completed.stdout))


def test_project_hook_commands_resolve_from_provider_root_tokens(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Why (ag-o08): project hooks anchor on provider root tokens, never on the
    physical checkout path, so the same tracked file works on every machine."""
    root, home, project = _hook_project(tmp_path, monkeypatch)
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    _projector(root).apply(project)
    base = {**os.environ, "HOME": str(home)}

    gemini = _first_command(
        project / ".gemini" / "settings.json",
        "hooks",
        "SessionStart",
        -1,
        "hooks",
        0,
        "command",
    )
    assert (
        gemini
        == 'python3 "${GEMINI_PROJECT_DIR}/.gemini/aihub-hooks/gemini-sessionstart.py"'
    )
    _run_hook(gemini, env={**base, "GEMINI_PROJECT_DIR": str(project)}, cwd=tmp_path)

    cursor = _first_command(
        project / ".cursor" / "hooks.json", "hooks", "sessionStart", -1, "command"
    )
    assert (
        cursor
        == 'python3 "${CURSOR_PROJECT_DIR}/.cursor/aihub-hooks/cursor-sessionstart.py"'
    )
    _run_hook(cursor, env={**base, "CURSOR_PROJECT_DIR": str(project)}, cwd=tmp_path)

    codex = _first_command(
        project / ".codex" / "hooks.json",
        "hooks",
        "SessionStart",
        -1,
        "hooks",
        0,
        "command",
    )
    assert codex == (
        'python3 "$(git rev-parse --show-toplevel)/.codex/aihub-hooks/codex-sessionstart.py"'
    )
    nested = project / "nested"
    nested.mkdir()
    _run_hook(codex, env=base, cwd=nested)

    copilot_config = project / ".github" / "hooks" / "aihub-governance.json"
    copilot_entry = cast(
        dict[str, object],
        cast(
            list[object],
            cast(dict[str, object], _json(copilot_config)["hooks"])["sessionStart"],
        )[0],
    )
    assert (
        copilot_entry["bash"]
        == 'python3 "./.github/hooks/aihub-hooks/copilot-sessionstart.py"'
    )
    assert copilot_entry["cwd"] == "."
    _run_hook(cast(str, copilot_entry["bash"]), env=base, cwd=project)


def test_emitted_hook_artifacts_never_embed_physical_boundaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, home, project = _hook_project(tmp_path, monkeypatch)
    _projector(root).apply(project)

    offenders = sorted(
        str(path)
        for boundary in (home, project)
        for path in boundary.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and (
            str(home).encode() in path.read_bytes()
            or str(project).encode() in path.read_bytes()
        )
    )
    assert offenders == []


def test_hook_command_root_is_required_for_every_planned_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from agents_governance.agent_profiles import AgentProvider
    from agents_governance.hook_projection import _portable_script_reference
    from agents_governance.projection_config import ProjectionContext

    _root, _home, project = _hook_project(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="hook command root is undefined"):
        _portable_script_reference(
            AgentProvider.OPENCODE,
            ProjectionContext.PROJECT,
            project,
            project / ".opencode" / "aihub-hooks" / "x.py",
        )
    with pytest.raises(ValueError):
        _portable_script_reference(
            AgentProvider.CLAUDE, ProjectionContext.PROJECT, project, tmp_path / "x.py"
        )
