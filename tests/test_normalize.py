from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents_governance.catalog import Catalog
from agents_governance.normalize import normalize, normalize_descriptions

_ROUTER_METADATA = (
    "metadata:\n"
    "  aihub.tags: "
    '\'["provenance:agents-owned","updates:manual","usage:router"]\'\n'
)
_ON_DEMAND_METADATA = (
    "metadata:\n"
    "  aihub.tags: "
    '\'["provenance:agents-owned","updates:manual","usage:on-demand"]\'\n'
)
_FROZEN_METADATA = (
    "metadata:\n"
    "  aihub.tags: "
    '\'["provenance:vendor","updates:forbidden","usage:frozen"]\'\n'
)


def test_normalize_preserves_body_in_required_reference(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "agent-wide" / "router"
    skill.mkdir(parents=True)
    original_body = "# Procedure\n\n[Read](guide.md)\n\n" + "step\n" * 20
    (skill / "guide.md").write_text("guide\n", encoding="utf-8")
    (skill / "SKILL.md").write_text(
        "---\nname: router\ndescription: routing, procedure, skill\n"
        + _ROUTER_METADATA
        + "---\n"
        + original_body,
        encoding="utf-8",
    )
    config = {
        "version": 2,
        "budgets": {
            "router_tokens": 10,
            "frozen_tokens": 1200,
            "on_demand_tokens": 5000,
            "max_lines": 500,
        },
    }
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(config), encoding="utf-8"
    )

    changes = normalize(Catalog(tmp_path), apply=True)

    assert len(changes) == 1
    procedure = (skill / "references" / "procedure.md").read_text(encoding="utf-8")
    assert "[Read](../guide.md)" in procedure
    assert "step\n" * 20 in procedure
    router = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "references/procedure.md" in router
    assert original_body not in router


def test_normalize_rolls_back_new_procedure_when_router_promotion_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "agent-wide" / "router"
    skill.mkdir(parents=True)
    skill_file = skill / "SKILL.md"
    original = (
        "---\nname: router\ndescription: routing, procedure, skill\n"
        + _ROUTER_METADATA
        + "---\n# Procedure\n\n"
        + "step\n" * 20
    )
    skill_file.write_text(original, encoding="utf-8")
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(
            {
                "version": 2,
                "budgets": {
                    "router_tokens": 10,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
            }
        ),
        encoding="utf-8",
    )
    original_replace = Path.replace

    def fail_router_promotion(source: Path, target: Path) -> Path:
        if target == skill_file:
            raise OSError("injected router promotion failure")
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", fail_router_promotion)

    with pytest.raises(OSError, match="injected router promotion failure"):
        normalize(Catalog(tmp_path), apply=True)

    assert skill_file.read_text(encoding="utf-8") == original
    assert not (skill / "references" / "procedure.md").exists()


def test_normalize_descriptions_reports_without_inventing_keywords(
    tmp_path: Path,
) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "agent-wide" / "review"
    skill.mkdir(parents=True)
    body = "# Review\n\nKeep this procedure unchanged.\n"
    (skill / "SKILL.md").write_text(
        "---\nname: review\n"
        "description: Use this skill for detailed code review and security.\n"
        + _ON_DEMAND_METADATA
        + "---\n"
        + body,
        encoding="utf-8",
    )
    (skill / "agents").mkdir()
    openai = skill / "agents" / "openai.yaml"
    openai_original = (
        "name: review\ndescription: Use this skill when reviewing code for security.\n"
    )
    openai.write_text(openai_original, encoding="utf-8")
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

    catalog = Catalog(tmp_path)
    changes = normalize_descriptions(catalog, apply=False)

    assert len(changes) == 1
    with pytest.raises(ValueError, match="authored discriminating keyword list"):
        normalize_descriptions(catalog, apply=True)
    assert (skill / "SKILL.md").read_text(encoding="utf-8").endswith(body)
    assert openai.read_text(encoding="utf-8") == openai_original


def test_normalize_descriptions_accepts_discriminating_keywords(
    tmp_path: Path,
) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "agent-wide" / "review"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: review\n"
        "description: security boundaries, code review, risk analysis\n"
        + _ON_DEMAND_METADATA
        + "---\n# Review\n",
        encoding="utf-8",
    )
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(
            {
                "version": 2,
                "budgets": {
                    "router_tokens": 500,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
            }
        ),
        encoding="utf-8",
    )

    assert normalize_descriptions(Catalog(tmp_path), apply=True) == []


def test_normalize_descriptions_skips_forbidden_provenance(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "agent-wide" / "vendor-frozen-review"
    (skill / "agents").mkdir(parents=True)
    original = "name: vendor-frozen-review\ndescription: Frozen prose remains byte-identical.\n"
    (skill / "SKILL.md").write_text(
        "---\nname: vendor-frozen-review\ndescription: frozen, vendor, review\n"
        + _FROZEN_METADATA
        + "---\n# Frozen\n",
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text(original, encoding="utf-8")
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

    assert normalize_descriptions(Catalog(tmp_path), apply=True) == []
    assert (skill / "agents" / "openai.yaml").read_text(encoding="utf-8") == original


def test_normalize_skips_forbidden_provenance(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "vendor-frozen"
    skill.mkdir(parents=True)
    original = (
        "---\nname: vendor-frozen\ndescription: vendor, frozen, router\n"
        + _FROZEN_METADATA
        + "---\n# Frozen\n\n"
        + ("word " * 100)
    )
    (skill / "SKILL.md").write_text(original, encoding="utf-8")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "skills.json").write_text(
        __import__("json").dumps(
            {
                "version": 2,
                "budgets": {
                    "router_tokens": 10,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
            }
        ),
        encoding="utf-8",
    )

    assert normalize(Catalog(tmp_path), apply=True) == []
    assert (skill / "SKILL.md").read_text(encoding="utf-8") == original


def test_normalize_rejects_invalid_catalog_before_any_write(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "agent-wide" / "invalid"
    skill.mkdir(parents=True)
    original = "---\nname: invalid\ndescription: invalid, catalog, example\n---\n" + (
        "step\n" * 20
    )
    skill_file = skill / "SKILL.md"
    skill_file.write_text(original, encoding="utf-8")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(
            {
                "version": 2,
                "budgets": {
                    "router_tokens": 10,
                    "frozen_tokens": 1200,
                    "on_demand_tokens": 5000,
                    "max_lines": 500,
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="tag-metadata"):
        normalize(Catalog(tmp_path), apply=True)

    assert skill_file.read_text(encoding="utf-8") == original
    assert not (skill / "references").exists()
