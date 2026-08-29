from __future__ import annotations

import tomllib
from dataclasses import replace
from pathlib import Path, PurePosixPath

import pytest

from agents_governance.commands import (
    CommandArtifact,
    CommandProvider,
    CommandRenderError,
    CommandTokenBudget,
    audit_command_specs,
    render_command,
    waza_bpe_counter,
)

PROJECT_TAGS = '["intent:implementation","risk:write","route:project"]'
AGENT_TAGS = '["intent:inspection","risk:external","route:agent"]'


def _write_command(
    root: Path,
    name: str = "deploy-service",
    *,
    description: str = "Deploy one approved service through its project owner.",
    argument_hint: str | None = "<service and approved target>",
    tags: str = PROJECT_TAGS,
    body: str = "# Deploy service\n\nUse $ARGUMENTS as the approved target.\n",
    subdir: str = "implementation",
) -> Path:
    commands = root / "commands" / subdir
    commands.mkdir(parents=True, exist_ok=True)
    hint = f"argument-hint: {argument_hint!r}\n" if argument_hint is not None else ""
    path = commands / f"{name}.md"
    path.write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"{hint}"
        "metadata:\n"
        f"  aihub.tags: '{tags}'\n"
        "---\n\n"
        f"{body}",
        encoding="utf-8",
    )
    return path


def _only_spec(root: Path):
    specs = audit_command_specs(root)
    assert len(specs) == 1
    return specs[0]


def _only_spec_after_write(root: Path):
    _write_command(root)
    return _only_spec(root)


def _budget(max_tokens: int | None = None) -> CommandTokenBudget:
    return CommandTokenBudget(max_tokens=max_tokens, counter=len)


def test_valid_command_is_loaded_into_a_typed_spec(tmp_path: Path) -> None:
    path = _write_command(tmp_path)
    spec = _only_spec(tmp_path)

    assert spec.path == path
    assert spec.name == "deploy-service"
    assert spec.route.value == "project"
    assert tuple(intent.value for intent in spec.intents) == ("implementation",)
    assert spec.risk.value == "write"
    assert spec.uses_arguments


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("name: deploy-service", "name: other", "name must equal"),
        (
            "Deploy one approved service through its project owner.",
            "First sentence. Second sentence.",
            "one short sentence",
        ),
        ("argument-hint: '<service and approved target>'\n", "", "argument-hint"),
        (PROJECT_TAGS, '["risk:write","route:project"]', "intent"),
        (PROJECT_TAGS, '["intent:unknown","risk:write","route:project"]', "unknown"),
        (
            "# Deploy service\n\nUse $ARGUMENTS as the approved target.\n",
            "   \n",
            "body",
        ),
    ],
)
def test_schema_stops_on_the_first_defect(
    tmp_path: Path, old: str, new: str, message: str
) -> None:
    path = _write_command(tmp_path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8"
    )

    with pytest.raises((TypeError, ValueError), match=message):
        audit_command_specs(tmp_path)


def test_discovery_rejects_the_first_noncanonical_entry(tmp_path: Path) -> None:
    commands = tmp_path / "commands"
    commands.mkdir()
    impl = commands / "implementation"
    impl.mkdir()
    (impl / "broken-link.md").symlink_to("/nonexistent")

    with pytest.raises(ValueError, match="physical regular file"):
        audit_command_specs(tmp_path)


def test_command_slug_collision_raises_immediately(tmp_path: Path) -> None:
    _write_command(tmp_path)

    with pytest.raises(ValueError, match="collides with canonical skill"):
        audit_command_specs(tmp_path, skill_names=("deploy-service",))


@pytest.mark.parametrize(
    ("provider", "destination"),
    [
        (CommandProvider.CLAUDE, PurePosixPath(".claude/commands/deploy-service.md")),
        (
            CommandProvider.GEMINI,
            PurePosixPath(".gemini/commands/deploy-service.toml"),
        ),
        (CommandProvider.OPENCODE, PurePosixPath("deploy-service.md")),
        (CommandProvider.CURSOR, PurePosixPath(".cursor/commands/deploy-service.md")),
    ],
)
def test_supported_adapters_render_complete_provider_owned_artifacts(
    tmp_path: Path, provider: CommandProvider, destination: PurePosixPath
) -> None:
    spec = _only_spec_after_write(tmp_path)
    artifact = render_command(spec, provider, token_budget=_budget())

    assert isinstance(artifact, CommandArtifact)
    assert artifact.destination == destination
    assert artifact.manual_only
    assert artifact.tokens == len(artifact.content)
    if provider is CommandProvider.GEMINI:
        assert tomllib.loads(artifact.content)["prompt"].endswith(
            "{{args}} as the approved target.\n"
        )
    else:
        assert spec.body in artifact.content


@pytest.mark.parametrize(
    "provider",
    (CommandProvider.ANTIGRAVITY, CommandProvider.CODEX, CommandProvider.COPILOT),
)
def test_unsupported_provider_is_an_exception(
    tmp_path: Path, provider: CommandProvider
) -> None:
    spec = _only_spec_after_write(tmp_path)

    with pytest.raises(CommandRenderError, match="UNSUPPORTED"):
        render_command(spec, provider, token_budget=_budget())


def test_cursor_agent_route_is_an_exception(tmp_path: Path) -> None:
    _write_command(tmp_path, tags=AGENT_TAGS)
    spec = _only_spec(tmp_path)

    with pytest.raises(CommandRenderError, match="UNSUPPORTED"):
        render_command(spec, CommandProvider.CURSOR, token_budget=_budget())


def test_token_budget_rejects_oversize_without_truncation(tmp_path: Path) -> None:
    spec = _only_spec_after_write(tmp_path)
    complete = render_command(spec, CommandProvider.CLAUDE, token_budget=_budget())

    with pytest.raises(CommandRenderError, match="provider limit"):
        render_command(
            spec,
            CommandProvider.CLAUDE,
            token_budget=_budget(len(complete.content) - 1),
        )
    assert spec.body in complete.content


def test_supported_adapter_requires_explicit_token_budget(tmp_path: Path) -> None:
    spec = _only_spec_after_write(tmp_path)

    with pytest.raises(CommandRenderError, match="token budget is required"):
        render_command(spec, CommandProvider.CLAUDE)


def test_command_spec_revalidates_direct_dataclass_changes(tmp_path: Path) -> None:
    spec = _only_spec_after_write(tmp_path)

    with pytest.raises(ValueError, match="body"):
        replace(spec, body="")


def test_waza_counter_uses_in_memory_content_and_preserves_original_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_command(tmp_path)

    def fail_count(content: str, root: Path) -> int:
        assert content == "complete rendered command\n"
        assert root == tmp_path
        raise RuntimeError("injected BPE failure")

    monkeypatch.setattr("agents_governance.commands.bpe_content", fail_count)
    with pytest.raises(RuntimeError, match="injected BPE failure"):
        waza_bpe_counter(tmp_path)("complete rendered command\n")


def test_all_canonical_commands_validate_without_registry() -> None:
    root = Path(__file__).resolve().parents[1]
    specs = audit_command_specs(root)

    assert {command.name for command in specs} == {
        path.stem for path in (root / "commands").rglob("*.md")
    }
