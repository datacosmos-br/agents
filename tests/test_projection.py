from __future__ import annotations

import inspect
import json
import subprocess
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from agents_governance.agent_profiles import audit_agent_profiles
from agents_governance.catalog import Catalog
from agents_governance.projection import (
    _SELECTION_FIELDS_V1,
    _SELECTION_FIELDS_V2,
    ProjectionDriftError,
    Projector,
)
from agents_governance.projection_config import load_projection_config
from agents_governance.rules import audit_rule_specs

_PROVIDERS = (
    "claude",
    "codex",
    "cursor",
    "copilot",
    "gemini",
    "opencode",
    "antigravity",
)
_SURFACES = ("skills", "commands", "agents", "rules")


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
    evaluation: bool = True,
) -> Path:
    directory = root / "skills" / category / name
    directory.mkdir(parents=True)
    encoded = json.dumps(list(tags), separators=(",", ":"))
    (directory / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "description: project guidance, validation, workflow\n"
        "metadata:\n"
        f"  aihub.tags: '{encoded}'\n"
        "---\n\n"
        f"{body}",
        encoding="utf-8",
    )
    if evaluation:
        _skill_eval(root, name, category)
    return directory


def _skill_eval(root: Path, name: str, category: str) -> None:
    directory = root / "evals" / name
    tasks = directory / "tasks"
    tasks.mkdir(parents=True)
    (directory / "eval.yaml").write_text(
        yaml.safe_dump(
            {
                "name": f"{name}-eval",
                "skill": name,
                "config": {
                    "trials_per_task": 1,
                    "model": "aihub-primary",
                    "timeout_seconds": 60,
                    "parallel": False,
                    "max_attempts": 0,
                    "fail_fast": True,
                    "executor": "copilot-sdk",
                    "required_skills": [name],
                    "skill_directories": [f"../../skills/{category}/{name}"],
                },
                "graders": [
                    {
                        "type": "prompt",
                        "name": f"{name}-contract",
                        "config": {"prompt": f"Grade the {name} material result."},
                    },
                    {
                        "type": "behavior",
                        "name": "bounded",
                        "config": {"max_duration_ms": 50_000},
                    },
                ],
                "tasks": ["tasks/*.yaml"],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    scenarios = {
        "basic-usage.yaml": {
            "id": f"{name}-happy-001",
            "inputs": {"prompt": f"Produce the material {name} result."},
            "expected": {"output_contains": [f"{name} material result"]},
        },
        "edge-case.yaml": {
            "id": f"{name}-fail-closed-001",
            "inputs": {"prompt": ""},
            "expected": {
                "output_contains": [f"blocked {name}"],
                "output_not_contains": [f"published invalid {name}"],
            },
        },
        "should-not-trigger.yaml": {
            "id": f"{name}-should-not-trigger-001",
            "inputs": {"prompt": f"Perform an adjacent operation unrelated to {name}."},
            "expected": {"output_not_contains": [f"activated {name}"]},
        },
    }
    for filename, payload in scenarios.items():
        (tasks / filename).write_text(
            yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
        )


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
    for category in (
        "agent-wide",
        "project-wide",
        "technology",
        "framework",
        "tool",
        "domain",
    ):
        (root / "skills" / category).mkdir(parents=True, exist_ok=True)
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
                        **({"layout": "directory"} if surface == "rules" else {}),
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
        json.dumps(
            {
                "version": 7,
                "manifest_versions": {"projection": 5},
                "providers": providers,
            }
        ),
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


def _project(
    tmp_path: Path,
    *,
    authorized: bool = True,
    selected_tags: tuple[str, ...] = (),
) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    if authorized:
        selection = project / ".agents" / "projection.json"
        selection.parent.mkdir()
        selection.write_text(
            json.dumps(
                {
                    "version": 1,
                    "agents": [],
                    "opt_ins": [],
                    "selected_tags": list(selected_tags),
                }
            ),
            encoding="utf-8",
        )
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


def _git(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ("git", "-C", str(repository), *arguments),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def _git_repository(path: Path) -> Path:
    path.mkdir()
    _git(path, "init", "--initial-branch=develop")
    _git(path, "config", "user.name", "Projection Fixture")
    _git(path, "config", "user.email", "projection@example.invalid")
    (path / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(path, "add", "README.md")
    _git(path, "commit", "-m", "fixture")
    return path


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


def test_absent_project_authorization_is_a_non_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path, authorized=False)
    malformed = project / "skills" / "project-wide" / "malformed"
    malformed.mkdir(parents=True)
    (malformed / "SKILL.md").write_text("not frontmatter\n", encoding="utf-8")
    monkeypatch.chdir(project)

    projector.apply()
    projector.check()

    assert not (project / ".agents").exists()


def test_authorized_local_skill_composes_with_central_sources_and_reaches_fixed_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    local = _skill(
        project,
        "local-guidance",
        tags=(
            "provenance:project-owned",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    source_snapshot = Catalog.physical_tree_contract(local)
    monkeypatch.chdir(project)

    projector.apply()
    target = project / ".agents" / "skills"
    first = Catalog.physical_tree_contract(target)
    manifest_mtime = (target / Projector.MANIFEST).stat().st_mtime_ns
    projector.apply()

    assert (target / "project-guidance" / "SKILL.md").is_file()
    assert (target / "local-guidance" / "SKILL.md").is_file()
    managed = _manifest(target)["managed"]
    assert isinstance(managed, dict)
    assert managed["project-guidance"]["origin"] == "agents:skills"
    assert managed["local-guidance"]["origin"] == "project:skills"
    assert Catalog.physical_tree_contract(target) == first
    assert (target / Projector.MANIFEST).stat().st_mtime_ns == manifest_mtime
    assert Catalog.physical_tree_contract(local) == source_snapshot


def test_selected_flext_and_cosmos_tags_activate_only_their_central_skills(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "project-guidance")
    _skill(
        root,
        "flext-development",
        category="framework",
        tags=(
            "activation:detected",
            "detect:selected-tag:flext",
            "framework:flext",
            "provenance:agents-owned",
            "route:project",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    _skill(
        root,
        "cosmos-gitops",
        category="domain",
        tags=(
            "activation:detected",
            "detect:selected-tag:cosmos-gitops",
            "domain:cosmos-gitops",
            "provenance:agents-owned",
            "route:project",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    _config(root, {("codex", "skills"): ".agents/skills"})
    projector = Projector(Catalog(root), load_projection_config(root), (), (), ())
    project = _project(tmp_path, selected_tags=("flext",))
    monkeypatch.chdir(project)

    projector.apply()
    target = project / ".agents" / "skills"
    assert (target / "flext-development" / "SKILL.md").is_file()
    assert not (target / "cosmos-gitops").exists()

    selection = project / ".agents" / "projection.json"
    selection.write_text(
        json.dumps(
            {
                "version": 1,
                "agents": [],
                "opt_ins": [],
                "selected_tags": ["cosmos-gitops"],
            }
        ),
        encoding="utf-8",
    )
    projector.apply()
    first = Catalog.physical_tree_contract(target)
    projector.apply()

    assert not (target / "flext-development").exists()
    assert (target / "cosmos-gitops" / "SKILL.md").is_file()
    assert Catalog.physical_tree_contract(target) == first


@pytest.mark.parametrize(
    ("name", "tags", "evaluation", "message"),
    [
        (
            "wrong-owner",
            ("provenance:agents-owned", "updates:manual", "usage:on-demand"),
            True,
            "provenance:project-owned",
        ),
        (
            "missing-eval",
            ("provenance:project-owned", "updates:manual", "usage:on-demand"),
            False,
            "eval",
        ),
        (
            "project-guidance",
            ("provenance:project-owned", "updates:manual", "usage:on-demand"),
            True,
            "central/local skill name collision",
        ),
    ],
)
def test_invalid_local_skill_fails_before_any_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    tags: tuple[str, ...],
    evaluation: bool,
    message: str,
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    _skill(project, name, tags=tags, evaluation=evaluation)
    monkeypatch.chdir(project)

    with pytest.raises((FileNotFoundError, ValueError), match=message):
        projector.apply()

    assert not (project / ".agents" / "skills").exists()


def test_local_skill_symlink_fails_before_any_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    local = _skill(
        project,
        "local-symlink",
        tags=(
            "provenance:project-owned",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    external = project / "external.md"
    external.write_text("external\n", encoding="utf-8")
    references = local / "references"
    references.mkdir()
    (references / "external.md").symlink_to(external)
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="symlink forbidden"):
        projector.apply()

    assert not (project / ".agents" / "skills").exists()


def test_local_skill_cross_bundle_reference_fails_before_any_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    local = _skill(
        project,
        "local-reference",
        tags=(
            "provenance:project-owned",
            "updates:manual",
            "usage:on-demand",
        ),
        body="# Local\n\nRead [foreign](../../foreign.md).\n",
    )
    foreign = local.parents[1] / "foreign.md"
    foreign.write_text("foreign\n", encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="is not in the subpath"):
        projector.apply()

    assert not (project / ".agents" / "skills").exists()


def test_personal_projection_includes_agent_routed_capabilities(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "always", category="agent-wide")
    _skill(
        root,
        "agent-tool",
        category="tool",
        tags=(
            "activation:opt-in",
            "detect:opt-in:agent-tool",
            "provenance:test",
            "route:agent",
            "tool:agent-tool",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    _skill(
        root,
        "project-tool",
        category="tool",
        tags=(
            "activation:opt-in",
            "detect:opt-in:project-tool",
            "provenance:test",
            "route:project",
            "tool:project-tool",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    _config(root, {})
    config_path = root / "config" / "projections.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["providers"]["codex"]["personal"]["skills"] = {
        "status": "SUPPORTED",
        "path": "${HOME}/.codex/skills",
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    project = _project(tmp_path, authorized=False)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(project)
    projector = Projector(Catalog(root), load_projection_config(root), (), (), ())

    projector.apply()

    target = home / ".codex" / "skills"
    assert (target / "always" / "SKILL.md").is_file()
    assert (target / "agent-tool" / "SKILL.md").is_file()
    assert not (target / "project-tool").exists()


def test_personal_projection_never_publishes_over_canonical_skill_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "always", category="agent-wide")
    _config(root, {})
    config_path = root / "config" / "projections.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["providers"]["codex"]["personal"]["skills"] = {
        "status": "SUPPORTED",
        "path": "${HOME}/source/skills",
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    project = _project(tmp_path, authorized=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(project)
    projector = Projector(Catalog(root), load_projection_config(root), (), (), ())

    projector.apply()

    assert not (root / "skills" / ".agents-governance.json").exists()
    assert not (root / "skills" / "always").exists()


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

    with pytest.raises(ValueError, match="unadjudicated projection divergence"):
        projector.apply()

    assert marker.read_text(encoding="utf-8") == "keep"
    assert not (project / ".agents" / "skills").exists()
    assert not tuple(project.rglob(".agents-stage.*"))


def test_divergent_unmanifested_agent_requires_adjudication_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "project-guidance")
    _agent_source(root)
    _config(
        root,
        {
            ("codex", "skills"): ".agents/skills",
            ("claude", "agents"): ".claude/agents",
        },
    )
    projector = Projector(
        Catalog(root),
        load_projection_config(root),
        (),
        audit_agent_profiles(root),
        audit_rule_specs(root),
    )
    project = _project(tmp_path)
    selection = project / ".agents" / "projection.json"
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
    collision = project / ".claude" / "agents" / "reviewer.md"
    collision.parent.mkdir(parents=True)
    foreign = (
        "---\n"
        "name: reviewer\n"
        "description: Review project changes.\n"
        "tools: [Read]\n"
        "model: opus\n"
        "---\n\n"
        "## Prompt Defense Baseline\n\n"
        "Locally authored semantic requirement.\n"
    )
    collision.write_text(foreign, encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(
        ValueError, match="unadjudicated projection divergence"
    ) as raised:
        projector.apply()

    message = str(raised.value)
    assert f"destination={collision}" in message
    assert "source_type=agent" in message
    assert "operator decision required before replacement" in message
    assert collision.read_text(encoding="utf-8") == foreign
    assert not (collision.parent / Projector.MANIFEST).exists()
    assert not (project / ".agents" / "skills").exists()
    assert not tuple(project.rglob(".agents-stage.*"))


def test_foreign_symlink_is_preserved_and_blocks_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    target = project / ".agents" / "skills"
    target.mkdir(parents=True)
    outside = project / "foreign-source"
    outside.mkdir()
    link = target / "foreign-link"
    link.symlink_to(outside, target_is_directory=True)
    original = link.readlink()
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="symlink"):
        projector.apply()

    assert link.is_symlink()
    assert link.readlink() == original
    assert not (target / "project-guidance").exists()
    assert not (target / Projector.MANIFEST).exists()
    assert not tuple(project.rglob(".agents-stage.*"))


def test_foreign_unknown_physical_entry_is_preserved_at_fixed_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    target = project / ".agents" / "skills"
    target.mkdir(parents=True)
    foreign = target / "operator-owned.txt"
    foreign.write_text("preserve\n", encoding="utf-8")
    monkeypatch.chdir(project)

    projector.apply()
    projector.check()

    assert foreign.read_text(encoding="utf-8") == "preserve\n"
    assert (target / "project-guidance" / "SKILL.md").is_file()
    manifest = target / Projector.MANIFEST
    assert manifest.is_file()
    first = Catalog.physical_tree_contract(target)
    manifest_mtime = manifest.stat().st_mtime_ns

    projector.apply()

    assert Catalog.physical_tree_contract(target) == first
    assert manifest.stat().st_mtime_ns == manifest_mtime
    assert not tuple(project.rglob(".agents-stage.*"))


def test_broken_destination_symlink_created_after_preflight_is_preserved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    target = project / ".agents" / "skills"
    outside = project / "missing-external-target"
    original_publish = projector._publish
    monkeypatch.chdir(project)

    def race(staged: Any) -> None:
        if staged.state.plan.root == target:
            target.symlink_to(outside, target_is_directory=True)
        original_publish(staged)

    monkeypatch.setattr(projector, "_publish", race)

    with pytest.raises(ValueError, match="symlink"):
        projector.apply()

    assert target.is_symlink()
    assert target.readlink() == outside
    assert not outside.exists()
    assert not tuple(project.rglob(".agents-stage.*"))


def test_unmanifested_source_symlink_requires_adjudication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, projector = _source(tmp_path)
    project = _project(tmp_path)
    target = project / ".agents" / "skills"
    target.mkdir(parents=True)
    retired = source / "skills" / "project-guidance"
    managed = target / "project-guidance"
    managed.symlink_to(retired, target_is_directory=True)
    assert managed.is_symlink()
    assert not managed.exists()
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="symlink forbidden"):
        projector.apply()

    assert managed.is_symlink()
    assert managed.readlink() == retired
    assert not (target / Projector.MANIFEST).exists()


def test_exact_orphaned_projection_is_adopted_by_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    monkeypatch.chdir(project)
    projector.apply()
    target = project / ".agents" / "skills"
    managed = target / "project-guidance"
    before = managed.stat().st_mtime_ns
    (target / Projector.MANIFEST).unlink()

    projector.apply()
    projector.check()

    assert managed.stat().st_mtime_ns == before
    assert (target / Projector.MANIFEST).is_file()


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


def test_removed_manifest_schema_is_rejected_without_rewrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    target = project / ".agents" / "skills"
    target.mkdir(parents=True)
    manifest = target / Projector.MANIFEST
    removed = json.dumps({"managed": {}, "version": 2})
    manifest.write_text(removed, encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="fields must equal"):
        projector.apply()

    assert manifest.read_text(encoding="utf-8") == removed


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
    selection.parent.mkdir(exist_ok=True)
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
        audit_rule_specs(root),
    )
    project = _project(tmp_path)
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir(exist_ok=True)
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
    selection.parent.mkdir(exist_ok=True)
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


def test_contained_git_submodule_is_a_physical_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    member_source = _git_repository(tmp_path / "member-source")
    umbrella = _git_repository(tmp_path / "umbrella")
    _git(
        umbrella,
        "-c",
        "protocol.file.allow=always",
        "submodule",
        "add",
        str(member_source),
        "member",
    )
    _git(umbrella, "commit", "-am", "add member")
    member = umbrella / "member"
    nested = member / "src"
    nested.mkdir()
    monkeypatch.chdir(nested)

    assert projector.project_root() == member.resolve(strict=True)


def test_borrowed_contained_submodule_git_directory_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    member_source = _git_repository(tmp_path / "member-source")
    umbrella = _git_repository(tmp_path / "umbrella")
    _git(
        umbrella,
        "-c",
        "protocol.file.allow=always",
        "submodule",
        "add",
        str(member_source),
        "member",
    )
    _git(umbrella, "commit", "-am", "add member")
    borrowed = umbrella / "borrowed"
    borrowed.mkdir()
    (borrowed / ".git").write_text("gitdir: ../.git/modules/member\n", encoding="utf-8")
    monkeypatch.chdir(borrowed)

    with pytest.raises(ValueError, match="external Git directory is forbidden"):
        projector.project_root()


def test_git_worktree_is_a_valid_project_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    repository = _git_repository(tmp_path / "repository")
    worktree = tmp_path / "worktree"
    _git(repository, "worktree", "add", "--detach", str(worktree))
    monkeypatch.chdir(worktree)
    resolved = worktree.resolve(strict=True)

    if resolved == Path("/tmp") or Path("/tmp") in resolved.parents:
        with pytest.raises(ValueError, match="repositories under /tmp are prohibited"):
            projector.project_root()
        return

    assert projector.project_root() == resolved


def test_external_git_directory_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    external = _git_repository(tmp_path / "external")
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").write_text(f"gitdir: {external / '.git'}\n", encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="external Git directory is forbidden"):
        projector.apply()


def test_malformed_git_file_propagates_git_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").write_text("gitdir: missing\n", encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(subprocess.CalledProcessError):
        projector.apply()


def test_git_metadata_symlink_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    external = _git_repository(tmp_path / "external")
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").symlink_to(external / ".git", target_is_directory=True)
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="Git metadata symlink forbidden"):
        projector.apply()


# ===== v2 detection_rules tests =====


def _rule_activate_tags(rules: list[dict[str, object]]) -> set[str]:
    tags: set[str] = set()
    for rule in rules:
        tags.update(cast(list[str], rule["activate_tags"]))
    return tags


def _conditional_skill(root: Path, tag: str) -> None:
    category = "domain" if tag == "documentation" else "framework"
    tags = tuple(
        sorted(
            (
                "activation:detected",
                f"detect:selected-tag:{tag}",
                f"{category}:{tag}",
                "provenance:agents-owned",
                "route:project",
                "updates:manual",
                "usage:on-demand",
            )
        )
    )
    _skill(
        root,
        f"{tag}-skill",
        category=category,
        tags=tags,
    )


def _make_v2_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    detection_rules: list[dict[str, object]],
    *,
    selected_tags: tuple[str, ...] = (),
    project_name: str = "project",
) -> tuple[Path, Projector]:
    project = tmp_path / f"{project_name}-project"
    project.mkdir()
    (project / ".git").mkdir()
    selection = project / ".agents" / "projection.json"
    selection.parent.mkdir()
    selection.write_text(
        json.dumps(
            {
                "version": 2,
                "agents": [],
                "opt_ins": [],
                "selected_tags": list(selected_tags),
                "detection_rules": detection_rules,
            }
        ),
        encoding="utf-8",
    )
    source = tmp_path / f"{project_name}-source"
    source.mkdir()
    _skill(source, "project-guidance")
    for tag in sorted({*selected_tags, *_rule_activate_tags(detection_rules)}):
        _conditional_skill(source, tag)
    _config(source, {("codex", "skills"): ".agents/skills"})
    projector = Projector(Catalog(source), load_projection_config(source), (), (), ())
    monkeypatch.chdir(project)
    return project, projector


def _write_doc(project: Path, name: str = "index.md") -> None:
    docs = project / "docs"
    docs.mkdir(exist_ok=True)
    (docs / name).write_text("# Docs\n", encoding="utf-8")


def test_v2_detection_rules_path_exists_activates_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "doc-project",
            "when": {
                "all": [
                    {"type": "path_exists", "pattern": "docs/*.md"},
                    {"type": "path_exists", "pattern": "mkdocs.yml"},
                ]
            },
            "activate_tags": ["documentation"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project)
    (project / "mkdocs.yml").write_text("site_name: Test\n", encoding="utf-8")

    projector.apply()

    target = project / ".agents" / "skills"
    assert (target / "documentation-skill" / "SKILL.md").is_file()
    assert "documentation" in cast(
        list[str],
        cast(dict[str, object], _manifest(target)["selection"])["selected_tags"],
    )


def test_v2_detection_rules_path_exists_any_operator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "doc-project",
            "when": {
                "any": [
                    {"type": "path_exists", "pattern": "docs/*.md"},
                    {"type": "path_exists", "pattern": "mkdocs.yml"},
                ]
            },
            "activate_tags": ["documentation"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project)

    projector.apply()

    assert (project / ".agents" / "skills" / "documentation-skill").is_dir()


def test_v2_detection_rules_path_exists_all_requires_all(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "doc-project",
            "when": {
                "all": [
                    {"type": "path_exists", "pattern": "docs/*.md"},
                    {"type": "path_exists", "pattern": "mkdocs.yml"},
                ]
            },
            "activate_tags": ["documentation"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project)

    projector.apply()

    assert not (project / ".agents" / "skills" / "documentation-skill").exists()


def test_v2_detection_rules_path_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "no-docs",
            "when": {"all": [{"type": "path_missing", "pattern": "docs/*.md"}]},
            "activate_tags": ["no-docs"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)

    projector.apply()

    selected = cast(
        list[str],
        cast(dict[str, object], _manifest(project / ".agents" / "skills")["selection"])[
            "selected_tags"
        ],
    )
    assert "no-docs" in selected


def test_v2_detection_rules_file_contains(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "flext-usage",
            "when": {
                "any": [
                    {
                        "type": "file_contains",
                        "pattern": "flext",
                        "paths": ["docs/*.md", "pyproject.toml"],
                    }
                ]
            },
            "activate_tags": ["flext"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project, "readme.md")
    (project / "docs" / "readme.md").write_text("# Uses flext\n", encoding="utf-8")

    projector.apply()

    assert (project / ".agents" / "skills" / "flext-skill").is_dir()


def test_v2_detection_rules_file_not_contains(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "no-flext",
            "when": {
                "all": [
                    {
                        "type": "file_not_contains",
                        "pattern": "flext",
                        "paths": ["src/*.py"],
                    }
                ]
            },
            "activate_tags": ["no-flext"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    source = project / "src"
    source.mkdir()
    (source / "main.py").write_text("import requests\n", encoding="utf-8")

    projector.apply()

    selected = cast(
        list[str],
        cast(dict[str, object], _manifest(project / ".agents" / "skills")["selection"])[
            "selected_tags"
        ],
    )
    assert "no-flext" in selected


def test_v2_detection_rules_when_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "always",
            "when": {"none": [{"type": "path_exists", "pattern": "docs/absent.md"}]},
            "activate_tags": ["always-active"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)

    projector.apply()

    assert (project / ".agents" / "skills" / "always-active-skill").is_dir()


def test_v2_detection_rules_external_symlink_is_not_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outside = tmp_path / "outside-source"
    outside.mkdir()
    (outside / "index.md").write_text("# Docs\n", encoding="utf-8")
    rules: list[dict[str, object]] = [
        {
            "id": "doc-project",
            "when": {"all": [{"type": "path_exists", "pattern": "link/*.md"}]},
            "activate_tags": ["documentation"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    (project / "link").symlink_to(outside, target_is_directory=True)

    projector.apply()

    assert not (project / ".agents" / "skills" / "documentation-skill").exists()


def test_v2_detection_rules_reject_unbounded_file_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "unbounded",
            "when": {
                "all": [
                    {
                        "type": "file_contains",
                        "pattern": "marker",
                        "paths": ["**/*.md"],
                    }
                ]
            },
            "activate_tags": ["unbounded"],
        }
    ]
    _, projector = _make_v2_project(tmp_path, monkeypatch, rules)

    with pytest.raises(ValueError, match="bounded relative glob"):
        projector.apply()


def test_v2_detection_rules_enforces_file_quota(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("agents_governance.projection._DETECTION_MAX_FILES", 1)
    rules: list[dict[str, object]] = [
        {
            "id": "quota",
            "when": {
                "all": [
                    {
                        "type": "file_contains",
                        "pattern": "marker",
                        "paths": ["docs/*.md"],
                    }
                ]
            },
            "activate_tags": ["quota"],
        }
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project, "one.md")
    _write_doc(project, "two.md")

    with pytest.raises(ValueError, match="exceeded 1 files"):
        projector.apply()


def test_v2_detection_rules_reject_duplicate_rule_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "duplicate",
            "when": {"all": [{"type": "path_exists", "pattern": "one.txt"}]},
            "activate_tags": ["one"],
        },
        {
            "id": "duplicate",
            "when": {"all": [{"type": "path_exists", "pattern": "two.txt"}]},
            "activate_tags": ["two"],
        },
    ]
    _, projector = _make_v2_project(tmp_path, monkeypatch, rules)

    with pytest.raises(ValueError, match="duplicates detection rule id duplicate"):
        projector.apply()


def test_v2_detection_rules_merge_with_selected_tags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[dict[str, object]] = [
        {
            "id": "python-project",
            "when": {"all": [{"type": "path_exists", "pattern": "pyproject.toml"}]},
            "activate_tags": ["python"],
        }
    ]
    project, projector = _make_v2_project(
        tmp_path,
        monkeypatch,
        rules,
        selected_tags=("documentation",),
    )
    (project / "pyproject.toml").write_text(
        "[project]\nname = 'test'\n", encoding="utf-8"
    )

    projector.apply()

    selected = cast(
        list[str],
        cast(dict[str, object], _manifest(project / ".agents" / "skills")["selection"])[
            "selected_tags"
        ],
    )
    assert {"python", "documentation"} <= set(selected)


def test_v2_selection_field_contracts_are_exact() -> None:
    assert set(_SELECTION_FIELDS_V1) == {
        "agents",
        "opt_ins",
        "selected_tags",
        "version",
    }
    assert set(_SELECTION_FIELDS_V2) == set(_SELECTION_FIELDS_V1) | {"detection_rules"}


# ===== End v2 detection_rules tests =====
