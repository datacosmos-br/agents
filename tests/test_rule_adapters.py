from __future__ import annotations

from pathlib import Path, PurePosixPath

import pytest
import yaml

from agents_governance.rule_adapters import (
    RuleAdapterStatus,
    RuleArtifact,
    RuleContext,
    RuleProvider,
    RuleRenderError,
    UnsupportedRule,
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
        path=Path("/repository/rules") / f"{identity}.md",
        identity=identity,
        description=description,
        activation=(RuleActivation.PATH_SCOPED if globs else RuleActivation.ALWAYS),
        globs=globs,
        references=(),
        body=body,
    )


def _metadata(content: str) -> tuple[dict[str, object], str]:
    assert content.startswith("---\n")
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
            RuleProvider.CLAUDE,
            RuleContext.PROJECT,
            PurePosixPath(".claude/rules/architecture--engineering-core.md"),
        ),
        (
            RuleProvider.CURSOR,
            RuleContext.PROJECT,
            PurePosixPath(".cursor/rules/architecture--engineering-core.mdc"),
        ),
        (
            RuleProvider.COPILOT,
            RuleContext.PERSONAL,
            PurePosixPath(
                ".copilot/instructions/architecture--engineering-core.instructions.md"
            ),
        ),
        (
            RuleProvider.COPILOT,
            RuleContext.PROJECT,
            PurePosixPath(
                ".github/instructions/architecture--engineering-core.instructions.md"
            ),
        ),
        (
            RuleProvider.ANTIGRAVITY,
            RuleContext.PROJECT,
            PurePosixPath(".agents/rules/architecture--engineering-core.md"),
        ),
    ],
)
def test_supported_always_rules_render_deterministically_without_weakening_body(
    provider: RuleProvider, context: RuleContext, destination: PurePosixPath
) -> None:
    spec = _spec()

    first = render_rule(spec, provider, context)
    second = render_rule(spec, provider, context)

    assert isinstance(first, RuleArtifact)
    assert first == second
    assert first.status is RuleAdapterStatus.SUPPORTED
    assert first.provider is provider
    assert first.context is context
    assert first.identity == spec.identity
    assert first.destination == destination
    assert not first.destination.is_absolute()
    assert first.content.endswith(spec.body)
    assert "model:" not in first.content
    assert "/repository/rules" not in first.content


def test_recursive_identities_have_collision_free_flat_physical_names() -> None:
    first = render_rule(
        _spec(identity="architecture/engineering-core"),
        RuleProvider.CLAUDE,
        RuleContext.PROJECT,
    )
    second = render_rule(
        _spec(identity="architecture-engineering/core"),
        RuleProvider.CLAUDE,
        RuleContext.PROJECT,
    )

    assert isinstance(first, RuleArtifact)
    assert isinstance(second, RuleArtifact)
    assert first.destination.name == "architecture--engineering-core.md"
    assert second.destination.name == "architecture-engineering--core.md"
    assert first.destination != second.destination


@pytest.mark.parametrize(
    ("provider", "suffix"),
    [
        (RuleProvider.CLAUDE, ".md"),
        (RuleProvider.CURSOR, ".mdc"),
        (RuleProvider.COPILOT, ".instructions.md"),
        (RuleProvider.ANTIGRAVITY, ".md"),
    ],
)
def test_local_rule_links_are_rebased_to_physical_projected_siblings(
    provider: RuleProvider, suffix: str
) -> None:
    spec = RuleSpec(
        path=Path("/repository/rules/architecture/engineering-core.md"),
        identity="architecture/engineering-core",
        description="Apply the canonical engineering sequence.",
        activation=RuleActivation.ALWAYS,
        globs=(),
        references=(
            "rules/architecture/generalized-abstraction.md",
            "rules/storage.md",
        ),
        body=(
            "Compose [ownership](generalized-abstraction.md) and "
            "[storage](../storage.md#scratch). Keep "
            "[official docs](https://example.com/rules) external.\n"
        ),
    )

    rendered = render_rule(spec, provider, RuleContext.PROJECT)

    assert isinstance(rendered, RuleArtifact)
    assert f"(architecture--generalized-abstraction{suffix})" in rendered.content
    assert f"(storage{suffix})" in rendered.content
    assert "(https://example.com/rules)" in rendered.content


@pytest.mark.parametrize(
    ("provider", "context"),
    [
        (RuleProvider.CURSOR, RuleContext.PERSONAL),
        (RuleProvider.ANTIGRAVITY, RuleContext.PERSONAL),
        (RuleProvider.GEMINI, RuleContext.PERSONAL),
        (RuleProvider.GEMINI, RuleContext.PROJECT),
        (RuleProvider.OPENCODE, RuleContext.PERSONAL),
        (RuleProvider.OPENCODE, RuleContext.PROJECT),
        (RuleProvider.CODEX, RuleContext.PERSONAL),
        (RuleProvider.CODEX, RuleContext.PROJECT),
    ],
)
def test_unsupported_item_scoped_combinations_are_loud_and_typed(
    provider: RuleProvider, context: RuleContext
) -> None:
    spec = _spec()

    rendered = render_rule(spec, provider, context)

    assert isinstance(rendered, UnsupportedRule)
    assert rendered.status is RuleAdapterStatus.UNSUPPORTED
    assert rendered.provider is provider
    assert rendered.context is context
    assert rendered.identity == spec.identity
    assert rendered.reason.startswith("UNSUPPORTED: ")


def test_codex_rejects_markdown_rule_directory_as_execution_policy() -> None:
    rendered = render_rule(_spec(), RuleProvider.CODEX, RuleContext.PROJECT)

    assert isinstance(rendered, UnsupportedRule)
    assert ".codex/rules" in rendered.reason
    assert "Starlark" in rendered.reason
    assert "AGENTS.md" in rendered.reason


def test_claude_path_scopes_use_native_paths_array_and_preserve_body() -> None:
    spec = _spec(globs=("*.py", "src/**/*.py"))

    rendered = render_rule(spec, RuleProvider.CLAUDE, RuleContext.PROJECT)

    assert isinstance(rendered, RuleArtifact)
    metadata, body = _metadata(rendered.content)
    assert metadata == {"paths": ["*.py", "src/**/*.py"]}
    assert body == spec.body


@pytest.mark.parametrize("globs", [(), ("*.py", "src/**/*.py")])
def test_cursor_metadata_preserves_explicit_activation_and_scopes(
    globs: tuple[str, ...],
) -> None:
    spec = _spec(globs=globs)

    rendered = render_rule(spec, RuleProvider.CURSOR, RuleContext.PROJECT)

    assert isinstance(rendered, RuleArtifact)
    metadata, body = _metadata(rendered.content)
    assert metadata == {
        "description": spec.description,
        "globs": list(globs),
        "alwaysApply": not globs,
    }
    assert body == spec.body


def test_cursor_without_description_does_not_invent_model_routing() -> None:
    rendered = render_rule(
        _spec(description=None), RuleProvider.CURSOR, RuleContext.PROJECT
    )

    assert isinstance(rendered, RuleArtifact)
    metadata, _body = _metadata(rendered.content)
    assert metadata == {"description": "", "globs": [], "alwaysApply": True}


def test_provider_frontmatter_uses_safe_yaml_without_scalar_coercion() -> None:
    spec = _spec(
        description='Apply "quoted": values # literally.',
        globs=("on", "src/**/[a-z].py"),
    )

    rendered = render_rule(spec, RuleProvider.CURSOR, RuleContext.PROJECT)

    assert isinstance(rendered, RuleArtifact)
    metadata, body = _metadata(rendered.content)
    assert metadata == {
        "description": spec.description,
        "globs": ["on", "src/**/[a-z].py"],
        "alwaysApply": False,
    }
    assert body == spec.body


@pytest.mark.parametrize("context", list(RuleContext))
@pytest.mark.parametrize(
    ("globs", "apply_to"),
    [((), "**"), (("*.py", "src/**/*.py"), "*.py,src/**/*.py")],
)
def test_copilot_uses_native_apply_to_for_personal_and_project_rules(
    context: RuleContext, globs: tuple[str, ...], apply_to: str
) -> None:
    spec = _spec(globs=globs)

    rendered = render_rule(spec, RuleProvider.COPILOT, context)

    assert isinstance(rendered, RuleArtifact)
    metadata, body = _metadata(rendered.content)
    assert metadata == {"applyTo": apply_to}
    assert body == spec.body


def test_copilot_rejects_ambiguous_comma_delimited_glob() -> None:
    spec = _spec(globs=("src/**/*.{ts,tsx}",))

    with pytest.raises(RuleRenderError, match="comma delimiter"):
        render_rule(spec, RuleProvider.COPILOT, RuleContext.PROJECT)


def test_antigravity_path_scope_is_unsupported_without_a_documented_file_schema() -> (
    None
):
    rendered = render_rule(
        _spec(globs=("*.go",)), RuleProvider.ANTIGRAVITY, RuleContext.PROJECT
    )

    assert isinstance(rendered, UnsupportedRule)
    assert "glob-metadata" in rendered.reason


def test_antigravity_character_limit_is_exact_and_never_truncates() -> None:
    exact = _spec(body="x" * 12_000)
    oversized = _spec(body="x" * 12_001)

    rendered = render_rule(exact, RuleProvider.ANTIGRAVITY, RuleContext.PROJECT)

    assert isinstance(rendered, RuleArtifact)
    assert rendered.content == exact.body
    with pytest.raises(
        RuleRenderError,
        match=r"uses 12001 characters; provider limit is 12000",
    ):
        render_rule(oversized, RuleProvider.ANTIGRAVITY, RuleContext.PROJECT)


@pytest.mark.parametrize(
    ("provider", "context", "message"),
    [
        ("invented", RuleContext.PROJECT, "unknown rule provider"),
        (RuleProvider.CLAUDE, "invented", "unknown rule context"),
    ],
)
def test_unknown_provider_or_context_fails_loudly(
    provider: RuleProvider | str, context: RuleContext | str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        render_rule(_spec(), provider, context)


def test_artifact_and_unsupported_types_reject_invalid_manual_construction() -> None:
    with pytest.raises(ValueError, match="relative physical path"):
        RuleArtifact(
            RuleProvider.CLAUDE,
            RuleContext.PROJECT,
            "core",
            PurePosixPath("/absolute.md"),
            "# Body\n",
        )
    with pytest.raises(ValueError, match="must be explicit"):
        UnsupportedRule(
            RuleProvider.CODEX,
            RuleContext.PROJECT,
            "core",
            "implicit skip",
        )
