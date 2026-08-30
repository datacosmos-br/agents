from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path, PurePosixPath

import pytest

from agents_governance.agent_profiles import (
    AgentArtifact,
    AgentContext,
    AgentProvider,
    AgentRenderError,
    audit_agent_profiles,
    render_agent,
)
from agents_governance.rules import audit_rule_specs, prompt_defense_body


def _authority(root: Path) -> None:
    (root / "agents" / "agent-wide").mkdir(parents=True)
    (root / "agents" / "project-wide").mkdir(parents=True)
    rule = root / "rules" / "security" / "prompt-defense.md"
    rule.parent.mkdir(parents=True)
    rule.write_text("# Prompt defense\n", encoding="utf-8")


def _profile(
    root: Path,
    name: str = "reviewer",
    *,
    distribution: str = "project-wide",
    tags: tuple[str, ...] = (
        "activation:opt-in",
        "mode:review",
        "role:reviewer",
    ),
    tools: str = "",
    instructions: str = "# Instructions\n",
) -> Path:
    path = root / "agents" / distribution / f"{name}.md"
    encoded_tags = json.dumps(tags)
    path.write_text(
        "---\n"
        f"name: {name}\n"
        "description: Review changes for correctness.\n"
        f"{tools}"
        "metadata:\n"
        f"  aihub.tags: '{encoded_tags}'\n"
        "---\n\n"
        f"{instructions}",
        encoding="utf-8",
    )
    return path


def test_audit_returns_complete_strict_inventory(tmp_path: Path) -> None:
    _authority(tmp_path)
    personal = _profile(
        tmp_path,
        "operator",
        distribution="agent-wide",
        tags=("activation:always", "mode:operate", "role:operator"),
    )
    project = _profile(
        tmp_path,
        "go-reviewer",
        tags=(
            "activation:detected",
            "detect:marker:go.mod",
            "mode:review",
            "role:reviewer",
        ),
    )

    profiles = audit_agent_profiles(tmp_path)

    assert [profile.path for profile in profiles] == [personal, project]
    assert profiles[0].distribution == "agent-wide"
    assert profiles[1].detectors == ("detect:marker:go.mod",)
    assert profiles[1].rule_paths == ("rules/security/prompt-defense.md",)


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda text: text.replace("name: reviewer\n", ""), "name is required"),
        (lambda text: text.replace("name: reviewer", "name: other"), "equal filename"),
        (
            lambda text: text.replace(
                "description: Review changes for correctness.\n", ""
            ),
            "description is required",
        ),
        (
            lambda text: text.replace("metadata:\n", "model: invented\nmetadata:\n"),
            "must not declare model",
        ),
        (
            lambda text: text.replace("activation:opt-in", "activation:always"),
            "project-wide profiles forbid activation:always",
        ),
    ],
)
def test_invalid_profile_raises_first_defect(
    tmp_path: Path, mutator: Callable[[str], str], message: str
) -> None:
    _authority(tmp_path)
    path = _profile(tmp_path)
    path.write_text(mutator(path.read_text(encoding="utf-8")), encoding="utf-8")

    with pytest.raises((TypeError, ValueError), match=message):
        audit_agent_profiles(tmp_path)


@pytest.mark.parametrize(
    "reference",
    ["Beads", "GasCity", "~/agents/rules/python.md", "/home/operator/project"],
)
def test_project_profiles_reject_nonportable_references(
    tmp_path: Path, reference: str
) -> None:
    _authority(tmp_path)
    _profile(tmp_path, instructions=f"# Instructions\n\nUse {reference}.\n")

    with pytest.raises(ValueError, match="not portable"):
        audit_agent_profiles(tmp_path)


def test_discovery_stops_at_first_sorted_defect(tmp_path: Path) -> None:
    _authority(tmp_path)
    first = _profile(tmp_path, "a-first")
    _profile(tmp_path, "z-second")
    first.write_text("invalid\n", encoding="utf-8")

    with pytest.raises(ValueError, match="a-first.md: missing YAML frontmatter"):
        audit_agent_profiles(tmp_path)


def test_missing_prompt_defense_owner_raises_before_profile_read(
    tmp_path: Path,
) -> None:
    _authority(tmp_path)
    _profile(tmp_path)
    (tmp_path / "rules" / "security" / "prompt-defense.md").unlink()

    with pytest.raises(ValueError, match="prompt-defense owner"):
        audit_agent_profiles(tmp_path)


def test_supported_renderers_preserve_capabilities(tmp_path: Path) -> None:
    _authority(tmp_path)
    _profile(
        tmp_path,
        tools="tools: [filesystem:read, filesystem:write, mcp:context7:query-docs]\n",
    )
    profile = audit_agent_profiles(tmp_path)[0]
    prompt_defense = "# Prompt defense\n"

    claude = render_agent(
        profile,
        AgentProvider.CLAUDE,
        AgentContext.PROJECT,
        prompt_defense=prompt_defense,
    )
    gemini = render_agent(
        profile,
        AgentProvider.GEMINI,
        AgentContext.PROJECT,
        prompt_defense=prompt_defense,
    )
    opencode = render_agent(
        profile,
        AgentProvider.OPENCODE,
        AgentContext.PROJECT,
        prompt_defense=prompt_defense,
    )
    copilot = render_agent(
        profile,
        AgentProvider.COPILOT,
        AgentContext.PROJECT,
        prompt_defense=prompt_defense,
    )

    assert claude.destination == PurePosixPath(".claude/agents/reviewer.md")
    assert "- Read\n" in claude.content
    assert "- mcp__context7__query-docs\n" in claude.content
    assert gemini.destination == PurePosixPath(".gemini/agents/reviewer.md")
    assert "- mcp_context7_query-docs\n" in gemini.content
    assert opencode.destination == PurePosixPath(".opencode/agents/reviewer.md")
    assert "  context7_query-docs: allow\n" in opencode.content
    assert copilot.destination == PurePosixPath(".github/agents/reviewer.agent.md")
    assert "- read\n" in copilot.content
    assert "- context7/query-docs\n" in copilot.content


def test_empty_capability_allowlists_never_expand_to_provider_defaults(
    tmp_path: Path,
) -> None:
    _authority(tmp_path)
    _profile(tmp_path)
    profile = audit_agent_profiles(tmp_path)[0]

    claude = render_agent(
        profile,
        AgentProvider.CLAUDE,
        AgentContext.PROJECT,
        prompt_defense="# Prompt defense\n",
    )
    copilot = render_agent(
        profile,
        AgentProvider.COPILOT,
        AgentContext.PROJECT,
        prompt_defense="# Prompt defense\n",
    )

    assert "tools: []\n" in claude.content
    assert "tools: []\n" in copilot.content


@pytest.mark.parametrize(
    "provider",
    [
        AgentProvider.CURSOR,
        AgentProvider.CODEX,
        AgentProvider.ANTIGRAVITY,
    ],
)
def test_unproven_agent_providers_raise(
    provider: AgentProvider, tmp_path: Path
) -> None:
    _authority(tmp_path)
    _profile(tmp_path)
    profile = audit_agent_profiles(tmp_path)[0]

    with pytest.raises(AgentRenderError, match="^UNSUPPORTED:"):
        render_agent(
            profile,
            provider,
            AgentContext.PROJECT,
            prompt_defense="# Prompt defense\n",
        )


def test_artifact_rejects_absolute_destination() -> None:
    with pytest.raises(ValueError, match="relative physical path"):
        AgentArtifact(
            AgentProvider.CLAUDE,
            AgentContext.PROJECT,
            "reviewer",
            PurePosixPath("/reviewer.md"),
            "# Instructions\n",
        )


def test_canonical_inventory_has_exactly_sixty_two_profiles() -> None:
    root = Path(__file__).resolve().parents[1]

    assert len(audit_agent_profiles(root)) == 62


def test_render_agent_rejects_prompt_defense_frontmatter(tmp_path: Path) -> None:
    _authority(tmp_path)
    _profile(tmp_path)
    profile = audit_agent_profiles(tmp_path)[0]

    with pytest.raises(AgentRenderError, match="body text, not frontmatter"):
        render_agent(
            profile,
            AgentProvider.GEMINI,
            AgentContext.PROJECT,
            prompt_defense=(
                "---\n"
                "description: Composing prompt-defense constraints.\n"
                "---\n\n"
                "# Prompt defense baseline\n"
            ),
        )


def test_composed_python_reviewer_excludes_prompt_defense_frontmatter() -> None:
    root = Path(__file__).resolve().parents[1]
    profiles = {profile.name: profile for profile in audit_agent_profiles(root)}
    defense = prompt_defense_body(audit_rule_specs(root))
    rendered = render_agent(
        profiles["python-reviewer"],
        AgentProvider.GEMINI,
        AgentContext.PROJECT,
        prompt_defense=defense,
    )
    body = rendered.content.split("---\n", 2)[2].lstrip()

    assert body.startswith(defense.lstrip())
    assert "When invoked:\n\n1." in rendered.content


def test_chief_of_staff_uses_only_the_declared_tone_owner() -> None:
    root = Path(__file__).resolve().parents[1]
    body = (root / "agents" / "agent-wide" / "chief-of-staff.md").read_text(
        encoding="utf-8"
    )

    assert "operator-configured tone owner" in body
    assert "SOUL.md" not in body
