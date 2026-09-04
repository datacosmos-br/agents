from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import approved, seed_approval_docs

from agents_governance.agent_profiles import audit_agent_profiles
from agents_governance.catalog import Catalog
from agents_governance.commands import audit_command_specs
from agents_governance.rules import audit_rule_specs
from agents_governance.validation import (
    require_description,
    validate,
    validate_skill_catalogs,
)
from agents_governance.waza import require_model_projection


@pytest.mark.parametrize(
    "description",
    [
        "c++, cmake, service development",
        "agent behavior, session recovery, tool debugging",
        "rest api, resource naming, error semantics",
    ],
)
def test_description_contract_accepts_nominal_discovery_terms(
    description: str,
) -> None:
    assert require_description(description) == description


@pytest.mark.parametrize(
    ("description", "message"),
    [
        (None, "missing description"),
        (" review, security, validation", "trimmed line"),
        ("review, code", "3-10"),
        ("Code review, security, validation", "lowercase"),
        ("code review when deployed, security, validation", "nominal phrases"),
        ("code@review, security, validation", "technical identifiers"),
        ("review,security, validation", "separated"),
        ("code review, code review, validation", "unique"),
    ],
)
def test_description_contract_raises_first_defect(
    description: object, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        require_description(description)


def test_canonical_validation_executes_complete_offline_authority() -> None:
    root = Path(__file__).resolve().parents[1]

    catalog = Catalog(root)
    validate(
        catalog,
        require_model_projection(root),
        audit_command_specs(root, (record.name for record in catalog.records())),
        audit_agent_profiles(root),
        audit_rule_specs(root),
    )


_CATEGORIES = (
    "agent-wide",
    "domain",
    "framework",
    "project-wide",
    "technology",
    "tool",
)

_BUDGETS = {
    "router_tokens": 500,
    "frozen_tokens": 1200,
    "on_demand_tokens": 5000,
    "max_lines": 500,
}

_EVAL_YAML = """\
skill: gas-city-kit
config:
  trials_per_task: 1
  timeout_seconds: 300
  parallel: false
  max_attempts: 0
  fail_fast: true
  executor: copilot-sdk
  model: fixture-model
  skill_directories:
  - ../../skills/tool/gas-city-kit
  required_skills:
  - gas-city-kit
graders:
- type: prompt
  name: gas-city-kit-contract
  config:
    prompt: |-
      Grade the gas-city-kit response. Pass only when it declares the opt-in
      state, asks for explicit operator selection, and stops at a missing
      selection without inventing a city, a rig, or an alternate store.
- type: behavior
  name: bounded_execution
  config: {max_duration_ms: 240000}
tasks:
- tasks/*.yaml
"""


def _seed_dual_route_skill(
    root: Path,
    *,
    activation: str,
    detector: str,
) -> None:
    """Seed a full central fixture with one dual-route conditional skill."""

    seed_approval_docs(root)
    for category in _CATEGORIES:
        (root / "skills" / category).mkdir(parents=True)
    directory = root / "skills" / "tool" / "gas-city-kit"
    directory.mkdir()
    tags = approved(
        tuple(
            sorted(
                (
                    f"activation:{activation}",
                    detector,
                    "provenance:agents-owned",
                    "route:agent",
                    "route:project",
                    "tool:gas-city",
                    "updates:manual",
                    "usage:on-demand",
                )
            )
        )
    )
    encoded = json.dumps(list(tags), separators=(",", ":"))
    (directory / "SKILL.md").write_text(
        "---\n"
        "name: gas-city-kit\n"
        "description: gas city kit, rig selection, city toml, operator gates\n"
        "metadata:\n"
        '  version: "1.0.0"\n'
        f"  aihub.tags: '{encoded}'\n"
        "---\n"
        "# gas-city-kit\n\n"
        "Gas City kits require one declared city per authorized repository.\n",
        encoding="utf-8",
    )


def _seed_eval_suite(root: Path) -> None:
    tasks = root / "evals" / "gas-city-kit" / "tasks"
    tasks.mkdir(parents=True)
    (tasks.parent / "eval.yaml").write_text(_EVAL_YAML, encoding="utf-8")
    (tasks / "basic-usage.yaml").write_text(
        "id: gas-city-kit-happy-001\n"
        "name: Happy path gas-city-kit\n"
        "description: Register one opted-in rig inside a declared city.\n"
        "tags: [gas-city-kit, happy-path]\n"
        "inputs:\n"
        "  prompt: >-\n"
        "    The operator opted into the gas-city-kit capability for this checkout\n"
        "    and asks to register one rig. Read the declared city configuration,\n"
        "    confirm the operator approval, and report the declared store plus the\n"
        "    first observable checkpoint.\n"
        "expected:\n"
        "  output_contains: [operator, checkpoint, declared store]\n"
        "  output_not_contains: [invented city, unregistered rig]\n",
        encoding="utf-8",
    )
    (tasks / "edge-case.yaml").write_text(
        "id: gas-city-kit-edge-001\n"
        "name: Edge case gas-city-kit\n"
        "description: Stop at a missing rig declaration without a substitute store.\n"
        "inputs:\n"
        "  prompt: >-\n"
        "    The requested rig has no declared store in the city configuration.\n"
        "    Report the missing declaration and stop without creating an alternate\n"
        "    store or a substitute ledger.\n"
        "expected:\n"
        "  output_contains: [missing declaration, stopped]\n"
        "  output_not_contains: [alternate store, substitute ledger]\n",
        encoding="utf-8",
    )
    (tasks / "should-not-trigger.yaml").write_text(
        "id: gas-city-kit-negative-001\n"
        "name: Should not trigger gas-city-kit\n"
        "description: Ordinary repository work never activates the kit.\n"
        "tags: [gas-city-kit, anti-trigger]\n"
        "inputs:\n"
        "  prompt: >-\n"
        "    Fix one failing unit test in the current checkout. No rig, city, or\n"
        "    kit selection is requested for this change.\n"
        "expected:\n"
        "  output_not_contains: [rig registration, city configuration]\n",
        encoding="utf-8",
    )


def _write_skill_config(root: Path) -> None:
    (root / "config").mkdir()
    (root / "config" / "skills.json").write_text(
        json.dumps({"version": 2, "budgets": _BUDGETS}), encoding="utf-8"
    )


def test_opt_in_dual_route_skill_may_reference_project_vocabulary(
    tmp_path: Path,
) -> None:
    _write_skill_config(tmp_path)
    _seed_dual_route_skill(
        tmp_path,
        activation="opt-in",
        detector="detect:opt-in:gas-city-kit",
    )
    _seed_eval_suite(tmp_path)

    validate_skill_catalogs(Catalog(tmp_path))


def test_detected_dual_route_skill_rejects_non_portable_vocabulary(
    tmp_path: Path,
) -> None:
    _write_skill_config(tmp_path)
    _seed_dual_route_skill(
        tmp_path,
        activation="detected",
        detector="detect:marker:gas-city-kit.toml",
    )

    with pytest.raises(ValueError, match="not portable"):
        validate_skill_catalogs(Catalog(tmp_path))
