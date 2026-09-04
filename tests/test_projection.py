from __future__ import annotations

import inspect
import json
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast

import pytest
from conftest import approved, seed_approval_docs
from projection_fixtures import (
    JsonDocument,
    JsonValue,
    flext_detection_rule,
)
from waza_fixtures import write_eval_suite

from agents_governance.agent_profiles import audit_agent_profiles
from agents_governance.catalog import Catalog
from agents_governance.projection import (
    _SELECTION_FIELDS_V1,
    _SELECTION_FIELDS_V2,
    _SELECTION_FIELDS_V3,
    Projector,
)
from agents_governance.projection_config import (
    DetectionCondition,
    DetectionConditionType,
    DetectionOperator,
    ProjectDetectionRule,
    ProjectionConfig,
    ProjectionContext,
    ProjectionStatus,
    load_projection_config,
)
from agents_governance.rules import audit_rule_specs

_PROVIDERS = (
    "claude",
    "codex",
    "cursor",
    "copilot",
    "gemini",
    "opencode",
    "antigravity",
    "pool",
)
_SURFACES = ("skills", "commands", "agents", "rules", "hooks")


def _encode(tags: tuple[str, ...]) -> str:
    return json.dumps(list(approved(tags)), separators=(",", ":"))


_defense_tags = _encode(("route:both",))


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
    seed_approval_docs(root)
    directory = root / "skills" / category / name
    directory.mkdir(parents=True)
    encoded = json.dumps(list(approved(tags)), separators=(",", ":"))
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
    scenarios: dict[str, dict[str, object]] = {
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
    write_eval_suite(
        root,
        f"evals/{name}",
        name=name,
        skill=name,
        model="aihub-primary",
        skill_directories=[f"../../skills/{category}/{name}"],
        graders=[
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
        tasks=scenarios,
    )


def _config(
    root: Path,
    supported: dict[tuple[str, str], str],
    *,
    personal_supported: dict[tuple[str, str], str] | None = None,
    project_detection_rules: list[JsonDocument] | None = None,
) -> ProjectionConfig:
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
    base = load_projection_config(root)
    cells = {}
    for key, cell in base.cells.items():
        selected = (
            supported
            if cell.context is ProjectionContext.PROJECT
            else personal_supported or {}
        )
        selected_path = selected.get((cell.provider.value, cell.surface.value))
        cells[key] = (
            replace(cell, path=selected_path)
            if selected_path is not None
            else replace(
                cell,
                status=ProjectionStatus.UNSUPPORTED,
                path=None,
                reason="UNSUPPORTED: not part of this focused fixture",
                events=None,
                layout=None,
            )
        )
    rules: list[ProjectDetectionRule] = []
    for raw in project_detection_rules or []:
        when = cast("JsonDocument", raw["when"])
        operator = next(iter(when))
        conditions = cast("Sequence[JsonDocument]", when[operator])
        rules.append(
            ProjectDetectionRule(
                cast(str, raw["id"]),
                tuple(cast("Sequence[str]", raw["activate_tags"])),
                DetectionOperator(operator),
                tuple(
                    DetectionCondition(
                        DetectionConditionType(cast(str, condition["type"])),
                        cast(str, condition["pattern"]),
                        tuple(cast("Sequence[str]", condition.get("paths", []))),
                    )
                    for condition in conditions
                ),
            )
        )
    return replace(
        base,
        project_detection_rules=tuple(rules),
        cells=MappingProxyType(cells),
    )


def _source(
    tmp_path: Path,
    *,
    supported: dict[tuple[str, str], str] | None = None,
    project_detection_rules: list[JsonDocument] | None = None,
) -> tuple[Path, Projector]:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "project-guidance")
    if project_detection_rules is not None:
        detected = set(_rule_activate_tags(project_detection_rules))
        if "flext" in detected:
            detected.add("internal")
        for tag in sorted(detected):
            _conditional_skill(root, tag)
    projection = _config(
        root,
        supported or {("codex", "skills"): ".agents/skills"},
        project_detection_rules=project_detection_rules,
    )
    return root, Projector(Catalog(root), projection, (), (), ())


def _agent_projector(
    tmp_path: Path, supported: dict[tuple[str, str], str]
) -> tuple[Path, Projector]:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "project-guidance")
    _agent_source(root)
    projection = _config(root, supported)
    return root, Projector(
        Catalog(root),
        projection,
        (),
        audit_agent_profiles(root),
        audit_rule_specs(root),
    )


def _skill_projector(
    tmp_path: Path,
    specs: tuple[tuple[str, str, tuple[str, ...]], ...],
) -> tuple[Path, Projector]:
    root = tmp_path / "source"
    root.mkdir()
    _skill(root, "project-guidance")
    for name, category, tags in specs:
        _skill(root, name, category=category, tags=tags)
    projection = _config(root, {("codex", "skills"): ".agents/skills"})
    return root, Projector(Catalog(root), projection, (), (), ())


def _project(
    tmp_path: Path,
    *,
    authorized: bool = True,
    agents: tuple[str, ...] = (),
    opt_ins: tuple[str, ...] = (),
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
                    "agents": list(agents),
                    "opt_ins": list(opt_ins),
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
    defense.write_text(
        "---\n"
        "description: Prompt defense baseline.\n"
        "metadata:\n"
        f"  aihub.tags: '{_defense_tags}'\n"
        "---\n\n"
        "# Prompt defense\n",
        encoding="utf-8",
    )


def _manifest(root: Path) -> dict[str, object]:
    return json.loads((root / Projector.MANIFEST).read_text(encoding="utf-8"))


def _selected_tags(project: Path) -> list[str]:
    selection = cast(
        dict[str, object], _manifest(project / ".agents" / "skills")["selection"]
    )
    return cast(list[str], selection["selected_tags"])


def _dual_skill_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Projector, Path]:
    _, projector = _source(
        tmp_path,
        supported={
            ("codex", "skills"): ".agents/skills",
            ("claude", "skills"): ".claude/skills",
        },
    )
    project = _project(tmp_path)
    monkeypatch.chdir(project)
    return projector, project


def _published_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Projector, Path, Path, int]:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    monkeypatch.chdir(project)
    projector.apply()
    target = project / ".agents" / "skills"
    managed = target / "project-guidance"
    return projector, target, managed, managed.stat().st_mtime_ns


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


def _submodule(
    tmp_path: Path,
) -> tuple[Projector, Path, Path]:
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
    return projector, umbrella, umbrella / "member"


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

    # An absent projection root is an unborn publication target, not drift:
    # read-only check must stay green on a fresh runner before first apply.
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
    _, projector = _skill_projector(
        tmp_path,
        (
            (
                "flext-development",
                "framework",
                (
                    "activation:detected",
                    "detect:selected-tag:flext",
                    "framework:flext",
                    "provenance:agents-owned",
                    "route:project",
                    "updates:manual",
                    "usage:on-demand",
                ),
            ),
            (
                "cosmos-gitops",
                "domain",
                (
                    "activation:detected",
                    "detect:selected-tag:cosmos-gitops",
                    "domain:cosmos-gitops",
                    "provenance:agents-owned",
                    "route:project",
                    "updates:manual",
                    "usage:on-demand",
                ),
            ),
        ),
    )
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
    projection = _config(
        root,
        {},
        personal_supported={("codex", "skills"): "${HOME}/.codex/skills"},
    )
    project = _project(tmp_path, authorized=False)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(project)
    projector = Projector(Catalog(root), projection, (), (), ())

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
    projection = _config(
        root,
        {},
        personal_supported={("codex", "skills"): "${HOME}/source/skills"},
    )
    project = _project(tmp_path, authorized=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(project)
    projector = Projector(Catalog(root), projection, (), (), ())

    projector.apply()

    assert not (root / "skills" / ".agents-governance.json").exists()
    assert not (root / "skills" / "always").exists()


def test_foreign_collision_fails_before_any_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projector, project = _dual_skill_project(tmp_path, monkeypatch)
    collision = project / ".claude" / "skills" / "project-guidance"
    collision.mkdir(parents=True)
    marker = collision / "foreign"
    marker.write_text("keep", encoding="utf-8")

    with pytest.raises(ValueError, match="unadjudicated projection divergence"):
        projector.apply()

    assert marker.read_text(encoding="utf-8") == "keep"
    assert not (project / ".agents" / "skills").exists()
    assert not tuple(project.rglob(".agents-stage.*"))


def test_divergent_unmanifested_agent_requires_adjudication_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _root, projector = _agent_projector(
        tmp_path,
        {
            ("codex", "skills"): ".agents/skills",
            ("claude", "agents"): ".claude/agents",
        },
    )
    project = _project(tmp_path, agents=("reviewer",))
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
    projector, project, target = _empty_projection_target(tmp_path)
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
    projector, target, managed, before = _published_target(tmp_path, monkeypatch)
    (target / Projector.MANIFEST).unlink()

    projector.apply()
    projector.check()

    assert managed.stat().st_mtime_ns == before
    assert (target / Projector.MANIFEST).is_file()


def test_prior_version_manifest_transitions_without_rewriting_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projector, target, managed, before = _published_target(tmp_path, monkeypatch)
    payload = _manifest(target)
    assert payload["version"] == 6
    payload["version"] = 5
    entries = cast(dict[str, dict[str, object]], payload["managed"])
    for entry in entries.values():
        entry.pop("link_target", None)
    (target / Projector.MANIFEST).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    projector.apply()
    projector.check()

    assert managed.stat().st_mtime_ns == before
    assert _manifest(target)["version"] == 6
    first = Catalog.physical_tree_contract(target)
    projector.apply()
    assert Catalog.physical_tree_contract(target) == first


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
    projector, project, target = _empty_projection_target(tmp_path)
    manifest = target / Projector.MANIFEST
    removed = json.dumps({"managed": {}, "version": 2})
    manifest.write_text(removed, encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="fields must equal"):
        projector.apply()

    assert manifest.read_text(encoding="utf-8") == removed


def _empty_projection_target(tmp_path: Path) -> tuple[Projector, Path, Path]:
    _, projector = _source(tmp_path)
    project = _project(tmp_path)
    target = project / ".agents" / "skills"
    target.mkdir(parents=True)
    return projector, project, target


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
    _, projector = _skill_projector(
        tmp_path,
        (
            (
                "selected-tool",
                "tool",
                (
                    "activation:opt-in",
                    "detect:opt-in:selected-tool",
                    "provenance:test",
                    "route:project",
                    "tool:selected-tool",
                    "updates:manual",
                    "usage:on-demand",
                ),
            ),
        ),
    )
    project = _project(tmp_path, opt_ins=("selected-tool",))
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
    _root, projector = _agent_projector(
        tmp_path, {("copilot", "agents"): ".github/agents"}
    )
    project = _project(tmp_path, agents=("reviewer",))
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
    project = _project(tmp_path, opt_ins=("unknown",))
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
    projection = _config(root, {("codex", "skills"): ".agents/skills"})
    projector = Projector(Catalog(root), projection, (), (), ())
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
    projector, project = _dual_skill_project(tmp_path, monkeypatch)
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
    projector, _umbrella, member = _submodule(tmp_path)
    nested = member / "src"
    nested.mkdir()
    monkeypatch.chdir(nested)

    assert projector.project_root() == member.resolve(strict=True)


def test_borrowed_contained_submodule_git_directory_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projector, umbrella, _member = _submodule(tmp_path)
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

    assert projector.project_root() == resolved


def test_git_worktree_under_system_temp_is_a_valid_project_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    with tempfile.TemporaryDirectory(prefix="agents-projector-", dir="/tmp") as root:
        temporary = Path(root)
        repository = _git_repository(temporary / "repository")
        worktree = temporary / "worktree"
        _git(repository, "worktree", "add", "--detach", str(worktree))
        monkeypatch.chdir(worktree)

        assert projector.project_root() == worktree.resolve(strict=True)


def test_git_worktree_with_relative_paths_is_a_valid_project_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Git may write the administrative back-reference relative to its own directory.

    With ``worktree.useRelativePaths`` set, resolving that reference against
    the process working directory yields a path that does not exist, and a
    legitimate linked worktree is rejected as an external Git directory.
    """

    _, projector = _source(tmp_path)
    repository = _git_repository(tmp_path / "repository")
    _git(repository, "config", "worktree.useRelativePaths", "true")
    worktree = tmp_path / "worktree"
    _git(repository, "worktree", "add", "--relative-paths", "--detach", str(worktree))
    back_pointer = (
        repository / ".git" / "worktrees" / worktree.name / "gitdir"
    ).read_text(encoding="utf-8")
    assert not Path(back_pointer.strip()).is_absolute()
    monkeypatch.chdir(worktree)
    resolved = worktree.resolve(strict=True)

    assert projector.project_root() == resolved


def test_external_git_directory_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, projector = _source(tmp_path)
    project = _project_with_external_gitdir(tmp_path, "project")
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="external Git directory is forbidden"):
        projector.apply()


def test_external_git_directory_under_a_worktrees_directory_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A borrowed Git directory stays forbidden inside a `worktrees/` layout.

    Gas City places rig-scoped worktrees at `<rig-root>/worktrees/<id>`, so a
    path-component name check would silently accept every borrowed Git
    directory living under one.
    """

    _, projector = _source(tmp_path)
    project = _project_with_external_gitdir(tmp_path, "worktrees/borrowed")
    monkeypatch.chdir(project)

    with pytest.raises(ValueError, match="external Git directory is forbidden"):
        projector.apply()


def _project_with_external_gitdir(tmp_path: Path, relative: str) -> Path:
    external = _git_repository(tmp_path / "external")
    project = tmp_path / relative
    project.mkdir(parents=True)
    (project / ".git").write_text(f"gitdir: {external / '.git'}\n", encoding="utf-8")
    return project


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


def _rule_activate_tags(rules: list[JsonDocument]) -> set[str]:
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
    detection_rules: list[JsonDocument],
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
    projection = _config(
        source,
        {("codex", "skills"): ".agents/skills"},
        project_detection_rules=detection_rules,
    )
    projector = Projector(Catalog(source), projection, (), (), ())
    monkeypatch.chdir(project)
    return project, projector


def _write_doc(project: Path, name: str = "index.md") -> None:
    docs = project / "docs"
    docs.mkdir(exist_ok=True)
    (docs / name).write_text("# Docs\n", encoding="utf-8")


def _detection_rule(
    identifier: str,
    condition_type: str,
    operator: str,
    patterns: tuple[str, ...],
    tag: str,
    *,
    paths: tuple[str, ...] | None = None,
) -> JsonDocument:
    conditions: list[dict[str, JsonValue]] = [
        {"type": condition_type, "pattern": pattern} for pattern in patterns
    ]
    if paths is not None:
        for condition in conditions:
            condition["paths"] = list(paths)
    return {
        "id": identifier,
        "when": {operator: conditions},
        "activate_tags": [tag],
    }


def _path_rule(
    identifier: str,
    operator: str,
    condition_type: str,
    patterns: tuple[str, ...],
    tag: str,
) -> JsonDocument:
    return _detection_rule(identifier, condition_type, operator, patterns, tag)


def _documentation_path_rule(operator: str) -> list[JsonDocument]:
    return [
        _path_rule(
            "doc-project",
            operator,
            "path_exists",
            ("docs/*.md", "mkdocs.yml"),
            "documentation",
        )
    ]


def _file_rule(
    identifier: str,
    operator: str,
    condition_type: str,
    pattern: str,
    tag: str,
    paths: tuple[str, ...],
) -> JsonDocument:
    return _detection_rule(
        identifier,
        condition_type,
        operator,
        (pattern,),
        tag,
        paths=paths,
    )


def test_v2_detection_rules_path_exists_activates_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules = _documentation_path_rule("all")
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project)
    (project / "mkdocs.yml").write_text("site_name: Test\n", encoding="utf-8")

    projector.apply()

    target = project / ".agents" / "skills"
    assert (target / "documentation-skill" / "SKILL.md").is_file()
    assert "documentation" in _selected_tags(project)


def test_v2_detection_rules_path_exists_any_operator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules = _documentation_path_rule("any")
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project)

    projector.apply()

    assert (project / ".agents" / "skills" / "documentation-skill").is_dir()


def test_v2_detection_rules_path_exists_all_requires_all(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules = _documentation_path_rule("all")
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project)

    projector.apply()

    assert not (project / ".agents" / "skills" / "documentation-skill").exists()


def test_v2_detection_rules_path_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules = [_path_rule("no-docs", "all", "path_missing", ("docs/*.md",), "no-docs")]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)

    projector.apply()

    assert "no-docs" in _selected_tags(project)


def test_v2_detection_rules_file_contains(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules = [
        _file_rule(
            "flext-usage",
            "any",
            "file_contains",
            "flext",
            "flext",
            ("docs/*.md", "pyproject.toml"),
        )
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    _write_doc(project, "readme.md")
    (project / "docs" / "readme.md").write_text("# Uses flext\n", encoding="utf-8")

    projector.apply()

    assert (project / ".agents" / "skills" / "flext-skill").is_dir()


def test_v2_detection_rules_file_not_contains(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules = [
        _file_rule(
            "no-flext", "all", "file_not_contains", "flext", "no-flext", ("src/*.py",)
        )
    ]
    project, projector = _make_v2_project(tmp_path, monkeypatch, rules)
    source = project / "src"
    source.mkdir()
    (source / "main.py").write_text("import requests\n", encoding="utf-8")

    projector.apply()

    assert "no-flext" in _selected_tags(project)


def test_v2_detection_rules_when_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules: list[JsonDocument] = [
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
    rules: list[JsonDocument] = [
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
    rules: list[JsonDocument] = [
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
    rules: list[JsonDocument] = [
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
    rules = [
        _path_rule("duplicate", "all", "path_exists", ("one.txt",), "one"),
        _path_rule("duplicate", "all", "path_exists", ("two.txt",), "two"),
    ]
    _, projector = _make_v2_project(tmp_path, monkeypatch, rules)

    with pytest.raises(ValueError, match="duplicates detection rule id duplicate"):
        projector.apply()


def test_v2_detection_rules_merge_with_selected_tags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rules = [
        _path_rule(
            "python-project", "all", "path_exists", ("pyproject.toml",), "python"
        )
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

    selected = _selected_tags(project)
    assert {"python", "documentation"} <= set(selected)


def test_v2_selection_field_contracts_are_exact() -> None:
    assert set(_SELECTION_FIELDS_V1) == {
        "agents",
        "opt_ins",
        "selected_tags",
        "version",
    }
    assert set(_SELECTION_FIELDS_V2) == set(_SELECTION_FIELDS_V1) | {"detection_rules"}
    assert set(_SELECTION_FIELDS_V3) == {
        "agents",
        "detection_catalog_digest",
        "opt_ins",
        "project_profile",
        "selected_tags",
        "version",
    }


# ===== End v2 detection_rules tests =====


# ===== Alias primary surfaces =====


def test_alias_surfaces_link_to_the_primary_and_reach_fixed_point(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projector, project = _dual_skill_project(tmp_path, monkeypatch)

    projector.apply()
    projector.check()

    primary = project / ".claude" / "skills"
    alias = project / ".agents" / "skills"
    assert (primary / "project-guidance" / "SKILL.md").is_file()
    link = alias / "project-guidance"
    assert link.is_symlink()
    assert link.readlink() == Path("../../.claude/skills/project-guidance")
    managed = json.loads((alias / Projector.MANIFEST).read_text(encoding="utf-8"))[
        "managed"
    ]
    assert managed["project-guidance"]["link_target"] == (
        "../../.claude/skills/project-guidance"
    )
    primary_managed = json.loads(
        (primary / Projector.MANIFEST).read_text(encoding="utf-8")
    )["managed"]
    assert primary_managed["project-guidance"]["link_target"] is None

    first = Catalog.physical_tree_contract(primary)
    projector.apply()
    projector.check()
    assert Catalog.physical_tree_contract(primary) == first
    assert not tuple(project.rglob(".agents-stage.*"))

    link.unlink()
    projector.apply()
    assert link.is_symlink()
    assert link.readlink() == Path("../../.claude/skills/project-guidance")


def test_alias_link_divergence_requires_adjudication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projector, project = _dual_skill_project(tmp_path, monkeypatch)
    projector.apply()

    link = project / ".agents" / "skills" / "project-guidance"
    link.unlink()
    link.symlink_to(project / ".claude" / "skills")

    with pytest.raises(ValueError, match="projection destination symlink forbidden"):
        projector.apply()
    assert link.readlink() == project / ".claude" / "skills"

    link.unlink()
    link.mkdir()

    with pytest.raises(ValueError, match="unadjudicated projection divergence"):
        projector.apply()
    assert link.is_dir() and not link.is_symlink()


def _flext_consumer(
    tmp_path: Path, content: str, *, git: bool
) -> tuple[Projector, Path]:
    _, projector = _source(
        tmp_path,
        project_detection_rules=[flext_detection_rule()],
    )
    project = tmp_path / "consumer"
    project.mkdir()
    if git:
        (project / ".git").mkdir()
    (project / "pyproject.toml").write_text(content, encoding="utf-8")
    return projector, project


def test_canonical_marker_authorizes_minimal_project_selection(
    tmp_path: Path,
) -> None:
    projector, project = _flext_consumer(tmp_path, "# @flext-managed\n", git=True)

    authorization = projector.authorize(project)

    assert authorization.selected
    selection = json.loads(authorization.path.read_text(encoding="utf-8"))
    assert selection == {
        "agents": [],
        "detection_catalog_digest": Projector._detection_catalog_digest(
            projector.config.project_detection_rules
        ),
        "opt_ins": [],
        "project_profile": "internal_flext",
        "selected_tags": [],
        "version": 3,
    }
    second = projector.authorize(project)
    assert second.path.read_bytes() == authorization.path.read_bytes()


def test_check_rejects_stale_detection_digest_without_mutating_selection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    projector, project = _flext_consumer(tmp_path, "# @flext-managed\n", git=True)
    monkeypatch.chdir(project)
    authorization = projector.authorize(project)
    payload = json.loads(authorization.path.read_text(encoding="utf-8"))
    payload["detection_catalog_digest"] = "0" * 64
    stale = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    authorization.path.write_text(stale, encoding="utf-8")

    with pytest.raises(ValueError, match="detection catalog differs"):
        projector.check()

    assert authorization.path.read_text(encoding="utf-8") == stale
    projector.apply()
    projector.check()


def test_canonical_marker_does_not_create_unauthorized_selection(
    tmp_path: Path,
) -> None:
    projector, project = _flext_consumer(tmp_path, "# another project\n", git=False)

    authorization = projector.authorize(project)

    assert not authorization.selected
    assert not authorization.path.exists()
