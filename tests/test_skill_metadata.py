from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from agents_governance.skill_metadata import validate


def _skill(root: Path, name: str = "example") -> Path:
    directory = root / "skills" / "agent-wide" / name
    directory.mkdir(parents=True)
    (directory / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: example, metadata, validation\n---\n",
        encoding="utf-8",
    )
    return directory


def _metadata(skill: Path, text: str) -> Path:
    path = skill / "agents" / "openai.yaml"
    path.parent.mkdir()
    path.write_text(text, encoding="utf-8")
    return path


def test_metadata_is_optional(tmp_path: Path) -> None:
    _skill(tmp_path)

    assert validate(tmp_path) == ()


def test_complete_documented_schema_is_loaded(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    assets = skill / "assets"
    assets.mkdir()
    (assets / "small.svg").write_text("<svg/>", encoding="utf-8")
    (assets / "large.svg").write_text("<svg/>", encoding="utf-8")
    path = _metadata(
        skill,
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

    documents = validate(tmp_path)

    assert len(documents) == 1
    assert documents[0].path == path
    assert documents[0].interface is not None
    assert documents[0].interface.display_name == "Example Skill"
    assert [(tool.kind, tool.value) for tool in documents[0].tools] == [
        ("mcp", "github")
    ]
    assert documents[0].allow_implicit_invocation is False


@pytest.mark.parametrize(
    ("document", "message"),
    [
        ('model: "legacy"\n', "legacy field"),
        ('unknown: "value"\n', "not documented"),
        ('interface: "invalid"\n', "must be a mapping"),
        ("interface:\n  display_name: 7\n", "must be a string"),
        ('interface:\n  display_name: ""\n', "must not be empty"),
        ('interface:\n  short_description: "too short"\n', "25-64"),
        ('interface:\n  brand_color: "blue"\n', "hexadecimal"),
        ('interface:\n  default_prompt: "Use another skill."\n', "mention \\$example"),
        ('dependencies:\n  tools: "github"\n', "must be a list"),
        (
            'dependencies:\n  tools:\n    - type: "filesystem"\n      value: "files"\n',
            "documented mcp value",
        ),
        ("policy:\n  allow_implicit_invocation: 1\n", "must be a boolean"),
    ],
)
def test_invalid_metadata_raises_first_defect(
    tmp_path: Path, document: str, message: str
) -> None:
    _metadata(_skill(tmp_path), document)

    with pytest.raises((TypeError, ValueError), match=message):
        validate(tmp_path)


def test_yaml_errors_propagate_without_normalization(tmp_path: Path) -> None:
    _metadata(_skill(tmp_path), "interface: [\n")

    with pytest.raises(yaml.YAMLError):
        validate(tmp_path)


def test_quoted_keys_unquoted_strings_and_duplicates_raise(tmp_path: Path) -> None:
    path = _metadata(_skill(tmp_path), '"interface": {}\n')
    with pytest.raises(ValueError, match="key must be unquoted"):
        validate(tmp_path)

    path.write_text("interface:\n  display_name: Example Skill\n", encoding="utf-8")
    with pytest.raises(ValueError, match="string must be quoted"):
        validate(tmp_path)

    path.write_text(
        'interface:\n  display_name: "First"\n  display_name: "Second"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicated"):
        validate(tmp_path)


@pytest.mark.parametrize("icon", ["/absolute/icon.svg", "../icon.svg"])
def test_icon_paths_are_confined(tmp_path: Path, icon: str) -> None:
    _metadata(_skill(tmp_path), f'interface:\n  icon_small: "{icon}"\n')

    with pytest.raises(ValueError, match="contained"):
        validate(tmp_path)


def test_missing_icon_propagates_filesystem_error(tmp_path: Path) -> None:
    _metadata(
        _skill(tmp_path),
        'interface:\n  icon_small: "./assets/missing.svg"\n',
    )

    with pytest.raises(FileNotFoundError):
        validate(tmp_path)


def test_symlink_and_special_metadata_are_rejected(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    target = tmp_path / "target.yaml"
    target.write_text("{}\n", encoding="utf-8")
    path = skill / "agents" / "openai.yaml"
    path.parent.mkdir()
    path.symlink_to(target)
    with pytest.raises(ValueError, match="physical"):
        validate(tmp_path)

    path.unlink()
    os.mkfifo(path)
    with pytest.raises(ValueError, match="regular file"):
        validate(tmp_path)


def test_canonical_metadata_inventory_is_strict() -> None:
    root = Path(__file__).resolve().parents[1]
    expected = tuple(sorted(root.glob("skills/**/agents/openai.yaml")))

    assert tuple(document.path for document in validate(root)) == expected
