from __future__ import annotations

import tomllib
from dataclasses import replace
from pathlib import Path, PurePosixPath

import pytest

import agents_governance.cli as cli_module
from agents_governance.catalog import Catalog
from agents_governance.cli import main
from agents_governance.commands import (
    CommandAdapterStatus,
    CommandArtifact,
    CommandProvider,
    CommandRenderError,
    CommandTokenBudget,
    UnsupportedCommand,
    audit_command_specs,
    render_command,
    waza_bpe_counter,
)
from agents_governance.validation import validate

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
    extra_frontmatter: str = "",
) -> Path:
    commands = root / "commands"
    commands.mkdir(exist_ok=True)
    hint = f"argument-hint: {argument_hint!r}\n" if argument_hint is not None else ""
    path = commands / f"{name}.md"
    path.write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        f"{hint}"
        "metadata:\n"
        f"  aihub.tags: '{tags}'\n"
        f"{extra_frontmatter}"
        "---\n\n"
        f"{body}",
        encoding="utf-8",
    )
    return path


def _only_spec(root: Path):
    audit = audit_command_specs(root)
    assert audit.findings == ()
    assert len(audit.commands) == 1
    return audit.commands[0]


def _budget(max_tokens: int | None = None) -> CommandTokenBudget:
    return CommandTokenBudget(max_tokens=max_tokens, counter=len)


def _write_catalog_config(root: Path) -> None:
    config = root / "config"
    config.mkdir()
    (root / "skills").mkdir()
    (config / "skills.json").write_text(
        '{"version":2,"budgets":{"router_tokens":500,'
        '"frozen_tokens":1200,"on_demand_tokens":5000,"max_lines":500}}\n',
        encoding="utf-8",
    )


def test_valid_command_is_loaded_into_a_typed_spec(tmp_path: Path) -> None:
    path = _write_command(tmp_path)

    spec = _only_spec(tmp_path)

    assert spec.path == path
    assert spec.name == "deploy-service"
    assert spec.route.value == "project"
    assert tuple(intent.value for intent in spec.intents) == ("implementation",)
    assert spec.risk.value == "write"
    assert spec.uses_arguments is True
    assert spec.body == "# Deploy service\n\nUse $ARGUMENTS as the approved target.\n"


@pytest.mark.parametrize(
    ("mutate", "expected_code"),
    [
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "name: deploy-service", "name: another-command"
                ),
                encoding="utf-8",
            ),
            "command-name",
        ),
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "Deploy one approved service through its project owner.",
                    "This is one sentence. This is another.",
                ),
                encoding="utf-8",
            ),
            "command-description",
        ),
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "argument-hint: '<service and approved target>'\n", ""
                ),
                encoding="utf-8",
            ),
            "command-argument-hint",
        ),
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    PROJECT_TAGS,
                    '["risk:write","intent:implementation","route:project"]',
                ),
                encoding="utf-8",
            ),
            "command-tags",
        ),
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    PROJECT_TAGS,
                    '["intent:unknown","risk:write","route:project"]',
                ),
                encoding="utf-8",
            ),
            "command-intent",
        ),
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    PROJECT_TAGS,
                    '["intent:implementation","risk:read","risk:write","route:project"]',
                ),
                encoding="utf-8",
            ),
            "command-risk",
        ),
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    PROJECT_TAGS,
                    '["intent:implementation","risk:write","route:agent","route:project"]',
                ),
                encoding="utf-8",
            ),
            "command-route",
        ),
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "# Deploy service\n\nUse $ARGUMENTS as the approved target.\n",
                    "   \n",
                ),
                encoding="utf-8",
            ),
            "command-body",
        ),
        (
            lambda path: path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "metadata:\n", "model: forbidden\nmetadata:\n"
                ),
                encoding="utf-8",
            ),
            "command-field",
        ),
    ],
)
def test_schema_violations_fail_closed(
    mutate: object, expected_code: str, tmp_path: Path
) -> None:
    path = _write_command(tmp_path)
    assert callable(mutate)
    mutate(path)

    audit = audit_command_specs(tmp_path)

    assert expected_code in {finding.code for finding in audit.findings}
    assert audit.commands == ()


@pytest.mark.parametrize(
    "tags",
    [
        "not-json",
        '{"intent": "implementation"}',
        '["intent:implementation",7,"risk:write","route:project"]',
        '["intent:implementation","intent:implementation","risk:write","route:project"]',
        '["intent:implementation","risk:write","route:project","scope:extra"]',
    ],
)
def test_tags_must_be_a_sorted_json_string_with_only_typed_values(
    tags: str, tmp_path: Path
) -> None:
    _write_command(tmp_path, tags=tags)

    audit = audit_command_specs(tmp_path)

    assert "command-tags" in {finding.code for finding in audit.findings}
    assert audit.commands == ()


def test_command_spec_revalidates_direct_dataclass_changes(tmp_path: Path) -> None:
    _write_command(tmp_path)
    spec = _only_spec(tmp_path)

    with pytest.raises(ValueError, match="body"):
        replace(spec, body="")


def test_discovery_rejects_nested_non_markdown_and_linked_commands(
    tmp_path: Path,
) -> None:
    commands = tmp_path / "commands"
    commands.mkdir()
    nested = commands / "nested"
    nested.mkdir()
    (nested / "hidden.md").write_text("hidden\n", encoding="utf-8")
    (commands / "registry.json").write_text("{}\n", encoding="utf-8")
    source = tmp_path / "linked-source.md"
    source.write_text("linked\n", encoding="utf-8")
    (commands / "linked.md").symlink_to(source)

    audit = audit_command_specs(tmp_path)

    assert {(finding.path, finding.code) for finding in audit.findings} == {
        ("commands/linked.md", "command-symlink"),
        ("commands/nested", "command-layout"),
        ("commands/registry.json", "command-layout"),
    }
    assert audit.commands == ()


def test_command_slug_collision_with_received_skill_names_is_blocking(
    tmp_path: Path,
) -> None:
    _write_command(tmp_path, name="deploy-service")

    audit = audit_command_specs(tmp_path, skill_names=("review", "deploy-service"))

    assert [(finding.path, finding.code) for finding in audit.findings] == [
        ("commands/deploy-service.md", "command-skill-collision")
    ]
    assert audit.commands == ()


@pytest.mark.parametrize(
    ("provider", "destination"),
    [
        (CommandProvider.CLAUDE, PurePosixPath(".claude/commands/deploy-service.md")),
        (CommandProvider.GEMINI, PurePosixPath(".gemini/commands/deploy-service.toml")),
        (CommandProvider.OPENCODE, PurePosixPath("deploy-service.md")),
        (CommandProvider.CURSOR, PurePosixPath(".cursor/commands/deploy-service.md")),
        (CommandProvider.COPILOT, PurePosixPath(".claude/commands/deploy-service.md")),
    ],
)
def test_supported_adapters_render_full_body_deterministically_and_manual_only(
    provider: CommandProvider, destination: PurePosixPath, tmp_path: Path
) -> None:
    _write_command(tmp_path)
    spec = _only_spec(tmp_path)

    first = render_command(spec, provider, token_budget=_budget())
    second = render_command(spec, provider, token_budget=_budget())

    assert isinstance(first, CommandArtifact)
    assert first == second
    assert first.status is CommandAdapterStatus.SUPPORTED
    assert first.destination == destination
    assert first.manual_only is True
    assert first.tokens == len(first.content)
    assert first.max_tokens is None
    if provider is CommandProvider.GEMINI:
        rendered = tomllib.loads(first.content)
        assert rendered["description"] == spec.description
        assert rendered["prompt"] == spec.body.replace("$ARGUMENTS", "{{args}}")
    elif provider is CommandProvider.CURSOR:
        assert first.content == spec.body
    else:
        assert first.content.endswith(spec.body)


def test_claude_and_copilot_use_claude_manual_command_format(tmp_path: Path) -> None:
    _write_command(tmp_path)
    spec = _only_spec(tmp_path)

    for provider in (CommandProvider.CLAUDE, CommandProvider.COPILOT):
        rendered = render_command(spec, provider, token_budget=_budget())
        assert isinstance(rendered, CommandArtifact)
        assert rendered.content.startswith(
            "---\n"
            'description: "Deploy one approved service through its project owner."\n'
            'argument-hint: "<service and approved target>"\n'
            "disable-model-invocation: true\n"
            "---\n\n"
        )


def test_long_command_body_is_never_truncated_or_converted(tmp_path: Path) -> None:
    body = "# Complete workflow\n\n" + "Preserve this material line.\n" * 2_000
    _write_command(tmp_path, argument_hint=None, body=body)
    spec = _only_spec(tmp_path)

    rendered = render_command(spec, CommandProvider.OPENCODE, token_budget=_budget())

    assert isinstance(rendered, CommandArtifact)
    assert rendered.content.endswith(body)
    assert rendered.content.count("Preserve this material line.") == 2_000
    assert rendered.destination.suffix == ".md"


def test_token_budget_accepts_exact_boundary_and_rejects_oversize_without_truncation(
    tmp_path: Path,
) -> None:
    _write_command(tmp_path)
    spec = _only_spec(tmp_path)
    baseline = render_command(spec, CommandProvider.CLAUDE, token_budget=_budget())
    assert isinstance(baseline, CommandArtifact)
    exact_tokens = len(baseline.content)

    exact = render_command(
        spec,
        CommandProvider.CLAUDE,
        token_budget=_budget(exact_tokens),
    )

    assert isinstance(exact, CommandArtifact)
    assert exact.content == baseline.content
    assert exact.tokens == exact_tokens
    assert exact.max_tokens == exact_tokens
    with pytest.raises(
        CommandRenderError,
        match=rf"uses {exact_tokens} tokens; provider limit is {exact_tokens - 1}",
    ):
        render_command(
            spec,
            CommandProvider.CLAUDE,
            token_budget=_budget(exact_tokens - 1),
        )
    assert spec.body in baseline.content


def test_supported_adapter_requires_caller_owned_token_budget(tmp_path: Path) -> None:
    _write_command(tmp_path)
    spec = _only_spec(tmp_path)

    with pytest.raises(CommandRenderError, match="token budget is required"):
        render_command(spec, CommandProvider.CLAUDE)


def test_waza_counter_removes_destination_local_candidate_on_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_command(tmp_path)

    def fail_count(_path: Path, _root: Path) -> int:
        raise RuntimeError("injected BPE failure")

    monkeypatch.setattr("agents_governance.commands.bpe_tokens", fail_count)

    with pytest.raises(RuntimeError, match="injected BPE failure"):
        waza_bpe_counter(tmp_path)("complete rendered command\n")
    assert not tuple((tmp_path / "commands").glob(".*.candidate"))


@pytest.mark.parametrize(
    ("provider", "body"),
    [
        (CommandProvider.GEMINI, "# Unsafe\n\nRun !{rm -rf /} for $ARGUMENTS.\n"),
        (CommandProvider.GEMINI, "# Unsafe\n\nRead @{../../secret} for $ARGUMENTS.\n"),
        (CommandProvider.OPENCODE, "# Unsafe\n\nRun !`rm -rf /` for $ARGUMENTS.\n"),
        (CommandProvider.OPENCODE, "# Unsafe\n\nRun $(malicious) for $ARGUMENTS.\n"),
    ],
)
def test_provider_shell_and_file_interpolation_is_rejected(
    provider: CommandProvider, body: str, tmp_path: Path
) -> None:
    _write_command(tmp_path, body=body)
    spec = _only_spec(tmp_path)

    with pytest.raises(CommandRenderError, match="interpolation"):
        render_command(spec, provider, token_budget=_budget())


def test_opencode_rejects_provider_builtin_override(tmp_path: Path) -> None:
    _write_command(tmp_path, name="review")
    spec = _only_spec(tmp_path)

    with pytest.raises(CommandRenderError, match="reserved"):
        render_command(
            spec,
            CommandProvider.OPENCODE,
            token_budget=_budget(),
            reserved_slugs=("review",),
        )


@pytest.mark.parametrize(
    "provider", (CommandProvider.CODEX, CommandProvider.ANTIGRAVITY)
)
def test_unsupported_providers_return_explicit_typed_status(
    provider: CommandProvider, tmp_path: Path
) -> None:
    _write_command(tmp_path)
    spec = _only_spec(tmp_path)

    rendered = render_command(spec, provider)

    assert isinstance(rendered, UnsupportedCommand)
    assert rendered.status is CommandAdapterStatus.UNSUPPORTED
    assert rendered.provider is provider
    assert rendered.slug == spec.name
    assert rendered.reason.startswith("UNSUPPORTED:")


def test_cursor_rejects_agent_route_because_only_project_commands_are_supported(
    tmp_path: Path,
) -> None:
    _write_command(tmp_path, tags=AGENT_TAGS)
    spec = _only_spec(tmp_path)

    rendered = render_command(spec, CommandProvider.CURSOR)

    assert isinstance(rendered, UnsupportedCommand)
    assert rendered.status is CommandAdapterStatus.UNSUPPORTED
    assert "project" in rendered.reason


def test_all_seven_canonical_commands_validate_without_a_registry() -> None:
    root = Path(__file__).resolve().parents[1]

    audit = audit_command_specs(root)

    assert audit.findings == ()
    assert {command.name for command in audit.commands} == {
        "add-language-rules",
        "database-migration",
        "feature-development",
        "ghi-list",
        "pr-list",
        "ralph-loop",
        "security-triage",
    }
    assert all(command.body for command in audit.commands)


def test_commands_cli_audits_renders_and_reports_unsupported_explicitly(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_catalog_config(tmp_path)
    _write_command(tmp_path)

    assert main(["--root", str(tmp_path), "commands", "audit"]) == 0
    assert "PASS: 1 commands validated" in capsys.readouterr().out

    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "commands",
                "render",
                "deploy-service",
                "--provider",
                "gemini",
            ]
        )
        == 0
    )
    rendered = tomllib.loads(capsys.readouterr().out)
    assert rendered["prompt"].endswith("Use {{args}} as the approved target.\n")

    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "commands",
                "render",
                "deploy-service",
                "--provider",
                "codex",
                "--max-tokens",
                "10000",
            ]
        )
        == 2
    )
    assert "UNSUPPORTED: Codex has no canonical command adapter" in (
        capsys.readouterr().err
    )


def test_command_render_reports_bpe_runtime_failure_without_traceback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_catalog_config(tmp_path)
    _write_command(tmp_path)

    def unavailable_counter(_root: Path) -> object:
        raise OSError("BPE runtime unavailable")

    monkeypatch.setattr(cli_module, "waza_bpe_counter", unavailable_counter)

    assert (
        main(
            [
                "--root",
                str(tmp_path),
                "commands",
                "render",
                "deploy-service",
                "--provider",
                "gemini",
            ]
        )
        == 1
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "FAIL: BPE runtime unavailable\n"


def test_global_validation_includes_command_skill_slug_collision(
    tmp_path: Path,
) -> None:
    _write_catalog_config(tmp_path)
    skill = tmp_path / "skills" / "agent-wide" / "deploy-service"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: deploy-service\n"
        "description: Deploy a governed service when that reusable skill is requested.\n"
        "metadata:\n"
        "  aihub.tags: "
        '\'["provenance:agents-owned","updates:manual","usage:on-demand"]\'\n'
        "---\n"
        "# Deploy service\n",
        encoding="utf-8",
    )
    _write_command(tmp_path)

    findings = validate(Catalog(tmp_path))

    assert (
        "commands/deploy-service.md",
        "command-skill-collision",
    ) in {(finding.path, finding.code) for finding in findings}
