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
        "personal": ["example"] if (tmp_path / "skills" / "example").is_dir() else [],
    }
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(config), encoding="utf-8"
    )
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


def test_generic_eval_scaffold_fails_closed(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, validation\n---\n# Example\n",
        encoding="utf-8",
    )
    tasks = tmp_path / "evals" / "example" / "tasks"
    tasks.mkdir(parents=True)
    (tasks.parent / "eval.yaml").write_text(
        "config: {}\ngraders:\n- name: relevant_content\n",
        encoding="utf-8",
    )
    (tasks / "basic.yaml").write_text(
        "inputs:\n  prompt: Help me with this task\nexpected:\n  output_contains: function\n",
        encoding="utf-8",
    )

    findings = validate(_catalog(tmp_path))

    assert {item.code for item in findings} == {"eval-generic", "eval-skill"}


def test_function_in_realistic_prompt_is_not_a_generic_assertion(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, validation\n---\n# Example\n",
        encoding="utf-8",
    )
    tasks = tmp_path / "evals" / "example" / "tasks"
    tasks.mkdir(parents=True)
    (tasks.parent / "eval.yaml").write_text(
        "config:\n"
        "  required_skills: [example]\n"
        "  skill_directories: [../../skills/example]\n"
        "graders:\n- type: prompt\n  name: material\n",
        encoding="utf-8",
    )
    (tasks / "basic.yaml").write_text(
        "inputs:\n  prompt: Explain this function.\n"
        "expected:\n  output_contains: [validation]\n",
        encoding="utf-8",
    )

    assert validate(_catalog(tmp_path)) == []


def test_orphan_skill_directory_fails_closed(tmp_path: Path) -> None:
    orphan = tmp_path / "skills" / "learned" / "agents"
    orphan.mkdir(parents=True)
    (orphan / "openai.yaml").write_text("name: learned\n", encoding="utf-8")

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.path) for item in findings] == [
        ("orphan-skill-directory", "skills/learned")
    ]


def test_eval_model_must_match_project_owner(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, validation\n---\n# Example\n",
        encoding="utf-8",
    )
    (tmp_path / ".waza.yaml").write_text(
        "defaults:\n  model: gpt-5.4\n", encoding="utf-8"
    )
    tasks = tmp_path / "evals" / "example" / "tasks"
    tasks.mkdir(parents=True)
    (tasks.parent / "eval.yaml").write_text(
        "config:\n  model: claude-sonnet-4.6\n"
        "  required_skills: [example]\n"
        "  skill_directories: [../../skills/example]\n"
        "graders: []\n",
        encoding="utf-8",
    )
    (tasks / "basic.yaml").write_text(
        "inputs:\n  prompt: Validate the example skill.\n", encoding="utf-8"
    )

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.path) for item in findings] == [
        ("eval-model-drift", "evals/example/eval.yaml")
    ]
