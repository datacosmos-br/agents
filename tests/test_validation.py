from __future__ import annotations

import json
from pathlib import Path

from agents_governance.catalog import Catalog
from agents_governance.validation import validate


def _catalog(tmp_path: Path) -> Catalog:
    (tmp_path / "config").mkdir()
    config = {
        "budgets": {
            "router_tokens": 500,
            "frozen_tokens": 1200,
            "on_demand_tokens": 5000,
            "max_lines": 500,
            "universal_core_tokens": 2000,
        },
        "classification": [],
        "default": {"class": "on_demand", "provenance": "adopted", "updates": "manual"},
    }
    (tmp_path / "config" / "skills.json").write_text(json.dumps(config), encoding="utf-8")
    return Catalog(tmp_path)


def test_missing_reference_fails_closed(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, reference\n---\n[missing](references/no.md)\n",
        encoding="utf-8",
    )

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.message) for item in findings] == [
        ("reference", "unsafe or missing: references/no.md")
    ]


def test_directory_name_must_match_frontmatter(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: wrong\ndescription: example, validation\n---\n# Example\n",
        encoding="utf-8",
    )

    findings = validate(_catalog(tmp_path))

    assert findings[0].code == "name-directory"


def test_links_inside_fenced_examples_are_not_dependencies(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, fenced, reference\n---\n"
        "```markdown\n[Generated](missing.md)\n```\n",
        encoding="utf-8",
    )

    assert not validate(_catalog(tmp_path))


def test_description_allows_technology_identifiers(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: next.js, go.mod, c++, bak/.bkp\n---\n# Example\n",
        encoding="utf-8",
    )

    assert not validate(_catalog(tmp_path))


def test_description_rejects_prose(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: Use this skill for code review.\n---\n# Example\n",
        encoding="utf-8",
    )

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.message) for item in findings] == [
        ("description", "description must be a comma-separated keyword list")
    ]
