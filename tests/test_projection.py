from __future__ import annotations

import json
import subprocess
from pathlib import Path

from agents_governance.catalog import Catalog
from agents_governance.projection import Projector


def _projector(tmp_path: Path, target: Path) -> Projector:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example.\n---\n# Example\n",
        encoding="utf-8",
    )
    skills_config = {
        "budgets": {
            "router_tokens": 500,
            "frozen_tokens": 1200,
            "on_demand_tokens": 5000,
            "max_lines": 500,
            "universal_core_tokens": 2000,
        },
        "classification": [],
        "project_generic": [],
        "private_patterns": [],
        "technologies": {},
        "default": {"class": "on_demand", "provenance": "adopted", "updates": "manual"},
    }
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(skills_config), encoding="utf-8"
    )
    projections = {
        "version": 2,
        "surfaces": {"commands": {"entries": []}, "rules": {"entries": []}},
        "personal_targets": {"test": {"skills": str(target)}},
        "projects": {
            "town_root": str(tmp_path / "town"),
            "checkout_glob": "*/mayor/rig",
            "skills_path": ".agents/skills",
            "flext_remote": "flext-sh/flext",
        },
    }
    (tmp_path / "config" / "projections.json").write_text(
        json.dumps(projections), encoding="utf-8"
    )
    return Projector(Catalog(tmp_path))


def test_apply_is_idempotent(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)

    assert projector.apply("personal") == []
    first = (target / Projector.MANIFEST).read_bytes()
    assert projector.apply("personal") == []

    assert not (target / "example").is_symlink()
    assert (target / "example" / "SKILL.md").read_bytes() == (
        tmp_path / "skills" / "example" / "SKILL.md"
    ).read_bytes()
    assert (target / Projector.MANIFEST).read_bytes() == first
    assert projector.check("personal") == []


def test_commands_and_rules_are_independently_projected(tmp_path: Path) -> None:
    target = tmp_path / "skills-target"
    projector = _projector(tmp_path, target)
    commands_target = tmp_path / "commands-target"
    rules_target = tmp_path / "rules-target"
    projector.config["personal_targets"]["test"].update(
        {
            "commands": str(commands_target),
            "rules": str(rules_target),
        }
    )
    projector.config["surfaces"] = {
        "commands": {"entries": ["review.md"]},
        "rules": {"entries": ["security"]},
    }
    (tmp_path / "commands").mkdir()
    (tmp_path / "commands" / "review.md").write_text("# Review\n", encoding="utf-8")
    rule = tmp_path / "rules" / "security"
    rule.mkdir(parents=True)
    (rule / "closure.md").write_text("# Closure\n", encoding="utf-8")

    assert projector.apply("personal", surface="commands") == []
    assert projector.apply("personal", surface="rules") == []
    assert (commands_target / "review.md").read_text(encoding="utf-8") == "# Review\n"
    assert (rules_target / "security" / "closure.md").read_text(
        encoding="utf-8"
    ) == "# Closure\n"
    assert projector.check("personal", surface="commands") == []
    assert projector.check("personal", surface="rules") == []


def test_foreign_collision_is_archived_before_explicit_apply(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    foreign = target / "example"
    foreign.mkdir(parents=True)
    marker = foreign / "foreign.txt"
    marker.write_text("preserve", encoding="utf-8")

    findings = projector.apply("personal")

    assert findings == []
    assert (foreign / "SKILL.md").is_file()
    archived = list((target / ".agents-archive").glob("example.*.bak/foreign.txt"))
    assert len(archived) == 1
    assert archived[0].read_text(encoding="utf-8") == "preserve"


def test_modified_stale_managed_entry_is_archived(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    assert projector.apply("personal") == []
    stale = target / "example"
    (stale / "operator.txt").write_text("preserve", encoding="utf-8")
    projector.catalog.config["classification"] = [
        {
            "pattern": "example",
            "class": "router",
            "provenance": "retired",
            "updates": "forbidden",
        }
    ]

    assert projector.apply("personal") == []
    assert not stale.exists()
    archived = list((target / ".agents-archive").glob("example.*.bak/operator.txt"))
    assert len(archived) == 1
    assert archived[0].read_text(encoding="utf-8") == "preserve"


def test_legacy_destination_symlink_is_removed_and_replaced_with_copy(
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

    assert findings == []
    assert destination.is_dir()
    assert not destination.is_symlink()
    assert (destination / "SKILL.md").is_file()


def test_technology_skill_is_not_personal(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    projector.catalog.config["technologies"] = {
        "python": {"markers": ["pyproject.toml"], "skills": ["example"]}
    }

    assert projector.apply("personal") == []
    assert not (target / "example").exists()


def test_structured_markers_detect_technologies(tmp_path: Path) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    projector.catalog.config["technologies"] = {
        "go": {"markers": ["go.mod"], "skills": []},
        "rust": {"markers": ["Cargo.toml"], "skills": []},
    }
    project = tmp_path / "project"
    project.mkdir()
    (project / "go.mod").write_text("module example\n", encoding="utf-8")

    assert projector.detected_technologies(project) == ("go",)


def test_flext_source_overrides_same_named_generic_skill(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "target"
    projector = _projector(tmp_path, target)
    projector.catalog.config["project_generic"] = ["example"]
    project = tmp_path / "project"
    project.mkdir()
    flext_skill = tmp_path / "flext" / "example"
    flext_skill.mkdir(parents=True)
    (flext_skill / "SKILL.md").write_text("flext owner\n", encoding="utf-8")
    monkeypatch.setattr(projector, "is_flext_project", lambda _root: True)
    monkeypatch.setattr(
        projector, "_flext_sources", lambda: (projector._source(flext_skill, "flext"),)
    )

    sources = projector.project_sources(project)

    assert sources[0].origin == "flext"
    assert sources[0].directory == flext_skill.resolve()


def test_linux_copy_requests_reflink(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
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


def test_unknown_project_target_fails_closed(tmp_path: Path) -> None:
    projector = _projector(tmp_path, tmp_path / "target")

    findings = projector.check("projects", "typo-does-not-exist")

    assert [(item.target, item.message) for item in findings] == [
        ("typo-does-not-exist", "unknown project projection target")
    ]
