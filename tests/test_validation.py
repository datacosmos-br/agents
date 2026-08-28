from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

import agents_governance.validation as validation_module
from agents_governance.catalog import Catalog
from agents_governance.validation import validate


def _catalog(tmp_path: Path) -> Catalog:
    (tmp_path / "config").mkdir(exist_ok=True)
    (tmp_path / "commands").mkdir(exist_ok=True)
    rules = tmp_path / "rules"
    rules.mkdir(exist_ok=True)
    baseline = rules / "baseline.md"
    if not baseline.exists():
        baseline.write_text(
            "# Baseline\n\nUse the canonical owner.\n", encoding="utf-8"
        )
    config = {
        "version": 2,
        "budgets": {
            "router_tokens": 500,
            "frozen_tokens": 1200,
            "on_demand_tokens": 5000,
            "max_lines": 500,
        },
    }
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(config), encoding="utf-8"
    )
    for skill_file in (tmp_path / "skills").glob("*/*/SKILL.md"):
        text = skill_file.read_text(encoding="utf-8")
        if "\nmetadata:\n" in text:
            continue
        marker = text.find("\n---\n", 4)
        if marker >= 0:
            tags = (
                "metadata:\n"
                '  version: "1.0.0"\n'
                "  aihub.tags: "
                '\'["provenance:agents-owned","updates:manual",'
                '"usage:on-demand"]\''
            )
            skill_file.write_text(
                f"{text[:marker]}\n{tags}{text[marker:]}", encoding="utf-8"
            )
    return Catalog(tmp_path)


def test_rule_contract_findings_are_part_of_global_validation(tmp_path: Path) -> None:
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "Invalid.md").write_text("# Invalid path\n", encoding="utf-8")

    findings = validate(_catalog(tmp_path))

    assert any(
        finding.path == "rules/Invalid.md" and finding.code == "rule-path"
        for finding in findings
    )


def _write_semantic_eval(tmp_path: Path, *, name: str = "example") -> Path:
    directory = tmp_path / "evals" / name
    tasks = directory / "tasks"
    fixtures = directory / "fixtures"
    tasks.mkdir(parents=True)
    fixtures.mkdir()
    (fixtures / "request.txt").write_text(
        "Validate account records against the declared schema.\n", encoding="utf-8"
    )
    (directory / "eval.yaml").write_text(
        yaml.safe_dump(
            {
                "name": f"{name}-eval",
                "skill": name,
                "schemaVersion": "1.0",
                "config": {
                    "timeout_seconds": 300,
                    "required_skills": [name],
                    "skill_directories": [f"../../skills/agent-wide/{name}"],
                },
                "graders": [
                    {
                        "type": "prompt",
                        "name": f"{name}_material_result",
                        "config": {
                            "prompt": (
                                f"Grade {name} against the requested schema report, "
                                "including its record count and rejected record reasons."
                            )
                        },
                    },
                    {
                        "type": "behavior",
                        "name": "bounded_execution",
                        "config": {"max_duration_ms": 240000},
                    },
                ],
                "tasks": ["tasks/*.yaml"],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    task_payloads = {
        "basic-usage.yaml": {
            "id": f"{name}-happy-001",
            "name": "Happy Path",
            "tags": ["happy-path"],
            "inputs": {
                "prompt": (
                    "Validate the supplied account records and report both the accepted "
                    "record count and every rejected record reason."
                ),
                "files": [{"path": "request.txt"}],
            },
            "expected": {
                "outcomes": [{"type": "task_completed"}],
                "output_contains": ["accepted records", "rejected records"],
            },
        },
        "edge-case.yaml": {
            "id": f"{name}-fail-closed-001",
            "name": "Missing Schema",
            "tags": ["edge-case"],
            "inputs": {
                "prompt": (
                    "The record schema is absent. Identify that blocking input and do "
                    "not claim that validation ran."
                )
            },
            "expected": {
                "output_contains": ["schema is required"],
                "output_not_contains": ["validation passed"],
            },
        },
        "should-not-trigger.yaml": {
            "id": f"{name}-negative-001",
            "name": "Unrelated Writing Request",
            "tags": ["anti-trigger", "negative-test"],
            "inputs": {"prompt": "Rewrite this sales headline in a friendlier tone."},
            "expected": {
                "output_not_contains": ["accepted records", "schema validation"]
            },
        },
    }
    for filename, payload in task_payloads.items():
        (tasks / filename).write_text(
            yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
        )
    return directory


def test_missing_reference_fails_closed(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: local references, skill bundles, validation\n---\n[missing](references/no.md)\n",
        encoding="utf-8",
    )

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.message) for item in findings] == [
        ("reference", "unsafe or missing: references/no.md")
    ]


def test_directory_name_must_match_frontmatter(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: wrong\ndescription: example behavior, skill contract, validation\n---\n# Example\n",
        encoding="utf-8",
    )

    findings = validate(_catalog(tmp_path))

    assert findings[0].code == "name-directory"


def test_links_inside_fenced_examples_are_not_dependencies(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: fenced examples, local references, validation\n---\n"
        "```markdown\n[Generated](missing.md)\n```\n",
        encoding="utf-8",
    )

    assert not validate(_catalog(tmp_path))


def test_description_accepts_discriminating_keyword_phrases(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\n"
        "description: c++, cmake, service development\n"
        "---\n# Example\n",
        encoding="utf-8",
    )

    assert not validate(_catalog(tmp_path))


def test_description_rejects_prose_instead_of_keyword_phrases(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\n"
        "description: code review when deployment changes, security, validation\n"
        "---\n# Example\n",
        encoding="utf-8",
    )

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.message) for item in findings] == [
        (
            "description",
            "description must contain keywords or nominal phrases, not prose",
        )
    ]


def test_description_enforces_discovery_budget(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    skill_file = skill / "SKILL.md"
    skill_file.write_text(
        "---\nname: example\ndescription: review, code\n---\n# Example\n",
        encoding="utf-8",
    )
    catalog = _catalog(tmp_path)

    findings = validate(catalog)

    assert [(item.code, item.message) for item in findings] == [
        ("description", "description must contain 3-10 unique terms")
    ]

    skill_file.write_text(
        "---\nname: example\ndescription: "
        + "architecture-validation-keyword-" * 4
        + "\n---\n# Example\n",
        encoding="utf-8",
    )

    findings = validate(catalog)

    assert [(item.code, item.message) for item in findings] == [
        ("description", "description must contain 12-96 characters")
    ]


def test_router_budget_uses_bpe_measurement_and_local_usage_tag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: example behavior, skill contract, validation\n"
        "metadata:\n"
        "  aihub.tags: "
        '\'["provenance:agents-owned","updates:manual","usage:router"]\'\n'
        "---\n# Example\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(validation_module, "bpe_tokens", lambda _path, _root: 501)

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.message) for item in findings] == [
        ("budget", "501 > 500 tokens")
    ]


def test_description_enforces_keyword_list_grammar(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    skill_file = skill / "SKILL.md"
    invalid_descriptions = {
        '" code review, security, validation "': (
            "description must be one trimmed line"
        ),
        "Code review, security, validation": ("description must use lowercase terms"),
        "code review, security, validation.": (
            "description terms may contain only lowercase words and technical identifiers"
        ),
        "code review,security, validation": (
            "description terms must be separated by ', '"
        ),
        "code review, code review, validation": ("description terms must be unique"),
    }
    for description, expected_message in invalid_descriptions.items():
        skill_file.write_text(
            f"---\nname: example\ndescription: {description}\n---\n# Example\n",
            encoding="utf-8",
        )

        findings = validate(_catalog(tmp_path))

        assert [(item.code, item.message) for item in findings] == [
            ("description", expected_message)
        ]


@pytest.mark.parametrize("distribution", ["project_generic", "technology"])
@pytest.mark.parametrize(
    "private_reference",
    [
        "~/.claude/skills",
        "/root/private/tool",
        "/Users/alice/private/tool",
        ".agents/skills",
        "Gas Town",
        "Gas City",
    ],
)
def test_all_project_distributions_reject_private_references(
    tmp_path: Path, distribution: str, private_reference: str
) -> None:
    category = "project-wide" if distribution == "project_generic" else "technology"
    skill = tmp_path / "skills" / category / "example"
    skill.mkdir(parents=True)
    metadata = ""
    if distribution == "technology":
        metadata = (
            "metadata:\n"
            "  aihub.tags: "
            '\'["activation:detected","detect:marker:pyproject.toml",'
            '"provenance:agents-owned","route:project",'
            '"technology:python","updates:manual",'
            '"usage:on-demand"]\'\n'
        )
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n"
        f"{metadata}"
        "---\n"
        f"Private owner reference: {private_reference}\n",
        encoding="utf-8",
    )
    catalog = _catalog(tmp_path)

    findings = validate(catalog)

    assert "non-generic" in {finding.code for finding in findings}


def test_project_distribution_accepts_lowercase_rest_user_route(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "project-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: rest routes, user resources, documentation\n---\n"
        "Document the resource routes `/api/v1/users/123` and `/api/v1/Users/123`.\n",
        encoding="utf-8",
    )
    catalog = _catalog(tmp_path)

    assert validate(catalog) == []


def test_generic_eval_scaffold_fails_closed(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    tasks = tmp_path / "evals" / "example" / "tasks"
    tasks.mkdir(parents=True)
    (tasks.parent / "eval.yaml").write_text(
        "config: {}\ngraders:\n- name: relevant_content\n",
        encoding="utf-8",
    )
    (tasks / "basic.yaml").write_text(
        "id: generic-001\ninputs:\n  prompt: Help me with this task\n"
        "expected:\n  output_contains: [function]\n",
        encoding="utf-8",
    )

    findings = validate(_catalog(tmp_path))

    assert {"eval-generic", "eval-skill"} <= {item.code for item in findings}


def test_function_in_realistic_prompt_is_not_a_generic_assertion(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    directory = _write_semantic_eval(tmp_path)
    basic = directory / "tasks" / "basic-usage.yaml"
    task = yaml.safe_load(basic.read_text(encoding="utf-8"))
    task["inputs"]["prompt"] = (
        "Explain this function and report accepted records and rejected records."
    )
    basic.write_text(yaml.safe_dump(task, sort_keys=False), encoding="utf-8")

    assert validate(_catalog(tmp_path)) == []


def test_semantic_eval_contract_is_accepted(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    _write_semantic_eval(tmp_path)

    assert validate(_catalog(tmp_path)) == []


def test_fail_closed_role_accepts_a_genuinely_empty_request(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    directory = _write_semantic_eval(tmp_path)
    edge = directory / "tasks" / "edge-case.yaml"
    task = yaml.safe_load(edge.read_text(encoding="utf-8"))
    task["inputs"]["prompt"] = ""
    edge.write_text(yaml.safe_dump(task, sort_keys=False), encoding="utf-8")

    assert validate(_catalog(tmp_path)) == []


def test_eval_requires_exact_roles_and_unique_ids(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    directory = _write_semantic_eval(tmp_path)
    unknown = directory / "tasks" / "extra.yaml"
    payload = yaml.safe_load(
        (directory / "tasks" / "edge-case.yaml").read_text(encoding="utf-8")
    )
    payload["id"] = "example-happy-001"
    unknown.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    findings = validate(_catalog(tmp_path))

    assert {"eval-roles", "eval-id"} <= {item.code for item in findings}


def test_eval_rejects_duplicate_and_weather_scaffold_prompts(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    directory = _write_semantic_eval(tmp_path)
    catalog = _catalog(tmp_path)
    basic = directory / "tasks" / "basic-usage.yaml"
    negative = directory / "tasks" / "should-not-trigger.yaml"
    basic_task = yaml.safe_load(basic.read_text(encoding="utf-8"))
    negative_task = yaml.safe_load(negative.read_text(encoding="utf-8"))
    negative_task["inputs"]["prompt"] = basic_task["inputs"]["prompt"]
    negative.write_text(
        yaml.safe_dump(negative_task, sort_keys=False), encoding="utf-8"
    )

    findings = validate(catalog)

    assert "eval-prompt-duplicate" in {item.code for item in findings}

    negative_task["inputs"]["prompt"] = "What is the weather today?"
    negative.write_text(
        yaml.safe_dump(negative_task, sort_keys=False), encoding="utf-8"
    )

    findings = validate(catalog)

    assert "eval-scaffold" in {item.code for item in findings}


def test_eval_fixtures_must_be_internal_regular_and_specific(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    directory = _write_semantic_eval(tmp_path)
    fixture = directory / "fixtures" / "request.txt"
    fixture.write_text(
        'def hello(name):\n    """Greet someone by name."""\n'
        '    return f"Hello, {name}!"\n',
        encoding="utf-8",
    )
    (directory / "fixtures" / "linked.txt").symlink_to(fixture)
    basic = directory / "tasks" / "basic-usage.yaml"
    task = yaml.safe_load(basic.read_text(encoding="utf-8"))
    task["inputs"]["files"] = [
        {"path": "request.txt"},
        {"path": "linked.txt"},
        {"path": "missing.txt"},
        {"path": "../outside.txt"},
    ]
    basic.write_text(yaml.safe_dump(task, sort_keys=False), encoding="utf-8")

    findings = validate(_catalog(tmp_path))
    codes = {item.code for item in findings}

    assert {"eval-fixture", "eval-fixture-symlink", "eval-fixture-generic"} <= codes


def test_eval_rejects_scaffolds_and_non_material_expectations(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    directory = _write_semantic_eval(tmp_path)
    basic = directory / "tasks" / "basic-usage.yaml"
    task = yaml.safe_load(basic.read_text(encoding="utf-8"))
    task["inputs"]["prompt"] = (
        "record validation, schema reports, material results "
        "Apply the example capability to the provided fixture. Exercise these "
        "requirements: return a concrete result."
    )
    task["expected"] = {"outcomes": [{"type": "task_completed"}]}
    basic.write_text(yaml.safe_dump(task, sort_keys=False), encoding="utf-8")
    negative = directory / "tasks" / "should-not-trigger.yaml"
    task = yaml.safe_load(negative.read_text(encoding="utf-8"))
    task["expected"] = {"output_not_contains": ["skill activated"]}
    negative.write_text(yaml.safe_dump(task, sort_keys=False), encoding="utf-8")

    findings = validate(_catalog(tmp_path))
    codes = {item.code for item in findings}

    assert {
        "eval-scaffold",
        "eval-description-copy",
        "eval-assertion",
        "eval-antitrigger",
    } <= codes


def test_eval_requires_skill_grader_and_shorter_duration(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    directory = _write_semantic_eval(tmp_path)
    config_path = directory / "eval.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["graders"][0]["name"] = "material_task_result"
    config["graders"][0]["config"]["prompt"] = "Grade material completion."
    config["graders"][1]["config"]["max_duration_ms"] = 300000
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    findings = validate(_catalog(tmp_path))

    assert {"eval-grader", "eval-duration"} <= {item.code for item in findings}


def test_orphan_skill_directory_fails_closed(tmp_path: Path) -> None:
    orphan = tmp_path / "skills" / "agent-wide" / "learned" / "agents"
    orphan.mkdir(parents=True)
    (orphan / "openai.yaml").write_text("name: learned\n", encoding="utf-8")

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.path) for item in findings] == [
        ("orphan-skill-directory", "skills/agent-wide/learned")
    ]


def test_eval_model_must_match_project_owner(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: record validation, schema reports, material results\n---\n# Example\n",
        encoding="utf-8",
    )
    (tmp_path / ".waza.yaml").write_text(
        "defaults:\n  model: owner-model\n", encoding="utf-8"
    )
    directory = _write_semantic_eval(tmp_path)
    config_path = directory / "eval.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["config"]["model"] = "other-model"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    findings = validate(_catalog(tmp_path))

    assert [(item.code, item.path) for item in findings] == [
        ("eval-model-drift", "evals/example/eval.yaml")
    ]
