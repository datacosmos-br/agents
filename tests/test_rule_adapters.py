from __future__ import annotations

from pathlib import Path, PurePosixPath

import pytest
import yaml

from agents_governance.rule_adapters import (
    RuleArtifact,
    RuleContext,
    RuleProvider,
    RuleRenderError,
    render_rule,
)
from agents_governance.rules import RuleActivation, RuleSpec


def _spec(
    *,
    identity: str = "architecture/engineering-core",
    description: str | None = "Apply the canonical engineering sequence.",
    globs: tuple[str, ...] = (),
    body: str = "# Engineering core\n\nPreserve every canonical requirement.\n",
) -> RuleSpec:
    return RuleSpec(
        Path("/repository/rules") / f"{identity}.md",
        identity,
        description,
        RuleActivation.PATH_SCOPED if globs else RuleActivation.ALWAYS,
        globs,
        (),
        body,
    )


def _metadata(content: str) -> tuple[dict[str, object], str]:
    marker = content.index("\n---\n", 4)
    loaded = yaml.safe_load(content[4:marker])
    assert isinstance(loaded, dict)
    return loaded, content[marker + 5 :].removeprefix("\n")


@pytest.mark.parametrize(
    ("provider", "context", "destination"),
    [
        (
            RuleProvider.CLAUDE,
            RuleContext.PERSONAL,
            PurePosixPath(".claude/rules/architecture--engineering-core.md"),
        ),
        (
            RuleProvider.CURSOR,
            RuleContext.PROJECT,
            PurePosixPath(".cursor/rules/architecture--engineering-core.mdc"),
        ),
        (
            RuleProvider.COPILOT,
            RuleContext.PROJECT,
            PurePosixPath(
                ".github/instructions/architecture--engineering-core.instructions.md"
            ),
        ),
    ],
)
def test_supported_rules_render_deterministically(
    provider: RuleProvider, context: RuleContext, destination: PurePosixPath
) -> None:
    spec = _spec()

    first = render_rule(spec, provider, context)

    assert first == render_rule(spec, provider, context)
    assert first.destination == destination
    assert first.content.endswith(spec.body)


def test_local_links_are_rebased_to_projected_siblings() -> None:
    spec = RuleSpec(
        Path("/repository/rules/architecture/engineering-core.md"),
        "architecture/engineering-core",
        "Apply the canonical engineering sequence.",
        RuleActivation.ALWAYS,
        (),
        ("rules/architecture/owner.md", "rules/storage.md"),
        "Read [owner](owner.md), [storage](../storage.md), and "
        "[official docs](https://example.com/rules).\n",
    )

    rendered = render_rule(spec, RuleProvider.CLAUDE, RuleContext.PROJECT)

    assert "(architecture--owner.md)" in rendered.content
    assert "(storage.md)" in rendered.content
    assert "(https://example.com/rules)" in rendered.content


def test_native_path_scope_metadata_is_preserved() -> None:
    spec = _spec(globs=("*.py", "src/**/*.py"))

    claude = render_rule(spec, RuleProvider.CLAUDE, RuleContext.PROJECT)
    cursor = render_rule(spec, RuleProvider.CURSOR, RuleContext.PROJECT)
    copilot = render_rule(spec, RuleProvider.COPILOT, RuleContext.PROJECT)

    assert _metadata(claude.content)[0] == {"paths": ["*.py", "src/**/*.py"]}
    assert _metadata(cursor.content)[0] == {
        "description": spec.description,
        "globs": ["*.py", "src/**/*.py"],
        "alwaysApply": False,
    }
    assert _metadata(copilot.content)[0] == {"applyTo": "*.py,src/**/*.py"}


@pytest.mark.parametrize(
    ("provider", "context"),
    [
        (RuleProvider.CURSOR, RuleContext.PERSONAL),
        (RuleProvider.ANTIGRAVITY, RuleContext.PERSONAL),
        (RuleProvider.ANTIGRAVITY, RuleContext.PROJECT),
        (RuleProvider.GEMINI, RuleContext.PERSONAL),
        (RuleProvider.GEMINI, RuleContext.PROJECT),
        (RuleProvider.OPENCODE, RuleContext.PERSONAL),
        (RuleProvider.OPENCODE, RuleContext.PROJECT),
        (RuleProvider.CODEX, RuleContext.PERSONAL),
        (RuleProvider.CODEX, RuleContext.PROJECT),
    ],
)
def test_unsupported_combinations_raise_immediately(
    provider: RuleProvider, context: RuleContext
) -> None:
    with pytest.raises(RuleRenderError, match="^UNSUPPORTED:"):
        render_rule(_spec(), provider, context)


def test_copilot_rejects_lossy_comma_delimited_glob() -> None:
    with pytest.raises(RuleRenderError, match="comma delimiter"):
        render_rule(
            _spec(globs=("src/**/*.{ts,tsx}",)),
            RuleProvider.COPILOT,
            RuleContext.PROJECT,
        )


def test_unknown_provider_and_context_propagate_enum_errors() -> None:
    with pytest.raises(ValueError, match="invented"):
        render_rule(_spec(), "invented", RuleContext.PROJECT)
    with pytest.raises(ValueError, match="invented"):
        render_rule(_spec(), RuleProvider.CLAUDE, "invented")


def test_artifact_rejects_absolute_destination() -> None:
    with pytest.raises(ValueError, match="relative physical path"):
        RuleArtifact(
            RuleProvider.CLAUDE,
            RuleContext.PROJECT,
            "core",
            PurePosixPath("/absolute.md"),
            "# Body\n",
        )
