from __future__ import annotations

import json
import shlex
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


def test_hook_projection_preserves_foreign_content_and_reaches_fixed_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
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
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "bd codex-hook old",
                                }
                            ]
                        },
                    ]
                },
            }
        ),
        encoding="utf-8",
    )
    agents = project / "AGENTS.md"
    agents.write_text("# Existing project law\n", encoding="utf-8")
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
    assert not any(
        group["hooks"][0].get("command", "").startswith("bd codex-hook")
        for group in session_groups
    )
    assert agents.read_text().startswith("# Existing project law\n")
    assert agents.read_text().count("AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN") == 1

    copilot = _json(project / ".github" / "hooks" / "aihub-governance.json")
    copilot_handler = copilot["hooks"]["sessionStart"][0]  # type: ignore[index]
    assert "bash" in copilot_handler
    assert "command" not in copilot_handler
    antigravity = _json(
        project / ".agents" / "plugins" / "aihub-governance" / "hooks.json"
    )
    assert set(antigravity) == {"aihub-governance"}
    assert "PreInvocation" in antigravity["aihub-governance"]  # type: ignore[operator]

    plugin = (project / ".opencode" / "plugins" / "aihub-governance.ts").read_text(
        encoding="utf-8"
    )
    assert "output.system[0]" in plugin
    assert "experimental.session.compacting" in plugin
    assert "chat.message" not in plugin
    assert "event: async" not in plugin


def test_generated_hook_executes_and_malformed_input_fails_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
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
