from __future__ import annotations

from pathlib import Path

from agents_governance.command_evals import (
    CommandEvalRole,
    audit_command_evals,
)
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
        path=path,
        name=name,
        description="Implement one approved feature.",
        argument_hint="<feature>",
        tags=("intent:implementation", "risk:write", "route:project"),
        route=CommandRoute.PROJECT,
        intents=(CommandIntent.IMPLEMENTATION,),
        risk=CommandRisk.WRITE,
        body="Use $ARGUMENTS and reject ambiguous input.\n",
    )


def _eval_text(command: str = "feature-development") -> str:
    roles = tuple(CommandEvalRole)
    blocks = []
    for role in roles:
        providers = ""
        if role in {
            CommandEvalRole.SUPPORTED_RENDERING,
            CommandEvalRole.PROJECTION_FIXED_POINT,
        }:
            providers = "\n    providers: [claude, copilot, cursor, gemini, opencode]"
        elif role is CommandEvalRole.UNSUPPORTED_PROVIDER:
            providers = "\n    providers: [antigravity, codex]"
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


def test_command_eval_audit_requires_all_seven_semantic_families(
    tmp_path: Path,
) -> None:
    command = _command(tmp_path)
    path = _write_eval(tmp_path)

    audit = audit_command_evals(tmp_path, (command,))

    assert not audit.findings
    assert audit.specs[0].path == path
    assert tuple(item.role for item in audit.specs[0].scenarios) == tuple(
        CommandEvalRole
    )


def test_command_eval_audit_fails_on_missing_unknown_or_duplicate_roles(
    tmp_path: Path,
) -> None:
    command = _command(tmp_path)
    path = _write_eval(tmp_path)
    payload = path.read_text(encoding="utf-8")
    path.write_text(
        payload.replace("  - role: should-not-run\n", "  - role: future-mode\n"),
        encoding="utf-8",
    )

    audit = audit_command_evals(tmp_path, (command,))

    assert {finding.code for finding in audit.findings} == {
        "command-eval-role",
        "command-eval-coverage",
    }


def test_command_eval_audit_fails_on_missing_extra_and_linked_suites(
    tmp_path: Path,
) -> None:
    command = _command(tmp_path)
    extra = _write_eval(tmp_path, "unknown-command")
    linked = extra.parent
    target = tmp_path / "linked-suite"
    linked.rename(target)
    linked.symlink_to(target, target_is_directory=True)

    audit = audit_command_evals(tmp_path, (command,))

    assert {finding.code for finding in audit.findings} == {
        "command-eval-missing",
        "command-eval-layout",
    }


def test_command_eval_provider_matrix_is_route_aware(tmp_path: Path) -> None:
    command = _command(tmp_path, "ghi-list")
    command = CommandSpec(
        path=command.path,
        name=command.name,
        description=command.description,
        argument_hint=command.argument_hint,
        tags=("intent:inspection", "risk:external", "route:agent"),
        route=CommandRoute.AGENT,
        intents=(CommandIntent.INSPECTION,),
        risk=CommandRisk.EXTERNAL,
        body=command.body,
    )
    path = _write_eval(tmp_path, "ghi-list")

    audit = audit_command_evals(tmp_path, (command,))

    assert any(
        finding.code == "command-eval-providers" and "cursor" in finding.message
        for finding in audit.findings
    )
    path.write_text(
        path.read_text(encoding="utf-8")
        .replace(
            "providers: [claude, copilot, cursor, gemini, opencode]",
            "providers: [claude, copilot, gemini, opencode]",
        )
        .replace(
            "providers: [antigravity, codex]",
            "providers: [antigravity, codex, cursor]",
        ),
        encoding="utf-8",
    )

    assert not audit_command_evals(tmp_path, (command,)).findings


def test_command_eval_assertions_must_be_material_and_bidirectional(
    tmp_path: Path,
) -> None:
    command = _command(tmp_path)
    path = _write_eval(tmp_path)
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "      output_contains: [owner, evidence]\n"
            "      output_not_contains: [fallback]\n",
            "      output_contains: []\n      output_not_contains: []\n",
            1,
        ),
        encoding="utf-8",
    )

    audit = audit_command_evals(tmp_path, (command,))

    assert {finding.code for finding in audit.findings} == {"command-eval-assertions"}
