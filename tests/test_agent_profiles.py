from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents_governance.agent_profiles import (
    AgentArtifact,
    AgentContext,
    AgentProvider,
    UnsupportedAgent,
    audit_agent_profiles,
    render_agent,
)


def _write_rule(root: Path) -> Path:
    rule = root / "rules" / "security" / "prompt-defense.md"
    rule.parent.mkdir(parents=True, exist_ok=True)
    rule.write_text("# Prompt defense\n", encoding="utf-8")
    return rule


def _tags(*values: str) -> str:
    return "metadata:\n  aihub.tags: '" + json.dumps(values) + "'\n"


def _valid_frontmatter(
    name: str,
    *,
    distribution: str = "project-wide",
    description: str = "Review changes for correctness.",
    extra: str = "",
    tags: tuple[str, ...] | None = None,
) -> str:
    default_tags = (
        ("activation:always", "mode:review", "role:reviewer")
        if distribution == "agent-wide"
        else ("activation:opt-in", "mode:review", "role:reviewer")
    )
    return (
        f"name: {name}\ndescription: {description}\n{extra}"
        f"{_tags(*(tags or default_tags))}"
    )


def _write_profile(
    root: Path,
    name: str = "reviewer",
    *,
    distribution: str = "project-wide",
    frontmatter: str | None = None,
    instructions: str = "# Instructions\n",
    write_rule: bool = True,
) -> Path:
    agents = root / "agents" / distribution
    agents.mkdir(parents=True, exist_ok=True)
    if write_rule:
        _write_rule(root)
    metadata = frontmatter or _valid_frontmatter(name, distribution=distribution)
    profile = agents / f"{name}.md"
    profile.write_text(f"---\n{metadata}---\n\n{instructions}", encoding="utf-8")
    return profile


def _write_minimal_authority(root: Path) -> None:
    (root / "config").mkdir()
    (root / "skills").mkdir()
    (root / "commands").mkdir()
    (root / "config" / "skills.json").write_text(
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


def test_agent_profile_audit_accepts_strict_recursive_profile(tmp_path: Path) -> None:
    profile_path = _write_profile(tmp_path)

    audit = audit_agent_profiles(tmp_path)

    assert audit.findings == ()
    assert len(audit.profiles) == 1
    profile = audit.profiles[0]
    assert profile.path == profile_path
    assert profile.name == "reviewer"
    assert profile.description == "Review changes for correctness."
    assert profile.distribution == "project-wide"
    assert profile.tags == (
        "activation:opt-in",
        "mode:review",
        "role:reviewer",
    )
    assert profile.rule_paths == ("rules/security/prompt-defense.md",)


def test_agent_profile_audit_accepts_detected_and_agent_wide_profiles(
    tmp_path: Path,
) -> None:
    _write_profile(tmp_path, "personal", distribution="agent-wide")
    _write_profile(
        tmp_path,
        "go-reviewer",
        frontmatter=_valid_frontmatter(
            "go-reviewer",
            tags=(
                "activation:detected",
                "detect:marker:go.mod",
                "mode:review",
                "role:reviewer",
            ),
        ),
    )

    audit = audit_agent_profiles(tmp_path)

    assert audit.findings == ()
    assert [(item.name, item.distribution) for item in audit.profiles] == [
        ("personal", "agent-wide"),
        ("go-reviewer", "project-wide"),
    ]


@pytest.mark.parametrize(
    "private_reference",
    [
        "FLEXT",
        "AI Hub",
        "GasCity",
        "Dolt",
        "Beads",
        "~/.agents/rules/python.md",
        ".claude/settings.json",
        "$HOME/private/project",
        "/home/operator/private/project",
        "file:///private/project",
    ],
)
def test_project_wide_profile_rejects_non_portable_reference(
    tmp_path: Path, private_reference: str
) -> None:
    _write_profile(
        tmp_path,
        instructions=f"# Instructions\n\nUse {private_reference}.\n",
    )

    audit = audit_agent_profiles(tmp_path)

    assert audit.profiles == ()
    assert [(finding.path, finding.code) for finding in audit.findings] == [
        ("agents/project-wide/reviewer.md", "agent-profile-non-generic")
    ]


def test_agent_wide_profile_can_own_personal_workflow_reference(
    tmp_path: Path,
) -> None:
    _write_profile(
        tmp_path,
        distribution="agent-wide",
        instructions="# Instructions\n\nUse the operator's AI Hub workflow.\n",
    )

    audit = audit_agent_profiles(tmp_path)

    assert audit.findings == ()
    assert [profile.name for profile in audit.profiles] == ["reviewer"]


def test_project_wide_profile_accepts_project_owned_configuration(
    tmp_path: Path,
) -> None:
    _write_profile(
        tmp_path,
        instructions=(
            "# Instructions\n\n"
            "Read AGENTS.md, CLAUDE.md, config/project.yaml, and "
            ".github/workflows/ci.yml from the active project.\n"
        ),
    )

    audit = audit_agent_profiles(tmp_path)

    assert audit.findings == ()
    assert [profile.name for profile in audit.profiles] == ["reviewer"]


@pytest.mark.parametrize(
    ("frontmatter", "code"),
    [
        (
            "description: Missing name.\n"
            + _tags("activation:opt-in", "mode:review", "role:reviewer"),
            "agent-profile-name",
        ),
        (
            _valid_frontmatter("different"),
            "agent-profile-name",
        ),
        (
            "name: reviewer\n"
            + _tags("activation:opt-in", "mode:review", "role:reviewer"),
            "agent-profile-description",
        ),
        (
            _valid_frontmatter("reviewer", extra="model: sonnet\n"),
            "agent-profile-model",
        ),
    ],
)
def test_agent_profile_audit_rejects_invalid_metadata(
    tmp_path: Path, frontmatter: str, code: str
) -> None:
    _write_profile(tmp_path, frontmatter=frontmatter)

    assert {finding.code for finding in audit_agent_profiles(tmp_path).findings} == {
        code
    }


@pytest.mark.parametrize(
    "contents",
    [
        "# Missing frontmatter\n",
        "---\nname: [invalid\n---\n",
        "---\n- not\n- a\n- mapping\n---\n",
        "---\nname: reviewer\ndescription: Review.\n",
    ],
)
def test_agent_profile_audit_requires_yaml_frontmatter(
    tmp_path: Path, contents: str
) -> None:
    profile = _write_profile(tmp_path)
    profile.write_text(contents, encoding="utf-8")

    findings = audit_agent_profiles(tmp_path).findings

    assert len(findings) == 1
    assert findings[0].code == "agent-profile-frontmatter"


def test_agent_profile_audit_rejects_flat_unknown_and_nested_paths(
    tmp_path: Path,
) -> None:
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "flat.md").write_text("# Flat\n", encoding="utf-8")
    (agents / "foreign" / "nested").mkdir(parents=True)
    (agents / "foreign" / "nested" / "profile.md").write_text(
        "# Foreign\n", encoding="utf-8"
    )
    (agents / "project-wide" / "nested").mkdir(parents=True)
    (agents / "project-wide" / "nested" / "profile.md").write_text(
        "# Nested\n", encoding="utf-8"
    )

    findings = audit_agent_profiles(tmp_path).findings

    assert findings
    assert {finding.code for finding in findings} == {"agent-profile-path"}


def test_agent_profile_audit_rejects_symlink_and_non_regular_file(
    tmp_path: Path,
) -> None:
    agents = tmp_path / "agents" / "project-wide"
    agents.mkdir(parents=True)
    target = tmp_path / "target.md"
    target.write_text("# Target\n", encoding="utf-8")
    (agents / "linked.md").symlink_to(target)
    (agents / "directory.md").mkdir()

    findings = audit_agent_profiles(tmp_path).findings

    assert {(finding.path, finding.code) for finding in findings} == {
        ("agents/project-wide/directory.md", "agent-profile-regular-file"),
        ("agents/project-wide/linked.md", "agent-profile-symlink"),
    }


def test_agent_profile_audit_rejects_retired_manifest_and_dispatcher(
    tmp_path: Path,
) -> None:
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "manifest.json").write_text("{}\n", encoding="utf-8")
    (agents / "dispatcher.md").write_text("# Dispatcher\n", encoding="utf-8")

    findings = audit_agent_profiles(tmp_path).findings

    assert {(finding.path, finding.code) for finding in findings} == {
        ("agents/dispatcher.md", "agent-profile-retired-surface"),
        ("agents/manifest.json", "agent-profile-retired-surface"),
    }


@pytest.mark.parametrize(
    ("distribution", "tags", "code"),
    [
        (
            "project-wide",
            ("activation:opt-in", "mode:review", "mode:review", "role:reviewer"),
            "agent-profile-tags",
        ),
        (
            "project-wide",
            ("role:reviewer", "mode:review", "activation:opt-in"),
            "agent-profile-tags",
        ),
        ("project-wide", ("mode:review", "role:reviewer"), "agent-profile-activation"),
        (
            "project-wide",
            ("activation:detected", "mode:review", "role:reviewer"),
            "agent-profile-detector",
        ),
        (
            "project-wide",
            (
                "activation:opt-in",
                "detect:marker:go.mod",
                "mode:review",
                "role:reviewer",
            ),
            "agent-profile-detector",
        ),
        (
            "agent-wide",
            ("activation:opt-in", "mode:review", "role:reviewer"),
            "agent-profile-distribution",
        ),
        (
            "project-wide",
            ("activation:always", "mode:review", "role:reviewer"),
            "agent-profile-distribution",
        ),
    ],
)
def test_agent_profile_audit_rejects_tag_contract_violations(
    tmp_path: Path, distribution: str, tags: tuple[str, ...], code: str
) -> None:
    _write_profile(
        tmp_path,
        distribution=distribution,
        frontmatter=_valid_frontmatter(
            "reviewer", distribution=distribution, tags=tags
        ),
    )

    assert code in {finding.code for finding in audit_agent_profiles(tmp_path).findings}


def test_agent_profile_audit_rejects_ambiguous_name_across_distributions(
    tmp_path: Path,
) -> None:
    _write_profile(tmp_path, distribution="project-wide")
    _write_profile(tmp_path, distribution="agent-wide")

    audit = audit_agent_profiles(tmp_path)

    assert audit.profiles == ()
    assert [finding.code for finding in audit.findings].count(
        "agent-profile-ambiguous"
    ) == 2


def test_agent_profile_audit_rejects_inline_prompt_defense(tmp_path: Path) -> None:
    _write_profile(
        tmp_path,
        instructions="## Prompt Defense Baseline\n\n- Duplicated policy.\n",
    )

    assert {finding.code for finding in audit_agent_profiles(tmp_path).findings} == {
        "agent-profile-inline-rule"
    }


def test_agent_profile_audit_requires_physical_prompt_defense_owner(
    tmp_path: Path,
) -> None:
    _write_profile(tmp_path, write_rule=False)

    audit = audit_agent_profiles(tmp_path)

    assert audit.profiles == ()
    assert [(finding.path, finding.code) for finding in audit.findings] == [
        ("rules/security/prompt-defense.md", "agent-profile-rule-owner")
    ]


@pytest.mark.parametrize(
    ("extra", "code"),
    [
        ("color: cyan\n", "agent-profile-frontmatter"),
        ("tools: [Read]\n", "agent-profile-tools"),
        ("tools: [filesystem:unknown]\n", "agent-profile-tools"),
    ],
)
def test_agent_profile_rejects_provider_specific_metadata(
    tmp_path: Path, extra: str, code: str
) -> None:
    _write_profile(
        tmp_path,
        frontmatter=_valid_frontmatter("reviewer", extra=extra),
    )

    assert {finding.code for finding in audit_agent_profiles(tmp_path).findings} == {
        code
    }


def test_supported_agent_adapters_preserve_canonical_capabilities(
    tmp_path: Path,
) -> None:
    _write_profile(
        tmp_path,
        frontmatter=_valid_frontmatter(
            "reviewer",
            extra=(
                "tools: [filesystem:read, filesystem:write, filesystem:grep, "
                "filesystem:glob, shell:execute, web:fetch, web:search, "
                "mcp:context7:query-docs]\n"
            ),
        ),
    )
    profile = audit_agent_profiles(tmp_path).profiles[0]

    claude = render_agent(
        profile,
        AgentProvider.CLAUDE,
        AgentContext.PROJECT,
        prompt_defense="# Prompt defense\n",
    )
    gemini = render_agent(
        profile,
        AgentProvider.GEMINI,
        AgentContext.PROJECT,
        prompt_defense="# Prompt defense\n",
    )
    opencode = render_agent(
        profile,
        AgentProvider.OPENCODE,
        AgentContext.PROJECT,
        prompt_defense="# Prompt defense\n",
    )

    assert isinstance(claude, AgentArtifact)
    assert claude.destination.as_posix() == ".claude/agents/reviewer.md"
    assert "- Read\n" in claude.content
    assert "- Edit\n" in claude.content
    assert "- Write\n" in claude.content
    assert "- mcp__context7__query-docs\n" in claude.content

    assert isinstance(gemini, AgentArtifact)
    assert gemini.destination.as_posix() == ".gemini/agents/reviewer.md"
    assert "kind: local\n" in gemini.content
    assert "- read_file\n" in gemini.content
    assert "- replace\n" in gemini.content
    assert "- write_file\n" in gemini.content
    assert "- mcp_context7_query-docs\n" in gemini.content

    assert isinstance(opencode, AgentArtifact)
    assert opencode.destination.as_posix() == ".opencode/agents/reviewer.md"
    assert "mode: subagent\n" in opencode.content
    assert "permission:\n  '*': deny\n" in opencode.content
    assert "  read: allow\n" in opencode.content
    assert "  edit: allow\n" in opencode.content
    assert "  context7_query-docs: allow\n" in opencode.content


@pytest.mark.parametrize(
    ("provider", "reason"),
    [
        (AgentProvider.CURSOR, "capability allowlist"),
        (AgentProvider.CODEX, "capability allowlist"),
        (AgentProvider.ANTIGRAVITY, "MCP tool identity"),
    ],
)
def test_unrepresentable_agent_adapters_are_explicit(
    tmp_path: Path, provider: AgentProvider, reason: str
) -> None:
    _write_profile(
        tmp_path,
        frontmatter=_valid_frontmatter(
            "reviewer", extra="tools: [mcp:context7:query-docs]\n"
        ),
    )
    profile = audit_agent_profiles(tmp_path).profiles[0]

    rendered = render_agent(
        profile,
        provider,
        AgentContext.PROJECT,
        prompt_defense="# Prompt defense\n",
    )

    assert isinstance(rendered, UnsupportedAgent)
    assert reason in rendered.reason
