"""Observable contract tests for the public semantic bundle facade."""

from __future__ import annotations

import hashlib
import json
from importlib.metadata import distribution
from pathlib import Path

import pytest

from agents_governance import (
    BUNDLE_SCHEMA_VERSION,
    CAPSULE_MARKER,
    EvalPolicy,
    GovernanceBundle,
    __version__,
    render_capsule,
)
from agents_governance.delivery import DeliveryContract
from agents_governance.skill_resources import ResourcePolicy


def test_public_bundle_is_complete_and_versioned(
    governance_bundle: GovernanceBundle,
) -> None:
    assert governance_bundle.schema_version == BUNDLE_SCHEMA_VERSION
    assert governance_bundle.distribution_version == __version__
    assert isinstance(governance_bundle.eval_policy, EvalPolicy)
    assert governance_bundle.root.is_dir()
    assert governance_bundle.skills
    assert governance_bundle.commands
    assert governance_bundle.agents
    assert governance_bundle.rules
    assert governance_bundle.config.guarantees
    assert governance_bundle.law.prelude


def test_public_capsule_is_content_addressed(
    governance_bundle: GovernanceBundle,
) -> None:
    capsule = render_capsule(governance_bundle)

    assert capsule.header == f"<!-- {CAPSULE_MARKER} sha256:{capsule.digest} -->"
    assert capsule.text == f"{capsule.header}\n{capsule.body}\n"
    assert hashlib.sha256(capsule.body.encode("utf-8")).hexdigest() == capsule.digest
    assert "AI Hub owns publication and provider activation." in capsule.body
    for identity in governance_bundle.config.bootstrap_rules:
        assert f"## Rule `{identity}`" in capsule.body


def test_public_inventories_have_unique_physical_owners(
    governance_bundle: GovernanceBundle,
) -> None:
    skills = {skill.name: skill.directory for skill in governance_bundle.skills}
    commands = {command.name: command.path for command in governance_bundle.commands}
    agents = {agent.name: agent.path for agent in governance_bundle.agents}
    rules = {rule.identity: rule.path for rule in governance_bundle.rules}

    assert len(skills) == len(governance_bundle.skills)
    assert len(commands) == len(governance_bundle.commands)
    assert len(agents) == len(governance_bundle.agents)
    assert len(rules) == len(governance_bundle.rules)
    assert all(path.is_dir() and not path.is_symlink() for path in skills.values())
    assert all(path.is_file() and not path.is_symlink() for path in commands.values())
    assert all(path.is_file() and not path.is_symlink() for path in agents.values())
    assert all(path.is_file() and not path.is_symlink() for path in rules.values())


def test_distribution_exposes_no_runtime_executable() -> None:
    metadata = distribution("agents-governance")
    assert not metadata.entry_points


def test_resources_preserve_declared_policy_and_content(
    governance_bundle: GovernanceBundle,
) -> None:
    document = json.loads((governance_bundle.root / "config/skills.json").read_text())
    policy = ResourcePolicy.parse(document["resources"])
    for skill in governance_bundle.skills:
        paths = {resource.path for resource in skill.resources}
        expected = {
            path
            for path in skill.directory.rglob("*")
            if path.is_file() and path.name != "SKILL.md"
        }
        assert paths == expected
        for resource in skill.resources:
            assert resource == policy.resource(governance_bundle.root, resource.path)
            assert (
                resource.sha256
                == hashlib.sha256(resource.path.read_bytes()).hexdigest()
            )
            assert bool(resource.mode & 0o100) == resource.executable


def test_binary_policy_is_explicit_and_unknown_override_fails(
    governance_bundle: GovernanceBundle, tmp_path: Path
) -> None:
    document = json.loads((governance_bundle.root / "config/skills.json").read_text())
    section = document["resources"]
    identity = "tool/probe/assets/data.bin"
    section["overrides"] = {identity: {"format": "binary", "executable": False}}
    path = tmp_path / "skills" / identity
    path.parent.mkdir(parents=True)
    payload = b"\x00\xff\x80resource"
    path.write_bytes(payload)
    policy = ResourcePolicy.parse(section)
    resource = policy.resource(tmp_path, path)
    assert resource.sha256 == hashlib.sha256(payload).hexdigest()
    policy.validate_inventory(tmp_path, (resource,))
    with pytest.raises(ValueError, match="no catalog owner"):
        policy.validate_inventory(tmp_path, ())
    section["overrides"] = {}
    with pytest.raises(UnicodeDecodeError):
        ResourcePolicy.parse(section).resource(tmp_path, path)


def test_public_bundle_preserves_non_utf8_resource_and_policy(
    governance_source_fixture: Path, governance_bundle: GovernanceBundle
) -> None:
    root = governance_source_fixture
    skill = governance_bundle.skills[0]
    relative = skill.directory.relative_to(governance_bundle.root)
    path = root / relative / "assets" / "binary-probe.bin"
    path.parent.mkdir(exist_ok=True)
    payload = b"\x00\xff\x80full-binary-payload"
    path.write_bytes(payload)
    config_path = root / "config/skills.json"
    document = json.loads(config_path.read_text())
    document["resources"]["overrides"][path.relative_to(root / "skills").as_posix()] = {
        "format": "binary",
        "executable": True,
    }
    config_path.write_text(json.dumps(document))
    policy = ResourcePolicy.parse(document["resources"])
    path.chmod(policy.executable_mode)

    loaded = GovernanceBundle.load(root)
    resource = next(
        resource
        for record in loaded.skills
        for resource in record.resources
        if resource.path == path
    )
    assert resource.format == "binary"
    assert resource.executable
    assert resource.mode == policy.executable_mode
    assert resource.path.read_bytes() == payload
    assert resource.sha256 == hashlib.sha256(payload).hexdigest()
    document["resources"]["overrides"].pop(path.relative_to(root / "skills").as_posix())
    config_path.write_text(json.dumps(document))
    with pytest.raises(UnicodeDecodeError):
        GovernanceBundle.load(root)


def test_resource_policy_owns_an_immutable_copy(
    governance_bundle: GovernanceBundle,
) -> None:
    document = json.loads((governance_bundle.root / "config/skills.json").read_text())
    section = document["resources"]
    policy = ResourcePolicy.parse(section)
    expected = dict(policy.overrides)
    section["overrides"].clear()
    assert dict(policy.overrides) == expected
    assert not hasattr(policy.overrides, "clear")


def test_delivery_budget_holds_with_measured_composition(
    governance_bundle: GovernanceBundle,
) -> None:
    delivery = governance_bundle.delivery
    contract = delivery.contract

    assert contract.capsule_budget_chars > contract.restore_list_reserve_chars > 0
    assert contract.events
    assert delivery.total_chars == (
        delivery.prelude_chars
        + delivery.rule_summary_chars
        + delivery.skill_index_chars
    )
    assert delivery.total_chars <= contract.capsule_budget_chars - (
        contract.restore_list_reserve_chars
    )
    assert delivery.headroom_chars >= 0


def test_delivery_contract_rejects_payload_outside_grammar() -> None:
    with pytest.raises(ValueError, match="payload:<slug>"):
        DeliveryContract.from_mapping(
            {
                "capsule_budget_chars": 10000,
                "restore_list_reserve_chars": 512,
                "events": {
                    "instructions-loaded": ["rule-bodies-by-routing"],
                    "post-compact": ["payload:capsule-full", "payload:restore-list"],
                    "prompt-submit": ["payload:operator-precedence-reminder"],
                    "session-end": ["payload:findings-harvest"],
                    "session-start": ["payload:capsule-full"],
                    "subagent-start": ["payload:authority-subset"],
                },
            },
            "test",
        )


def test_delivery_contract_rejects_unsorted_events() -> None:
    with pytest.raises(ValueError, match="events must be sorted"):
        DeliveryContract.from_mapping(
            {
                "capsule_budget_chars": 10000,
                "restore_list_reserve_chars": 512,
                "events": {
                    "session-start": ["payload:capsule-full"],
                    "instructions-loaded": ["payload:rule-bodies-by-routing"],
                    "post-compact": ["payload:capsule-full", "payload:restore-list"],
                    "prompt-submit": ["payload:operator-precedence-reminder"],
                    "session-end": ["payload:findings-harvest"],
                    "subagent-start": ["payload:authority-subset"],
                },
            },
            "test",
        )


def test_agent_approval_lineage_is_complete(
    governance_bundle: GovernanceBundle,
) -> None:
    for agent in governance_bundle.agents:
        namespaces = {tag.split(":", 1)[0] for tag in agent.tags}
        assert {"decision", "effective"} <= namespaces
