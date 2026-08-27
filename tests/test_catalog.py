from __future__ import annotations

import json
from pathlib import Path

from agents_governance.catalog import Catalog


def test_inventory_is_deterministic_and_owned(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "skills" / "example").mkdir(parents=True)
    (tmp_path / "skills" / "example" / "SKILL.md").write_text(
        "---\nname: example\ndescription: Example.\n---\n# Example\n",
        encoding="utf-8",
    )
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
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(config), encoding="utf-8"
    )

    first = Catalog(tmp_path).inventory()
    second = Catalog(tmp_path).inventory()

    assert first == second
    assert first[0]["owner"] == "agents"
    assert len(first[0]["digest"]) == 64


def test_forbidden_third_party_skill_is_not_distributed(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    skill = tmp_path / "skills" / "vendor-frozen-plan"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: vendor-frozen-plan\ndescription: vendor, frozen, plan\n---\n",
        encoding="utf-8",
    )
    config = {
        "budgets": {
            "router_tokens": 500,
            "frozen_tokens": 1200,
            "on_demand_tokens": 5000,
            "max_lines": 500,
        },
        "classification": [
            {
                "pattern": "vendor-frozen-*",
                "class": "router",
                "provenance": "vendor",
                "updates": "forbidden",
            }
        ],
        "technologies": {},
        "default": {"class": "on_demand", "provenance": "adopted", "updates": "manual"},
    }
    (tmp_path / "config" / "skills.json").write_text(
        json.dumps(config), encoding="utf-8"
    )

    catalog = Catalog(tmp_path)

    assert catalog.policy("vendor-frozen-plan").distributions == ()
    assert "vendor-frozen-plan" not in catalog.names_for("personal")
