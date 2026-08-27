from __future__ import annotations

import json
from pathlib import Path

from agents_governance.catalog import Catalog
from agents_governance.normalize import (
    keyword_description,
    normalize,
    normalize_descriptions,
)


def test_normalize_preserves_body_in_required_reference(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "router"
    skill.mkdir(parents=True)
    original_body = "# Procedure\n\n[Read](guide.md)\n\n" + "step\n" * 20
    (skill / "guide.md").write_text("guide\n", encoding="utf-8")
    (skill / "SKILL.md").write_text(
        "---\nname: router\ndescription: Route.\n---\n" + original_body,
        encoding="utf-8",
    )
    config = {
        "budgets": {
            "router_tokens": 10,
            "frozen_tokens": 1200,
            "on_demand_tokens": 5000,
            "max_lines": 500,
            "universal_core_tokens": 2000,
        },
        "classification": [
            {"pattern": "router", "class": "router", "provenance": "agents-owned", "updates": "manual"}
        ],
        "default": {"class": "on_demand", "provenance": "adopted", "updates": "manual"},
    }
    (tmp_path / "config" / "skills.json").write_text(json.dumps(config), encoding="utf-8")

    changes = normalize(Catalog(tmp_path), apply=True)

    assert len(changes) == 1
    procedure = (skill / "references" / "procedure.md").read_text(encoding="utf-8")
    assert "[Read](../guide.md)" in procedure
    assert "step\n" * 20 in procedure
    router = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "references/procedure.md" in router
    assert original_body not in router


def test_keyword_description_is_short_and_deterministic() -> None:
    assert keyword_description(
        "operator-correction-learning",
        "Learn durably from an operator correction and update ADR documents.",
    ) == "operator, correction, learning, learn, durably, update, adr, documents"


def test_normalize_descriptions_preserves_body(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "review"
    skill.mkdir(parents=True)
    body = "# Review\n\nKeep this procedure unchanged.\n"
    (skill / "SKILL.md").write_text(
        "---\nname: review\ndescription: Use this skill for detailed code review and security.\n---\n" + body,
        encoding="utf-8",
    )
    (skill / "agents").mkdir()
    (skill / "agents" / "openai.yaml").write_text(
        "name: review\ndescription: Use this skill when reviewing code for security.\n",
        encoding="utf-8",
    )
    config = {
        "budgets": {"router_tokens": 500, "frozen_tokens": 1200, "on_demand_tokens": 5000, "max_lines": 500},
        "classification": [],
        "default": {"class": "on_demand", "provenance": "adopted", "updates": "manual"},
    }
    (tmp_path / "config" / "skills.json").write_text(json.dumps(config), encoding="utf-8")

    changes = normalize_descriptions(Catalog(tmp_path), apply=True)

    assert len(changes) == 2
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "description: review, detailed, security" in text
    assert text.endswith(body)
    openai = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "description: review, reviewing, security" in openai


def test_normalize_descriptions_skips_forbidden_provenance(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "vendor-frozen-review"
    (skill / "agents").mkdir(parents=True)
    original = "name: vendor-frozen-review\ndescription: Frozen prose remains byte-identical.\n"
    (skill / "SKILL.md").write_text(
        "---\nname: vendor-frozen-review\ndescription: frozen, review\n---\n# Frozen\n",
        encoding="utf-8",
    )
    (skill / "agents" / "openai.yaml").write_text(original, encoding="utf-8")
    config = {
        "budgets": {"router_tokens": 500, "frozen_tokens": 1200, "on_demand_tokens": 5000, "max_lines": 500},
        "classification": [
            {"pattern": "vendor-frozen-*", "class": "router", "provenance": "vendor", "updates": "forbidden"}
        ],
        "default": {"class": "on_demand", "provenance": "adopted", "updates": "manual"},
    }
    (tmp_path / "config" / "skills.json").write_text(json.dumps(config), encoding="utf-8")

    assert normalize_descriptions(Catalog(tmp_path), apply=True) == []
    assert (skill / "agents" / "openai.yaml").read_text(encoding="utf-8") == original


def test_normalize_skips_forbidden_provenance(tmp_path: Path) -> None:
    skill = tmp_path / "skills" / "vendor-frozen"
    skill.mkdir(parents=True)
    original = "---\nname: vendor-frozen\ndescription: vendor, frozen\n---\n# Frozen\n\n" + ("word " * 100)
    (skill / "SKILL.md").write_text(original, encoding="utf-8")
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "skills.json").write_text(
        __import__("json").dumps({
            "budgets": {"router_tokens": 10, "frozen_tokens": 1200, "on_demand_tokens": 5000, "max_lines": 500},
            "classification": [{"pattern": "vendor-*", "class": "router", "provenance": "vendor", "updates": "forbidden"}],
            "project_generic": [], "private_patterns": [], "technologies": {},
            "default": {"class": "on_demand", "provenance": "adopted", "updates": "manual"},
        }),
        encoding="utf-8",
    )

    assert normalize(Catalog(tmp_path), apply=True) == []
    assert (skill / "SKILL.md").read_text(encoding="utf-8") == original
