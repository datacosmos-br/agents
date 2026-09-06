from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents_governance.catalog import Catalog
from agents_governance.commands import audit_command_specs
from agents_governance.governance_config import (
    audit_governance_config,
    load_governance_config,
)
from agents_governance.instruction_projection import InstructionProjector
from agents_governance.projection_config import load_projection_config
from agents_governance.rules import audit_rule_specs


def _projector(root: Path) -> InstructionProjector:
    catalog = Catalog(root)
    commands = audit_command_specs(root, (record.name for record in catalog.records()))
    rules = audit_rule_specs(root)
    governance = load_governance_config(root)
    audit_governance_config(root, governance, catalog, commands, rules)
    return InstructionProjector(
        governance,
        load_projection_config(root),
        commands,
        rules,
    )


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


def test_instruction_projection_preserves_foreign_content_and_reaches_fixed_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _authorize(project)
    monkeypatch.setenv("HOME", str(home))
    agents = project / "AGENTS.md"
    agents.write_text("# Existing project law\n", encoding="utf-8")
    projector = _projector(root)

    projector.apply(project)
    projector.check(project)
    first_mtime = agents.stat().st_mtime_ns
    projector.apply(project)

    assert agents.stat().st_mtime_ns == first_mtime
    rendered = agents.read_text(encoding="utf-8")
    assert rendered.startswith("# Existing project law\n")
    assert rendered.count("AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN") == 1
    assert "AIHUB-GOVERNANCE-CAPSULE v1 sha256:" in rendered
    assert "## Capability indexes" in rendered


def test_the_capsule_carries_every_bootstrap_rule_with_links_flattened(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _authorize(project)
    monkeypatch.setenv("HOME", str(home))
    governance = load_governance_config(root)

    _projector(root).apply(project)

    rendered = (project / "AGENTS.md").read_text(encoding="utf-8")
    for identity in governance.bootstrap_rules:
        assert f"## Rule `{identity}`" in rendered
    owned = rendered.split("AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN", 1)[1]
    assert "](" not in owned


def test_absent_project_authorization_projects_personal_instructions_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    monkeypatch.setenv("HOME", str(home))

    _projector(root).apply(project)

    assert (home / ".codex" / "AGENTS.md").is_file()
    assert not (project / "AGENTS.md").exists()


def test_modified_instruction_region_is_rejected(
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

    agents = project / "AGENTS.md"
    agents.write_text(
        agents.read_text().replace("The operator's newest", "Modified newest"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="instruction capsule was modified"):
        projector.apply(project)


def test_a_malformed_instruction_region_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _authorize(project)
    monkeypatch.setenv("HOME", str(home))
    agents = project / "AGENTS.md"
    agents.write_text(
        "# Existing project law\n\n<!-- AIHUB-GOVERNANCE-INSTRUCTIONS-BEGIN -->\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="managed instruction region is malformed"):
        _projector(root).apply(project)
