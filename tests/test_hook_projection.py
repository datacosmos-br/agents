from __future__ import annotations

import json
import shlex
import stat
import subprocess
from pathlib import Path

import pytest

from agents_governance.catalog import Catalog
from agents_governance.commands import audit_command_specs
from agents_governance.governance_config import (
    audit_governance_config,
    load_governance_config,
)
from agents_governance.hook_projection import HookProjector
from agents_governance.projection_config import load_projection_config
from agents_governance.rules import audit_rule_specs


def _projector(root: Path) -> HookProjector:
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


def test_hook_projection_preserves_foreign_content_and_reaches_fixed_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _authorize(project)
    monkeypatch.setenv("HOME", str(home))
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
    assert agents.read_text().startswith("# Existing project law\n")
    assert agents.read_text().count("AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN") == 1

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
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _authorize(project)
    monkeypatch.setenv("HOME", str(home))
    projector = _projector(root)
    projector.apply(project)
    settings_path = project / ".claude" / "settings.json"
    settings = _json(settings_path)
    foreign = {
        "hooks": [
            {
                "type": "command",
                "command": (
                    f"echo {project / '.claude' / 'aihub-hooks' / 'foreign.py'}"
                ),
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
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    monkeypatch.setenv("HOME", str(home))
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
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    monkeypatch.setenv("HOME", str(home))
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
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _authorize(project)
    monkeypatch.setenv("HOME", str(home))
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
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    monkeypatch.setenv("HOME", str(home))

    _projector(root).apply(project)

    assert (home / ".codex" / "hooks.json").is_file()
    assert not (project / ".codex").exists()
    assert not (project / ".claude").exists()


def test_generated_hook_executes_and_malformed_input_fails_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _authorize(project)
    monkeypatch.setenv("HOME", str(home))
    projector = _projector(root)
    projector.apply(project)
    settings = _json(project / ".claude" / "settings.json")
    command = settings["hooks"]["SessionStart"][-1]["hooks"][0]["command"]  # type: ignore[index]

    accepted = subprocess.run(
        shlex.split(command),
        input="{}",
        text=True,
        capture_output=True,
        check=True,
    )
    output = json.loads(accepted.stdout)
    assert "additionalContext" in output["hookSpecificOutput"]

    rejected = subprocess.run(
        shlex.split(command),
        input="[]",
        text=True,
        capture_output=True,
        check=False,
    )
    assert rejected.returncode != 0
    assert "TypeError: hook input must be a JSON object" in rejected.stderr


def test_modified_managed_hook_and_instruction_region_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _authorize(project)
    monkeypatch.setenv("HOME", str(home))
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
