from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agents_governance.catalog import Catalog
from agents_governance.skill_metadata import validate
from agents_governance.validation import validate as validate_catalog


def _write_metadata(root: Path, skill_name: str, text: str) -> Path:
    skill = root / "skills" / "agent-wide" / skill_name
    skill.mkdir(parents=True, exist_ok=True)
    skill_file = skill / "SKILL.md"
    if not skill_file.exists():
        skill_file.write_text(
            f"---\nname: {skill_name}\ndescription: example, metadata\n"
            "metadata:\n"
            '  version: "1.0.0"\n'
            "  aihub.tags: "
            '\'["provenance:agents-owned","updates:manual",'
            '"usage:on-demand"]\'\n'
            "---\n",
            encoding="utf-8",
        )
    path = skill / "agents" / "openai.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return path


def _codes(root: Path) -> list[str]:
    return [finding.code for finding in validate(root)]


def test_openai_metadata_is_optional(tmp_path: Path) -> None:
    (tmp_path / "skills" / "agent-wide" / "example").mkdir(parents=True)

    assert validate(tmp_path) == ()


def test_complete_documented_schema_is_accepted(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "example"
    assets = skill / "assets"
    assets.mkdir(parents=True)
    (assets / "small.svg").write_text("<svg/>", encoding="utf-8")
    (assets / "large.svg").write_text("<svg/>", encoding="utf-8")
    _write_metadata(
        tmp_path,
        "example",
        """interface:
  display_name: "Example Skill"
  short_description: "Example workflow for metadata validation"
  icon_small: "./assets/small.svg"
  icon_large: "./assets/large.svg"
  brand_color: "#3B82F6"
  default_prompt: "Use $example to validate skill metadata."
dependencies:
  tools:
    - type: "mcp"
      value: "github"
      description: "GitHub MCP server"
      transport: "streamable_http"
      url: "https://example.invalid/mcp/"
policy:
  allow_implicit_invocation: false
""",
    )

    assert validate(tmp_path) == ()


@pytest.mark.parametrize("legacy", ["model", "name", "description", "tools"])
def test_legacy_top_level_fields_are_rejected(tmp_path: Path, legacy: str) -> None:
    _write_metadata(tmp_path, "example", f'{legacy}: "legacy"\n')

    assert _codes(tmp_path) == ["legacy-field"]


@pytest.mark.parametrize(
    ("document", "expected_code"),
    [
        ("- interface\n", "document-type"),
        ('unknown: "value"\n', "unknown-field"),
        ('interface: "invalid"\n', "section-type"),
        ("interface:\n  display_name: 7\n", "field-type"),
        ('interface:\n  display_name: ""\n', "field-empty"),
        (
            'interface:\n  short_description: "too short"\n',
            "short-description-length",
        ),
        ('interface:\n  brand_color: "blue"\n', "brand-color"),
        (
            'interface:\n  default_prompt: "Use another skill."\n',
            "default-prompt-skill",
        ),
        ('interface:\n  extra: "value"\n', "unknown-field"),
        ("dependencies: []\n", "section-type"),
        ('dependencies:\n  tools: "github"\n', "field-type"),
        ("dependencies:\n  extra: []\n", "unknown-field"),
        ('dependencies:\n  tools:\n    - "github"\n', "field-type"),
        (
            'dependencies:\n  tools:\n    - type: "filesystem"\n      value: "files"\n',
            "dependency-type",
        ),
        ('dependencies:\n  tools:\n    - type: "mcp"\n', "missing-field"),
        (
            'dependencies:\n  tools:\n    - type: "mcp"\n      value: 3\n',
            "field-type",
        ),
        (
            'dependencies:\n  tools:\n    - type: "mcp"\n      value: "github"\n      extra: "value"\n',
            "unknown-field",
        ),
        ("policy: []\n", "section-type"),
        ("policy:\n  allow_implicit_invocation: 1\n", "field-type"),
        ("policy:\n  extra: true\n", "unknown-field"),
    ],
)
def test_invalid_shapes_and_values_fail_closed(
    tmp_path: Path, document: str, expected_code: str
) -> None:
    _write_metadata(tmp_path, "example", document)

    assert _codes(tmp_path) == [expected_code]


@pytest.mark.parametrize(
    "field",
    ["display_name", "short_description", "default_prompt"],
)
def test_interface_strings_must_be_quoted(tmp_path: Path, field: str) -> None:
    value = {
        "display_name": "Example Skill",
        "short_description": "Example metadata description for users",
        "default_prompt": "Use $example to validate metadata",
    }[field]
    _write_metadata(tmp_path, "example", f"interface:\n  {field}: {value}\n")

    assert _codes(tmp_path) == ["unquoted-string"]


def test_mapping_keys_must_be_unquoted(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "example", '"interface": {}\n')

    assert _codes(tmp_path) == ["quoted-key"]


def test_duplicate_keys_are_rejected(tmp_path: Path) -> None:
    _write_metadata(
        tmp_path,
        "example",
        'interface:\n  display_name: "First"\n  display_name: "Second"\n',
    )

    assert _codes(tmp_path) == ["duplicate-key"]


def test_invalid_yaml_is_reported_without_traceback(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "example", "interface: [\n")

    assert _codes(tmp_path) == ["yaml-invalid"]


@pytest.mark.parametrize("icon", ["/absolute/icon.svg", "../icon.svg"])
def test_icon_paths_must_be_contained_assets(icon: str, tmp_path: Path) -> None:
    _write_metadata(
        tmp_path,
        "example",
        f'interface:\n  icon_small: "{icon}"\n',
    )

    assert _codes(tmp_path) == ["icon-path"]


def test_icon_must_resolve_to_a_regular_local_asset(tmp_path: Path) -> None:
    _write_metadata(
        tmp_path,
        "example",
        'interface:\n  icon_small: "./assets/missing.svg"\n',
    )

    assert _codes(tmp_path) == ["icon-missing"]


def test_symlink_metadata_is_rejected_without_reading_target(tmp_path: Path) -> None:
    target = tmp_path / "target.yaml"
    target.write_text("{}\n", encoding="utf-8")
    path = tmp_path / "skills" / "agent-wide" / "example" / "agents" / "openai.yaml"
    path.parent.mkdir(parents=True)
    (path.parents[1] / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, metadata\n---\n",
        encoding="utf-8",
    )
    path.symlink_to(target)

    assert _codes(tmp_path) == ["metadata-symlink"]


def test_special_metadata_file_is_rejected_without_reading_it(tmp_path: Path) -> None:
    path = tmp_path / "skills" / "agent-wide" / "example" / "agents" / "openai.yaml"
    path.parent.mkdir(parents=True)
    (path.parents[1] / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, metadata\n---\n",
        encoding="utf-8",
    )
    os.mkfifo(path)

    assert _codes(tmp_path) == ["metadata-special"]


def test_findings_are_deterministic_by_path(tmp_path: Path) -> None:
    _write_metadata(tmp_path, "zeta", 'unknown: "value"\n')
    _write_metadata(tmp_path, "alpha", 'model: "legacy"\n')

    findings = validate(tmp_path)

    assert [(item.path, item.code) for item in findings] == [
        ("skills/agent-wide/alpha/agents/openai.yaml", "legacy-field"),
        ("skills/agent-wide/zeta/agents/openai.yaml", "unknown-field"),
    ]


def test_repository_skill_metadata_conforms_to_canonical_schema() -> None:
    root = Path(__file__).resolve().parents[1]

    assert validate(root) == ()
    assert "source-command-" not in "".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "skills").glob("*/*/agents/openai.yaml"))
    )


def test_canonical_catalog_validation_includes_metadata_gate(tmp_path: Path) -> None:
    (tmp_path / "commands").mkdir()
    skill = tmp_path / "skills" / "agent-wide" / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: example\ndescription: example, metadata\n"
        "metadata:\n"
        '  version: "1.0.0"\n'
        "  aihub.tags: "
        '\'["provenance:agents-owned","updates:manual",'
        '"usage:on-demand"]\'\n'
        "---\n# Example\n",
        encoding="utf-8",
    )
    _write_metadata(tmp_path, "example", 'model: "legacy"\n')
    config = {
        "version": 2,
        "budgets": {
            "router_tokens": 500,
            "frozen_tokens": 1200,
            "on_demand_tokens": 5000,
            "max_lines": 500,
        },
    }
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(config), encoding="utf-8"
    )

    findings = validate_catalog(Catalog(tmp_path))

    assert any(
        finding.path == "skills/agent-wide/example/agents/openai.yaml"
        and finding.code == "legacy-field"
        for finding in findings
    )
