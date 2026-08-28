from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from agents_governance.catalog import Catalog
from agents_governance.projection import ProjectionFinding, Projector

_AGENT_TAGS = (
    "provenance:agents-owned",
    "updates:manual",
    "usage:on-demand",
)
_FROZEN_TAGS = (
    "provenance:agents-owned",
    "updates:forbidden",
    "usage:frozen",
)


def _skill_directory(
    root: Path, category: str = "agent-wide", name: str = "example"
) -> Path:
    return root / "skills" / category / name


def _write_skill(
    root: Path,
    category: str = "agent-wide",
    name: str = "example",
    tags: tuple[str, ...] = _AGENT_TAGS,
    body: str = "# Example\n",
) -> Path:
    directory = _skill_directory(root, category, name)
    directory.mkdir(parents=True, exist_ok=True)
    encoded_tags = json.dumps(tags, separators=(",", ":"))
    (directory / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        f"description: Apply {name} when its governed capability is required.\n"
        "metadata:\n"
        f"  aihub.tags: '{encoded_tags}'\n"
        "---\n"
        f"{body}",
        encoding="utf-8",
    )
    return directory


def _projector(
    tmp_path: Path,
    target: Path,
    *,
    category: str = "agent-wide",
    tags: tuple[str, ...] = _AGENT_TAGS,
    extra_skills: tuple[tuple[str, str, tuple[str, ...]], ...] = (),
) -> Projector:
    (tmp_path / "config").mkdir()
    _write_skill(tmp_path, category, tags=tags)
    for extra_category, name, extra_tags in extra_skills:
        _write_skill(tmp_path, extra_category, name, extra_tags)
    skills_config = {
        "version": 2,
        "budgets": {
            "router_tokens": 500,
            "frozen_tokens": 1200,
            "on_demand_tokens": 5000,
            "max_lines": 500,
        },
    }
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(skills_config), encoding="utf-8"
    )
    unsupported = {
        "status": "UNSUPPORTED",
        "reason": "UNSUPPORTED: not enabled by this focused fixture",
    }
    projections: dict[str, object] = {
        "version": 4,
        "manifest_version": 4,
        "providers": {
            provider: {
                context: {
                    surface: dict(unsupported)
                    for surface in ("skills", "commands", "agents", "rules")
                }
                for context in ("personal", "project")
            }
            for provider in (
                "antigravity",
                "claude",
                "codex",
                "copilot",
                "cursor",
                "gemini",
                "opencode",
            )
        },
    }
    relative_target = target.relative_to(Path.home()).as_posix()
    providers = projections["providers"]
    assert isinstance(providers, dict)
    providers["claude"]["personal"]["skills"] = {
        "status": "SUPPORTED",
        "path": f"${{HOME}}/{relative_target}",
    }
    providers["codex"]["project"]["skills"] = {
        "status": "SUPPORTED",
        "path": ".agents/skills",
    }
    providers["cursor"]["project"]["commands"] = {
        "status": "SUPPORTED",
        "path": ".cursor/commands",
        "max_tokens": 100_000,
    }
    providers["antigravity"]["project"]["rules"] = {
        "status": "SUPPORTED",
        "path": ".agents/rules",
    }
    (tmp_path / "config" / "projections.json").write_text(
        json.dumps(projections), encoding="utf-8"
    )
    return Projector(Catalog(tmp_path))


def _configure_cell(
    projector: Projector,
    provider: str,
    context: str,
    surface: str,
    cell: dict[str, object],
) -> Projector:
    path = projector.catalog.root / "config" / "projections.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["providers"][provider][context][surface] = cell
    path.write_text(json.dumps(payload), encoding="utf-8")
    return Projector(Catalog(projector.catalog.root))


def _git_project(path: Path) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    return path


def _write_command(
    root: Path,
    name: str,
    *,
    route: str,
    body: str,
) -> Path:
    commands = root / "commands"
    commands.mkdir(exist_ok=True)
    path = commands / f"{name}.md"
    path.write_text(
        "---\n"
        f"name: {name}\n"
        f"description: Run the approved {name} workflow through its owner.\n"
        "metadata:\n"
        f'  aihub.tags: \'["intent:inspection","risk:read","route:{route}"]\'\n'
        "---\n\n"
        f"{body}",
        encoding="utf-8",
    )
    return path


def test_apply_is_idempotent(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)

    assert projector.apply("personal") == []
    first = (target / Projector.MANIFEST).read_bytes()
    assert projector.apply("personal") == []

    assert not (target / "example").is_symlink()
    assert (target / "example" / "SKILL.md").read_bytes() == (
        _skill_directory(tmp_path) / "SKILL.md"
    ).read_bytes()
    assert (target / Projector.MANIFEST).read_bytes() == first
    assert projector.check("personal") == []


def test_manifest_digest_contract_drift_is_reconciled(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    manifest_path = target / Projector.MANIFEST
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["managed"]["example"]["origin"] = "legacy-owner"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    assert [item.message for item in projector.check("personal")] == [
        "managed metadata update"
    ]
    assert projector.apply("personal") == []
    assert projector.check("personal") == []


def test_manifest_v4_ownership_survives_a_real_source_content_update(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    manifest_path = target / Projector.MANIFEST
    original_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert original_manifest["version"] == 4
    assert original_manifest["owner"] == "agents-governance"
    assert original_manifest["providers"] == ["claude"]
    assert original_manifest["context"] == "personal"
    assert original_manifest["surface"] == "skills"
    destination = target / "example"
    metadata = original_manifest["managed"]["example"]
    assert metadata["source_digest"] == Catalog.digest_tree(destination)
    assert metadata["physical_digest"] == Catalog.physical_tree_contract(destination)
    assert metadata["source_type"] == "skill"
    assert metadata["slug"] == "example"
    assert metadata["destination"] == "example"
    assert metadata["adapter_version"] == 1

    source_file = _skill_directory(tmp_path) / "SKILL.md"
    _write_skill(tmp_path, body="# Changed\n")
    projector = Projector(Catalog(tmp_path))

    assert [item.message for item in projector.check("personal")] == ["managed update"]
    assert projector.apply("personal") == []
    updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert updated_manifest["version"] == 4
    assert updated_manifest["managed"]["example"][
        "source_digest"
    ] == Catalog.digest_tree(source_file.parent)
    assert projector.check("personal") == []


@pytest.mark.parametrize(
    "invalid_manifest",
    ["version-2", "managed-list"],
)
def test_invalid_projection_manifest_blocks_check_and_apply_without_rewrite(
    tmp_path: Path, invalid_manifest: str
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    manifest_path = target / Projector.MANIFEST
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if invalid_manifest == "version-2":
        payload["version"] = 2
    else:
        payload["managed"] = []
    manifest_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    before = manifest_path.read_bytes()

    check_findings = projector.check("personal")
    apply_findings = projector.apply("personal")

    assert [finding.message for finding in check_findings] == [
        "invalid manifest: projection manifest must use version 4"
        if invalid_manifest == "version-2"
        else "invalid manifest: projection manifest managed field must be an object"
    ]
    assert apply_findings == check_findings
    assert manifest_path.read_bytes() == before


def test_apply_all_propagates_a_child_surface_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projector = _projector(tmp_path, tmp_path / "target")
    failure = ProjectionFinding("test", "target", "injected child failure")
    checked: list[str] = []

    def injected_check(
        _scope: str,
        _selected: str | None = None,
        surface: str = "skills",
        _project_roots: tuple[Path, ...] = (),
        *,
        provider: str | None = None,
    ) -> list[ProjectionFinding]:
        assert provider is None
        checked.append(surface)
        return [] if surface == "all" else [failure]

    monkeypatch.setattr(projector, "check", injected_check)

    assert projector.apply("personal", surface="all") == [failure]
    assert checked == ["all", "skills"]


def test_mode_drift_is_detected_and_repaired_from_the_physical_source(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    source_file = _skill_directory(tmp_path) / "SKILL.md"
    destination_file = target / "example" / "SKILL.md"
    destination_file.chmod(0o600)

    assert [item.message for item in projector.check("personal")] == [
        "managed physical update"
    ]
    assert projector.apply("personal") == []
    assert destination_file.stat().st_mode & 0o777 == source_file.stat().st_mode & 0o777
    assert projector.check("personal") == []


def test_commands_and_rules_are_independently_projected(tmp_path: Path) -> None:
    target = tmp_path / "skills-target"
    projector = _projector(tmp_path, target)
    commands_target = tmp_path / "home" / ".claude" / "commands"
    rules_target = tmp_path / "home" / ".claude" / "rules"
    projector = _configure_cell(
        projector,
        "claude",
        "personal",
        "commands",
        {
            "status": "SUPPORTED",
            "path": f"${{HOME}}/{commands_target.relative_to(Path.home())}",
            "max_tokens": 100_000,
        },
    )
    projector = _configure_cell(
        projector,
        "claude",
        "personal",
        "rules",
        {
            "status": "SUPPORTED",
            "path": f"${{HOME}}/{rules_target.relative_to(Path.home())}",
        },
    )
    _write_command(
        tmp_path,
        "inspect-repository",
        route="agent",
        body="# Inspect repository\n\nInspect the explicit repository.\n",
    )
    _write_command(
        tmp_path,
        "review-project",
        route="project",
        body="# Review project\n\nReview the current project.\n",
    )
    rule = tmp_path / "rules" / "security"
    rule.mkdir(parents=True)
    (rule / "closure.md").write_text("# Closure\n", encoding="utf-8")

    assert projector.apply("personal", surface="commands") == []
    assert projector.apply("personal", surface="rules") == []
    personal_command = commands_target / "inspect-repository.md"
    assert "disable-model-invocation: true" in personal_command.read_text(
        encoding="utf-8"
    )
    assert not (commands_target / "review-project.md").exists()
    assert (rules_target / "security--closure.md").read_text(
        encoding="utf-8"
    ) == "# Closure\n"
    assert projector.check("personal", surface="commands") == []
    assert projector.check("personal", surface="rules") == []

    project = _git_project(tmp_path / "project")
    assert (
        projector.apply("projects", surface="commands", project_roots=(project,)) == []
    )
    assert projector.apply("projects", surface="rules", project_roots=(project,)) == []
    assert (
        (project / ".cursor" / "commands" / "review-project.md")
        .read_text(encoding="utf-8")
        .endswith("Review the current project.\n")
    )
    assert not (project / ".cursor" / "commands" / "inspect-repository.md").exists()
    assert not (project / ".agents" / "rules" / "security").exists()
    assert (
        projector.check("projects", surface="commands", project_roots=(project,)) == []
    )
    projection_payload = json.loads(
        (tmp_path / "config" / "projections.json").read_text(encoding="utf-8")
    )
    assert set(projection_payload) == {"manifest_version", "providers", "version"}


def test_project_command_render_rejects_nonportable_output(
    tmp_path: Path,
) -> None:
    target = tmp_path / "skills-target"
    projector = _projector(tmp_path, target)
    _write_command(
        tmp_path,
        "review-project",
        route="project",
        body="Inspect ~/.claude/skills for the personal client.\n",
    )

    project = _git_project(tmp_path / "project")
    findings = projector.check("projects", surface="commands", project_roots=(project,))
    assert "cross-repository local path" in {item.message for item in findings}


def test_project_commands_render_every_configured_native_provider_at_fixed_point(
    tmp_path: Path,
) -> None:
    projector = _projector(tmp_path, tmp_path / "skills-target")
    for provider in ("claude", "gemini", "opencode"):
        projector = _configure_cell(
            projector,
            provider,
            "project",
            "commands",
            {
                "status": "SUPPORTED",
                "path": f".{provider}/commands",
                "max_tokens": 100_000,
            },
        )
    _write_command(
        tmp_path,
        "review-project",
        route="project",
        body="# Review project\n\nReview the current project.\n",
    )
    project = _git_project(tmp_path / "project")

    assert (
        projector.apply("projects", surface="commands", project_roots=(project,)) == []
    )
    assert (project / ".claude" / "commands" / "review-project.md").is_file()
    assert (project / ".cursor" / "commands" / "review-project.md").is_file()
    assert (project / ".gemini" / "commands" / "review-project.toml").is_file()
    assert (project / ".opencode" / "commands" / "review-project.md").is_file()
    assert (
        projector.check("projects", surface="commands", project_roots=(project,)) == []
    )
    assert (
        projector.apply("projects", surface="commands", project_roots=(project,)) == []
    )


def test_unsupported_personal_command_provider_is_explicit_and_write_free(
    tmp_path: Path,
) -> None:
    projector = _projector(tmp_path, tmp_path / "skills-target")
    _write_command(
        tmp_path,
        "inspect-repository",
        route="agent",
        body="Inspect the explicit repository.\n",
    )

    findings = projector.apply("personal", "codex", surface="commands")

    assert [finding.message for finding in findings] == [
        "UNSUPPORTED: not enabled by this focused fixture"
    ]
    assert not (tmp_path / "codex-commands").exists()


def test_copilot_command_projection_is_explicitly_unsupported(
    tmp_path: Path,
) -> None:
    target = tmp_path / "home" / ".claude" / "commands"
    projector = _projector(tmp_path, tmp_path / "skills-target")
    _write_command(
        tmp_path,
        "inspect-repository",
        route="agent",
        body="Inspect the explicit repository.\n",
    )

    findings = projector.apply("personal", "copilot", surface="commands")

    assert [finding.message for finding in findings] == [
        "UNSUPPORTED: not enabled by this focused fixture"
    ]
    assert not target.exists()


def test_personal_skill_can_keep_personal_tool_home_contract(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    _write_skill(
        tmp_path,
        body="Inspect ~/.claude/skills for the personal client.\n",
    )

    assert projector.apply("personal") == []
    assert projector.check("personal") == []


def test_project_generic_skill_rejects_personal_tool_home_contract(
    tmp_path: Path,
) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="project-wide",
    )
    _write_skill(
        tmp_path,
        "project-wide",
        body="Inspect ~/.claude/skills before delivery.\n",
    )
    projector = Projector(Catalog(tmp_path))
    project = _git_project(tmp_path / "project")

    findings = projector.check("projects", surface="skills", project_roots=(project,))

    assert "cross-repository local path" in {item.message for item in findings}


def test_foreign_collision_blocks_apply_and_is_preserved(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    foreign = target / "example"
    foreign.mkdir(parents=True)
    marker = foreign / "foreign.txt"
    marker.write_text("preserve", encoding="utf-8")

    findings = projector.apply("personal")

    assert [finding.message for finding in findings] == ["foreign collision"]
    assert marker.read_text(encoding="utf-8") == "preserve"
    assert not (foreign / "SKILL.md").exists()
    assert not (target / ".agents-archive").exists()


def test_modified_stale_managed_entry_blocks_apply(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    stale = target / "example"
    (stale / "operator.txt").write_text("preserve", encoding="utf-8")
    _write_skill(tmp_path, tags=_FROZEN_TAGS)
    projector = Projector(Catalog(tmp_path))

    findings = projector.apply("personal")

    assert [finding.message for finding in findings] == ["modified stale managed entry"]
    assert (stale / "operator.txt").read_text(encoding="utf-8") == "preserve"
    assert not (target / ".agents-archive").exists()


def test_unmodified_stale_managed_entry_is_removed_without_archive(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    stale = target / "example"
    _write_skill(tmp_path, tags=_FROZEN_TAGS)
    projector = Projector(Catalog(tmp_path))

    assert projector.apply("personal") == []
    assert not stale.exists()
    assert not (target / ".agents-archive").exists()


def test_destination_symlink_blocks_apply_and_is_preserved(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    target.mkdir()
    destination = target / "example"
    destination.symlink_to(foreign, target_is_directory=True)

    findings = projector.apply("personal")

    assert [item.message for item in findings] == ["destination symlink forbidden"]
    assert destination.is_symlink()
    assert destination.resolve() == foreign
    assert not (foreign / "SKILL.md").exists()


def test_conditional_project_skill_is_not_personal(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(
        tmp_path,
        target,
        category="technology",
        tags=(
            "activation:detected",
            "detect:marker:pyproject.toml",
            "provenance:agents-owned",
            "route:project",
            "technology:python",
            "updates:manual",
            "usage:on-demand",
        ),
    )

    assert projector.apply("personal") == []
    assert not (target / "example").exists()


def test_tag_derived_markers_detect_project_capabilities(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(
        tmp_path,
        target,
        category="technology",
        tags=(
            "activation:detected",
            "detect:marker:go.mod",
            "provenance:agents-owned",
            "route:project",
            "technology:go",
            "updates:manual",
            "usage:on-demand",
        ),
        extra_skills=(
            (
                "technology",
                "rust-example",
                (
                    "activation:detected",
                    "detect:marker:Cargo.toml",
                    "provenance:agents-owned",
                    "route:project",
                    "technology:rust",
                    "updates:manual",
                    "usage:on-demand",
                ),
            ),
        ),
    )
    project = tmp_path / "project"
    project.mkdir()
    (project / "go.mod").write_text("module example\n", encoding="utf-8")

    assert projector.detected_project_capabilities(project) == ("technology:go",)


def test_tag_derived_dependencies_detect_framework_and_tool_capabilities(
    tmp_path: Path,
) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="tool",
        tags=(
            "activation:detected",
            "detect:dependency:npm:@playwright/test",
            "detect:dependency:npm:playwright",
            "provenance:agents-owned",
            "route:project",
            "tool:playwright",
            "updates:manual",
            "usage:on-demand",
        ),
        extra_skills=(
            (
                "framework",
                "react-example",
                (
                    "activation:detected",
                    "detect:dependency:npm:react",
                    "framework:react",
                    "provenance:agents-owned",
                    "route:project",
                    "updates:manual",
                    "usage:on-demand",
                ),
            ),
        ),
    )
    project = tmp_path / "project"
    project.mkdir()
    (project / "package.json").write_text(
        json.dumps(
            {
                "dependencies": {"react": "latest"},
                "devDependencies": {"@playwright/test": "latest"},
            }
        ),
        encoding="utf-8",
    )

    assert projector.detected_project_capabilities(project) == (
        "framework:react",
        "tool:playwright",
    )


def test_owned_file_detectors_ignore_managed_projection_content(
    tmp_path: Path,
) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="technology",
        tags=(
            "activation:detected",
            "detect:owned-extension:.go",
            "provenance:agents-owned",
            "route:project",
            "technology:go",
            "updates:manual",
            "usage:on-demand",
        ),
        extra_skills=(
            (
                "tool",
                "openapi-example",
                (
                    "activation:detected",
                    "detect:owned-glob:openapi/*.yaml",
                    "provenance:agents-owned",
                    "route:project",
                    "tool:openapi",
                    "updates:manual",
                    "usage:on-demand",
                ),
            ),
        ),
    )
    project = tmp_path / "project"
    managed = project / ".agents" / "skills"
    managed.mkdir(parents=True)
    (managed / "generated.go").write_text("package generated\n", encoding="utf-8")

    assert projector.detected_project_capabilities(project) == ()

    source = project / "src"
    source.mkdir()
    (source / "main.go").write_text("package main\n", encoding="utf-8")
    assert projector.detected_project_capabilities(project) == ("technology:go",)

    contract = project / "openapi"
    contract.mkdir()
    (contract / "service.yaml").write_text("openapi: 3.1.0\n", encoding="utf-8")
    assert projector.detected_project_capabilities(project) == (
        "technology:go",
        "tool:openapi",
    )


def test_tag_derived_marker_detects_domain_capability(tmp_path: Path) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="domain",
        tags=(
            "activation:detected-or-opt-in",
            "detect:marker:MLproject",
            "detect:opt-in:machine-learning",
            "domain:mle",
            "provenance:agents-owned",
            "route:project",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    project = tmp_path / "project"
    project.mkdir()
    (project / "MLproject").write_text("name: example\n", encoding="utf-8")

    assert projector.detected_project_capabilities(project) == ("domain:mle",)


def test_project_opt_in_capability_is_not_activated_without_explicit_input(
    tmp_path: Path,
) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="tool",
        tags=(
            "activation:opt-in",
            "detect:opt-in:scope-code-navigation",
            "provenance:agents-owned",
            "route:project",
            "tool:scope-code-navigation",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    project = tmp_path / "project"
    project.mkdir()

    assert projector.detected_project_capabilities(project) == ()


def test_flutter_requires_structured_flutter_sdk_dependency(tmp_path: Path) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="framework",
        tags=(
            "activation:detected",
            "detect:dependency:dart:sdk:flutter",
            "framework:flutter",
            "provenance:agents-owned",
            "route:project",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    project = tmp_path / "project"
    project.mkdir()
    pubspec = project / "pubspec.yaml"
    pubspec.write_text(
        "name: dart_only\ndependencies:\n  collection: ^1.19.0\n",
        encoding="utf-8",
    )

    assert projector.detected_project_capabilities(project) == ()

    pubspec.write_text(
        "name: flutter_app\ndependencies:\n  flutter:\n    sdk: flutter\n",
        encoding="utf-8",
    )

    assert projector.detected_project_capabilities(project) == ("framework:flutter",)


def test_flutter_pubspec_symlink_fails_closed(tmp_path: Path) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="framework",
        tags=(
            "activation:detected",
            "detect:dependency:dart:sdk:flutter",
            "framework:flutter",
            "provenance:agents-owned",
            "route:project",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    project = tmp_path / "project"
    project.mkdir()
    external = tmp_path / "pubspec.yaml"
    external.write_text(
        "dependencies:\n  flutter:\n    sdk: flutter\n", encoding="utf-8"
    )
    pubspec = project / "pubspec.yaml"
    pubspec.symlink_to(external)

    with pytest.raises(ValueError, match="pubspec.yaml symlink forbidden"):
        projector.detected_project_capabilities(project)


def test_malformed_flutter_pubspec_fails_closed(tmp_path: Path) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="framework",
        tags=(
            "activation:detected",
            "detect:dependency:dart:sdk:flutter",
            "framework:flutter",
            "provenance:agents-owned",
            "route:project",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    project = tmp_path / "project"
    project.mkdir()
    (project / "pubspec.yaml").write_text("dependencies: [\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid pubspec.yaml"):
        projector.detected_project_capabilities(project)


def test_failed_copy_preserves_valid_destination_and_cleans_staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    destination = target / "example" / "SKILL.md"
    original = destination.read_bytes()
    _write_skill(tmp_path, body="# Changed\n")
    projector = Projector(Catalog(tmp_path))

    def fail_copy(_source: Path, staged: Path) -> None:
        staged.mkdir()
        (staged / "partial").write_text("partial\n", encoding="utf-8")
        raise RuntimeError("copy failed")

    monkeypatch.setattr(Projector, "_copy_tree", staticmethod(fail_copy))

    with pytest.raises(RuntimeError, match="copy failed"):
        projector.apply("personal")

    assert destination.read_bytes() == original
    assert list(target.glob(".agents-stage.*")) == []


def test_failed_projection_rollback_preserves_backup_and_primary_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    destination = target / "example"
    original = (destination / "SKILL.md").read_bytes()
    _write_skill(tmp_path, body="# Changed\n")
    projector = Projector(Catalog(tmp_path))
    original_replace = Path.replace

    def fail_promotion_and_rollback(source: Path, target_path: Path) -> Path:
        if source.name == "new-0" and target_path == destination:
            raise OSError("injected projection promotion failure")
        if source.name == "old-0" and target_path == destination:
            raise OSError("injected projection rollback failure")
        return original_replace(source, target_path)

    monkeypatch.setattr(Path, "replace", fail_promotion_and_rollback)

    with pytest.raises(
        OSError, match="injected projection promotion failure"
    ) as caught:
        projector.apply("personal")

    assert any(
        "injected projection rollback failure" in note
        for note in getattr(caught.value, "__notes__", ())
    )
    staging = list(target.glob(".agents-stage.*"))
    assert len(staging) == 1
    assert (staging[0] / "old-0" / "SKILL.md").read_bytes() == original


@pytest.mark.parametrize("source_kind", ["file", "directory"])
def test_linux_copy_requests_reflink(
    monkeypatch, tmp_path: Path, source_kind: str
) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    if source_kind == "file":
        source.write_text("source\n", encoding="utf-8")
    else:
        source.mkdir()
    calls: list[list[str]] = []

    def record(command: list[str], *, check: bool) -> subprocess.CompletedProcess[str]:
        assert check is True
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("agents_governance.projection.sys.platform", "linux")
    monkeypatch.setattr("agents_governance.projection.subprocess.run", record)

    Projector._copy_tree(source, destination)

    assert calls == [
        [
            "cp",
            "--archive",
            "--reflink=auto",
            "--no-target-directory",
            str(source),
            str(destination),
        ]
    ]


def test_physical_copy_is_independent_and_contains_no_symlink(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    source_file = source / "value.txt"
    source_file.write_text("source\n", encoding="utf-8")
    source_file.chmod(0o640)

    Projector._copy_tree(source, destination)
    assert (destination / "value.txt").stat().st_mode & 0o777 == 0o640
    (destination / "value.txt").write_text("destination\n", encoding="utf-8")

    assert source_file.read_text(encoding="utf-8") == "source\n"
    assert not any(path.is_symlink() for path in destination.rglob("*"))


def test_physical_copy_rejects_special_files_before_invoking_cp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    os.mkfifo(source / "events.fifo")

    def forbidden_cp(*_args: object, **_kwargs: object) -> None:
        pytest.fail("cp must not run for a source containing a special file")

    monkeypatch.setattr("agents_governance.projection.subprocess.run", forbidden_cp)

    with pytest.raises(ValueError, match="unsupported file type"):
        Projector._copy_tree(source, destination)

    assert not destination.exists()


@pytest.mark.parametrize("operation", ("check", "apply"))
def test_unknown_project_target_fails_closed(operation: str, tmp_path: Path) -> None:
    projector = _projector(tmp_path, tmp_path / "target")
    project = _git_project(tmp_path / "project")

    findings = (
        projector.check("projects", "typo-does-not-exist", project_roots=(project,))
        if operation == "check"
        else projector.apply(
            "projects", "typo-does-not-exist", project_roots=(project,)
        )
    )

    assert [(item.target, item.message) for item in findings] == [
        ("typo-does-not-exist", "unknown project projection target")
    ]
    assert not (project / ".agents").exists()


def test_zero_project_roots_fails_closed(tmp_path: Path) -> None:
    projector = _projector(tmp_path, tmp_path / "target")

    findings = projector.check("projects", project_roots=())

    assert [item.message for item in findings] == ["no project roots supplied"]


def test_project_roots_must_be_unique_exact_git_toplevels(tmp_path: Path) -> None:
    projector = _projector(tmp_path, tmp_path / "target")
    project = _git_project(tmp_path / "project")
    nested = project / "nested"
    nested.mkdir()

    nested_findings = projector.check("projects", project_roots=(nested,))
    duplicate_findings = projector.check("projects", project_roots=(project, project))

    assert [item.message for item in nested_findings] == [
        "project root is not the exact Git top-level"
    ]
    assert [item.message for item in duplicate_findings] == ["duplicate project root"]


def test_project_root_must_exist_and_be_a_git_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    projector = _projector(tmp_path, tmp_path / "target")
    missing = tmp_path / "missing"
    plain = tmp_path / "plain"
    plain.mkdir()

    def not_a_repository(
        command: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 128, "", "not a repository")

    monkeypatch.setattr("agents_governance.projection.subprocess.run", not_a_repository)

    missing_findings = projector.check("projects", project_roots=(missing,))
    plain_findings = projector.check("projects", project_roots=(plain,))

    assert [item.message for item in missing_findings] == [
        "project root is not a directory"
    ]
    assert [item.message for item in plain_findings] == [
        "project root is not a Git repository"
    ]


def test_project_root_symlink_is_blocked_and_preserved(tmp_path: Path) -> None:
    projector = _projector(tmp_path, tmp_path / "target")
    project = _git_project(tmp_path / "project")
    link = tmp_path / "project-link"
    link.symlink_to(project, target_is_directory=True)

    findings = projector.apply("projects", project_roots=(link,))

    assert [item.message for item in findings] == ["project root symlink forbidden"]
    assert link.is_symlink()


def test_project_target_must_remain_confined(tmp_path: Path) -> None:
    projector = _projector(tmp_path, tmp_path / "target")
    with pytest.raises(
        ValueError, match="project path must remain repository-relative"
    ):
        _configure_cell(
            projector,
            "codex",
            "project",
            "skills",
            {"status": "SUPPORTED", "path": "../outside"},
        )
    assert not (tmp_path / "outside").exists()


def test_project_target_ancestor_symlink_is_blocked_and_preserved(
    tmp_path: Path,
) -> None:
    projector = _projector(tmp_path, tmp_path / "target", category="project-wide")
    project = _git_project(tmp_path / "project")
    external = tmp_path / "external"
    external.mkdir()
    (project / ".agents").symlink_to(external, target_is_directory=True)

    findings = projector.apply("projects", surface="skills", project_roots=(project,))

    assert [item.message for item in findings] == ["projection path symlink forbidden"]
    assert (project / ".agents").is_symlink()
    assert not (external / "skills").exists()


def test_project_projection_copies_detected_capability_and_reaches_fixed_point(
    tmp_path: Path,
) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="technology",
        tags=(
            "activation:detected",
            "detect:marker:go.mod",
            "provenance:agents-owned",
            "route:project",
            "technology:go",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    project = _git_project(tmp_path / "project")
    (project / "go.mod").write_text("module example\n", encoding="utf-8")

    assert projector.apply("projects", surface="skills", project_roots=(project,)) == []
    destination = project / ".agents" / "skills" / "example"
    first = (project / ".agents" / "skills" / Projector.MANIFEST).read_bytes()
    assert destination.is_dir() and not destination.is_symlink()
    assert projector.apply("projects", surface="skills", project_roots=(project,)) == []
    assert (project / ".agents" / "skills" / Projector.MANIFEST).read_bytes() == first
    assert projector.check("projects", surface="skills", project_roots=(project,)) == []


def test_source_symlink_blocks_projection_and_is_preserved(tmp_path: Path) -> None:
    projector = _projector(tmp_path, tmp_path / "target")
    source = _skill_directory(tmp_path)
    external = tmp_path / "external.md"
    external.write_text("external\n", encoding="utf-8")
    link = source / "external.md"
    link.symlink_to(external)

    findings = projector.apply("personal")

    assert [item.message for item in findings] == ["source symlink forbidden"]
    assert link.is_symlink()
    assert external.read_text(encoding="utf-8") == "external\n"


def test_source_root_symlink_blocks_projection_and_is_preserved(tmp_path: Path) -> None:
    projector = _projector(tmp_path, tmp_path / "target")
    source = _skill_directory(tmp_path)
    (source / "SKILL.md").unlink()
    source.rmdir()
    external = tmp_path / "external-skill"
    external.mkdir()
    (external / "SKILL.md").write_text("external\n", encoding="utf-8")
    source.symlink_to(external, target_is_directory=True)

    findings = projector.apply("personal")

    assert [item.message for item in findings] == ["source symlink forbidden"]
    assert source.is_symlink()
    assert (external / "SKILL.md").read_text(encoding="utf-8") == "external\n"


def test_destination_descendant_symlink_blocks_apply_and_is_preserved(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    external = tmp_path / "external.txt"
    external.write_text("preserve\n", encoding="utf-8")
    link = target / "example" / "external.txt"
    link.symlink_to(external)

    findings = projector.apply("personal")

    assert [item.message for item in findings] == ["destination symlink forbidden"]
    assert link.is_symlink()
    assert external.read_text(encoding="utf-8") == "preserve\n"


def test_project_capability_marker_symlink_fails_closed(tmp_path: Path) -> None:
    projector = _projector(
        tmp_path,
        tmp_path / "target",
        category="technology",
        tags=(
            "activation:detected",
            "detect:marker:go.mod",
            "provenance:agents-owned",
            "route:project",
            "technology:go",
            "updates:manual",
            "usage:on-demand",
        ),
    )
    project = _git_project(tmp_path / "project")
    external = tmp_path / "external-go.mod"
    external.write_text("module external\n", encoding="utf-8")
    marker = project / "go.mod"
    marker.symlink_to(external)

    findings = projector.check("projects", surface="skills", project_roots=(project,))

    assert [item.message for item in findings] == [
        f"project capability marker symlink forbidden: {marker}"
    ]
    assert marker.is_symlink()


def test_managed_tree_removal_refuses_nested_symlink(tmp_path: Path) -> None:
    managed = tmp_path / "managed"
    external = tmp_path / "external"
    managed.mkdir()
    external.write_text("preserve\n", encoding="utf-8")
    (managed / "escape").symlink_to(external)

    with pytest.raises(RuntimeError, match="refusing recursive removal of symlink"):
        Projector._remove_managed_tree(managed)

    assert external.read_text(encoding="utf-8") == "preserve\n"
    (managed / "escape").unlink()
