from __future__ import annotations

from pathlib import Path

from agents_governance.agent_profiles import AgentProvider
from agents_governance.projection_config import (
    HookClient,
    HookCoverage,
    ProjectionContext,
    ProjectionStatus,
    ProjectionSurface,
    load_projection_config,
)


def test_projection_contract_is_complete_and_calculated(tmp_path: Path) -> None:
    contract = load_projection_config(tmp_path)

    assert contract.version == 8
    assert contract.projection_manifest_version == 6
    assert contract.hook_manifest_version == 3
    assert len(contract.cells) == len(AgentProvider) * len(ProjectionContext) * len(
        ProjectionSurface
    )
    assert tuple(tmp_path.iterdir()) == ()


def test_provider_native_paths_are_derived_by_surface() -> None:
    contract = load_projection_config(Path.cwd())

    assert (
        contract.cell("claude", "personal", "skills").path == "${HOME}/.claude/skills"
    )
    assert contract.cell("codex", "project", "skills").path == ".agents/skills"
    assert contract.cell("codex", "project", "hooks").path == ".codex/hooks.json"
    assert contract.cell("codex", "project", "rules").path == "AGENTS.md"
    assert contract.cell("copilot", "project", "agents").path == ".github/agents"
    assert contract.cell("pool", "project", "skills").path == ".poolside/skills"
    assert (
        contract.cell("pool", "personal", "skills").status
        is ProjectionStatus.UNSUPPORTED
    )


def test_native_hook_fidelity_is_owned_by_provider_adapter() -> None:
    contract = load_projection_config(Path.cwd())

    codex = contract.cell("codex", "project", "hooks").events
    cursor = contract.cell("cursor", "project", "hooks").events
    gemini = contract.cell("gemini", "project", "hooks").events
    assert codex is not None and cursor is not None and gemini is not None
    assert codex["context_refresh"].native == ("SessionStart",)
    assert codex["subagent_start"].coverage is HookCoverage.EXACT
    assert cursor["session_start"].clients == (HookClient.LOCAL,)
    assert gemini["subagent_start"].status is ProjectionStatus.UNSUPPORTED


def test_project_detection_contains_no_repository_identity() -> None:
    contract = load_projection_config(Path.cwd())
    rendered = repr(contract.project_detection_rules)

    assert "datacosmos" not in rendered
    assert "gascity" not in rendered
    assert "aihub-internal" not in rendered
    assert {rule.rule_id for rule in contract.project_detection_rules} == {
        "associated-internal",
        "associated-internal-flext",
        "associated-upstream-fork",
        "flext-capability",
    }
