from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from agents_governance.agent_profiles import audit_agent_profiles
from agents_governance.catalog import Catalog
from agents_governance.projection import ProjectionDriftError, Projector
from agents_governance.projection_config import load_projection_config

_PROVIDERS = (
    "claude",
    "codex",
    "cursor",
    "copilot",
    "gemini",
    "opencode",
    "antigravity",
)
_SURFACES = ("skills", "commands", "agents", "rules", "hooks")


def _skill(
    root: Path,
    name: str,
    *,
    category: str = "project-wide",
    tags: tuple[str, ...] = (
        "provenance:test",
        "updates:manual",
        "usage:on-demand",
    ),
    body: str = "# Test\n\nCanonical project guidance.\n",
) -> Path:
    directory = root / "skills" / category / name
    directory.mkdir(parents=True)
    encoded = json.dumps(list(tags), separators=(",", ":"))
    (directory / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "description: project guidance\n"
        "metadata:\n"
        f"  aihub.tags: '{encoded}'\n"
        "---\n\n"
        f"{body}",
        encoding="utf-8",
    )
    return directory


def _config(root: Path, supported: dict[tuple[str, str], str]) -> None:
    config = root / "config"
    config.mkdir()
    (config / "skills.json").write_text(
        json.dumps(
            {
                "version": 2,
                "budgets": {
                    "router_tokens": 1000,
                    "frozen_tokens": 1000,
                    "on_demand_tokens": 1000,
                    "max_lines": 200,
                },
            }
        ),
        encoding="utf-8",
    )
    providers: dict[str, object] = {}
    for provider in _PROVIDERS:
        contexts: dict[str, object] = {}
        for context in ("personal", "project"):
            surfaces: dict[str, object] = {}
            for surface in _SURFACES:
                path = (
                    supported.get((provider, surface)) if context == "project" else None
                )
                surfaces[surface] = (
                    {
                        "status": "SUPPORTED",
                        "path": path,
                        **(
                            {
                                "events": {
                                    "context_refresh": ["ContextRefresh"],
                                    "prompt_submit": ["PromptSubmit"],
                                    "session_start": ["SessionStart"],
                                    "subagent_start": ["SubagentStart"],
                                },
                                "coverage": {
                                    "context_refresh": "exact",
                                    "prompt_submit": "exact",
                                    "session_start": "exact",
                                    "subagent_start": "exact",
                                },
                            }
                            if surface == "hooks"
                            else {"layout": "directory"}
                            if surface == "rules"
                            else {}
                        ),
                    }
                    if path is not None
                    else {
                        "status": "UNSUPPORTED",
                        "reason": "UNSUPPORTED: not part of this focused fixture",
                    }
                )
            contexts[context] = surfaces
        providers[provider] = contexts
    (config / "projections.json").write_text(
        json.dumps({"version": 5, "manifest_version": 5, "providers": providers}),
        encoding="utf-8",
    )


def _source(
    tmp_path: Path,
    *,
    supported: dict[tuple[str, str], str] | None = None,
) -> tuple[Path, Projector]:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "project-guidance")
    _config(root, supported or {("codex", "skills"): ".agents/skills"})
    return root, Projector(Catalog(root), load_projection_config(root), (), (), ())


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    return project


def _agent_source(root: Path) -> None:
    (root / "agents" / "agent-wide").mkdir(parents=True)
    project_agents = root / "agents" / "project-wide"
    project_agents.mkdir(parents=True)
    (project_agents / "reviewer.md").write_text(
        "---\n"
        "name: reviewer\n"
        "description: Review project changes.\n"
        "tools: [filesystem:read]\n"
        "metadata:\n"
        '  aihub.tags: \'["activation:opt-in", "mode:review", "role:reviewer"]\'\n'
        "---\n\n"
        "# Review\n",
        encoding="utf-8",
    )
    defense = root / "rules" / "security" / "prompt-defense.md"
    defense.parent.mkdir(parents=True)
    defense.write_text("# Prompt defense\n", encoding="utf-8")


def _manifest(root: Path) -> dict[str, object]:
    return json.loads((root / Projector.MANIFEST).read_text(encoding="utf-8"))


def test_apply_derives_nested_invocation_project_and_reaches_fixed_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    nested = project / "src" / "package"
    nested.mkdir(parents=True)
    personal = tmp_path / "personal"
    personal.mkdir()
    monkeypatch.setenv("HOME", str(personal))
    monkeypatch.chdir(nested)

    with pytest.raises(ProjectionDriftError):
        projector.check()
    projector.apply()
    projector.check()

    target = project / ".agents" / "skills"
    first = Catalog.physical_tree_contract(target)
    manifest_mtime = (target / Projector.MANIFEST).stat().st_mtime_ns
    projector.apply()

    assert Catalog.physical_tree_contract(target) == first
    assert (target / Projector.MANIFEST).stat().st_mtime_ns == manifest_mtime
    assert (target / "project-guidance" / "SKILL.md").is_file()
    assert not tuple(personal.iterdir())
    assert _manifest(target)["project"] == "."
    assert _manifest(target)["destination"] == ".agents/skills"


def test_foreign_collision_fails_before_any_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(
        tmp_path,
        supported={
            ("codex", "skills"): ".agents/skills",
            ("claude", "skills"): ".claude/skills",
        },
    )
    project = _project(tmp_path)
    collision = project / ".claude" / "skills" / "project-guidance"
    collision.mkdir(parents=True)
    marker = collision / "foreign"
    marker.write_text("keep", encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="foreign projection collision"):
        projector.apply()

    assert marker.read_text(encoding="utf-8") == "keep"
    assert not (project / ".agents" / "skills").exists()
    assert not tuple(project.rglob(".agents-stage.*"))


def test_managed_source_update_is_reconciled_but_local_edit_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, projector = _source(tmp_path)
    project = _project(tmp_path)
    monkeypatch.chdir(project)
    projector.apply()
    source = root / "skills" / "project-wide" / "project-guidance" / "SKILL.md"
    source.write_text(
        source.read_text(encoding="utf-8") + "\nUpdated source.\n",
        encoding="utf-8",
    )

    projector.apply()

    destination = project / ".agents" / "skills" / "project-guidance" / "SKILL.md"
    assert destination.read_text(encoding="utf-8").endswith("Updated source.\n")
    destination.write_text("local edit", encoding="utf-8")
    with pytest.raises(ValueError, match="managed projection was modified"):
        projector.apply()
    assert destination.read_text(encoding="utf-8") == "local edit"


def test_invalid_manifest_and_destination_symlink_are_never_rewritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    target = project / ".agents" / "skills"
    target.mkdir(parents=True)
    manifest = target / Projector.MANIFEST
    manifest.write_text("not-json", encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(json.JSONDecodeError):
        projector.apply()
    assert manifest.read_text(encoding="utf-8") == "not-json"

    manifest.unlink()
    outside = project / "outside"
    outside.mkdir()
    target.rmdir()
    target.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        projector.apply()
    assert target.is_symlink()


def test_absolute_manifest_identity_is_rejected_without_rewrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    monkeypatch.chdir(project)
    projector.apply()
    target = project / ".agents" / "skills"
    manifest = target / Projector.MANIFEST
    payload = _manifest(target)
    payload["project"] = str(project)
    invalid = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    manifest.write_text(invalid, encoding="utf-8")

    with pytest.raises(ValueError, match="project must equal"):
        projector.apply()

    assert manifest.read_text(encoding="utf-8") == invalid


def test_project_selection_activates_only_declared_project_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "project-guidance")
    _skill(
        root,
        "selected-tool",
        category="tool",
        tags=(
            "activation:opt-in",
            "detect:opt-in:selected-tool",
            "provenance:test",
            "route:project",
            "tool:selected-tool",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    _config(root, {("codex", "skills"): ".agents/skills"})
    projector = Projector(Catalog(root), load_projection_config(root), (), (), ())
    project = _project(tmp_path)
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir()
    selection.write_text(
        json.dumps(
            {
                "version": 1,
                "agents": [],
                "opt_ins": ["selected-tool"],
                "selected_tags": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(project)

    projector.apply()

    target = project / ".agents" / "skills"
    assert (target / "selected-tool" / "SKILL.md").is_file()
    selected = _manifest(target)["selection"]
    assert isinstance(selected, dict)
    assert selected["opt_ins"] == ["selected-tool"]


def test_project_selection_projects_copilot_agent_with_native_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "project-guidance")
    _agent_source(root)
    _config(root, {("copilot", "agents"): ".github/agents"})
    projector = Projector(
        Catalog(root),
        load_projection_config(root),
        (),
        audit_agent_profiles(root),
        (),
    )
    project = _project(tmp_path)
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir()
    selection.write_text(
        json.dumps(
            {
                "version": 1,
                "agents": ["reviewer"],
                "opt_ins": [],
                "selected_tags": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(project)

    projector.apply()
    projector.check()

    target = project / ".github" / "agents"
    artifact = target / "reviewer.agent.md"
    assert artifact.is_file()
    assert "target: github-copilot\n" in artifact.read_text(encoding="utf-8")
    assert _manifest(target)["providers"] == ["copilot"]


def test_unknown_selection_fails_without_creating_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir()
    selection.write_text(
        json.dumps(
            {
                "version": 1,
                "agents": [],
                "opt_ins": ["unknown"],
                "selected_tags": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="unknown project opt-in"):
        projector.apply()

    assert not (project / ".agents" / "skills").exists()


def test_each_skill_uses_only_its_own_detector_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    for name, marker in (
        ("first-tool", "first.marker"),
        ("second-tool", "second.marker"),
    ):
        _skill(
            root,
            name,
            category="tool",
            tags=(
                "activation:detected",
                f"detect:marker:{marker}",
                "provenance:test",
                "route:project",
                "tool:shared",
                "updates:manual",
                "usage:on-demand",
            ),
        )
    _config(root, {("codex", "skills"): ".agents/skills"})
    projector = Projector(Catalog(root), load_projection_config(root), (), (), ())
    project = _project(tmp_path)
    (project / "first.marker").write_text("present", encoding="utf-8")
    monkeypatch.chdir(project)

    projector.apply()

    target = project / ".agents" / "skills"
    assert (target / "first-tool").is_dir()
    assert not (target / "second-tool").exists()


def test_invalid_dependency_manifest_is_not_treated_as_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    (project / "pyproject.toml").write_text(
        '[project]\ndependencies = "react"\n', encoding="utf-8"
    )
    monkeypatch.chdir(project)

    with pytest.raises(TypeError, match="dependencies must be an array"):
        projector.apply()

    assert not (project / ".agents" / "skills").exists()


def test_second_target_failure_rolls_back_first_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(
        tmp_path,
        supported={
            ("codex", "skills"): ".agents/skills",
            ("claude", "skills"): ".claude/skills",
        },
    )
    project = _project(tmp_path)
    monkeypatch.chdir(project)
    original = projector._publish

    def fail_second(staged: Any) -> None:
        root = staged.state.plan.root
        if root == project / ".claude" / "skills":
            raise RuntimeError("injected publication failure")
        original(staged)

    monkeypatch.setattr(projector, "_publish", fail_second)

    with pytest.raises(RuntimeError, match="injected publication failure"):
        projector.apply()

    assert not (project / ".agents" / "skills").exists()
    assert not (project / ".claude" / "skills").exists()
    assert not tuple(project.rglob(".agents-stage.*"))


def test_projector_public_operations_are_optionless() -> None:
    assert tuple(inspect.signature(Projector.apply).parameters) == ("self",)
    assert tuple(inspect.signature(Projector.check).parameters) == ("self",)


def test_worktree_git_file_is_rejected_without_git_subprocess(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="physical .git directory"):
        projector.apply()
