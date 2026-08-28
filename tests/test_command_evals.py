from __future__ import annotations

from pathlib import Path

import pytest

from agents_governance.command_evals import CommandEvalRole, audit_command_evals
from agents_governance.commands import (
    CommandIntent,
    CommandRisk,
    CommandRoute,
    CommandSpec,
)


def _command(root: Path, name: str = "feature-development") -> CommandSpec:
    path = root / "commands" / f"{name}.md"
    path.parent.mkdir(parents=True)
    path.write_text("command\n", encoding="utf-8")
    return CommandSpec(
        path,
        name,
        "Implement one approved feature.",
        "<feature>",
        ("intent:implementation", "risk:write", "route:project"),
        CommandRoute.PROJECT,
        (CommandIntent.IMPLEMENTATION,),
        CommandRisk.WRITE,
        "Use $ARGUMENTS and reject ambiguous input.\n",
    )


def _eval_text(command: str = "feature-development") -> str:
    blocks: list[str] = []
    for role in CommandEvalRole:
        providers = ""
        if role in {
            CommandEvalRole.SUPPORTED_RENDERING,
            CommandEvalRole.PROJECTION_FIXED_POINT,
        }:
            providers = "\n    providers: [claude, cursor, gemini, opencode]"
        elif role is CommandEvalRole.UNSUPPORTED_PROVIDER:
            providers = "\n    providers: [antigravity, codex, copilot]"
        blocks.append(
            f"  - role: {role.value}\n"
            f"    prompt: Material {role.value} request for {command}."
            f"{providers}\n"
            "    assertions:\n"
            "      output_contains: [owner, evidence]\n"
            "      output_not_contains: [fallback]\n"
        )
    return f"command: {command}\nschemaVersion: '1.0'\nscenarios:\n" + "".join(blocks)


def _write_eval(root: Path, command: str = "feature-development") -> Path:
    path = root / "evals" / "commands" / command / "eval.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(_eval_text(command), encoding="utf-8")
    return path


def test_command_eval_requires_all_seven_families(tmp_path: Path) -> None:
    command = _command(tmp_path)
    path = _write_eval(tmp_path)

    specs = audit_command_evals(tmp_path, (command,))

    assert specs[0].path == path
    assert tuple(item.role for item in specs[0].scenarios) == tuple(CommandEvalRole)


def test_unknown_role_raises_before_later_scenarios(tmp_path: Path) -> None:
    command = _command(tmp_path)
    path = _write_eval(tmp_path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "  - role: should-not-run\n", "  - role: future-mode\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="future-mode"):
        audit_command_evals(tmp_path, (command,))


def test_suite_directories_must_exactly_equal_commands(tmp_path: Path) -> None:
    command = _command(tmp_path)
    _write_eval(tmp_path, "unknown-command")

    with pytest.raises(ValueError, match="exactly equal"):
        audit_command_evals(tmp_path, (command,))


def test_provider_matrix_rejects_copilot_as_supported(tmp_path: Path) -> None:
    command = _command(tmp_path)
    path = _write_eval(tmp_path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "providers: [claude, cursor, gemini, opencode]",
            "providers: [claude, copilot, cursor, gemini, opencode]",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="providers must equal"):
        audit_command_evals(tmp_path, (command,))


def test_assertions_are_material_and_bidirectional(tmp_path: Path) -> None:
    command = _command(tmp_path)
    path = _write_eval(tmp_path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "      output_contains: [owner, evidence]\n",
            "      output_contains: []\n",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(TypeError, match="output_contains"):
        audit_command_evals(tmp_path, (command,))


def test_repository_has_one_complete_suite_per_command() -> None:
    root = Path(__file__).resolve().parents[1]
    from agents_governance.commands import audit_command_specs

    commands = audit_command_specs(root)
    specs = audit_command_evals(root, commands)

    assert len(specs) == len(commands) == 7
