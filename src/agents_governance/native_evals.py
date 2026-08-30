"""Deterministic provider rendering evaluations for non-skill artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .agent_profiles import AgentContext, AgentProfile, render_agent
from .commands import (
    CommandRoute,
    CommandSpec,
    CommandTokenBudget,
    render_command,
    waza_bpe_counter,
)
from .projection_config import (
    ProjectionCell,
    ProjectionConfig,
    ProjectionContext,
    ProjectionStatus,
    ProjectionSurface,
    RuleLayout,
)
from .rule_adapters import RuleContext, render_rule
from .rules import RuleDistribution, RuleSpec


@dataclass(frozen=True)
class NativeEvalResult:
    commands: int
    agents: int
    rules: int


def _prefix(cell: ProjectionCell) -> PurePosixPath:
    if cell.path is None:
        raise ValueError("supported projection cell has no destination")
    return PurePosixPath(cell.path.removeprefix("${HOME}/"))


def _require_destination(cell: ProjectionCell, destination: PurePosixPath) -> None:
    if destination.parent not in {PurePosixPath("."), _prefix(cell)}:
        raise ValueError(
            "provider artifact destination differs from matrix: "
            f"{cell.provider.value}/{cell.context.value}/{cell.surface.value}/"
            f"{destination}"
        )


def _command_selected(command: CommandSpec, context: ProjectionContext) -> bool:
    route = (
        CommandRoute.AGENT
        if context is ProjectionContext.PERSONAL
        else CommandRoute.PROJECT
    )
    return command.route is route


def _agent_selected(agent: AgentProfile, context: ProjectionContext) -> bool:
    distribution = (
        "agent-wide" if context is ProjectionContext.PERSONAL else "project-wide"
    )
    return agent.distribution == distribution


def _rule_selected(rule: RuleSpec, context: ProjectionContext) -> bool:
    selected = (
        RuleDistribution.PERSONAL
        if context is ProjectionContext.PERSONAL
        else RuleDistribution.PROJECT
    )
    return rule.distribution in {RuleDistribution.BOTH, selected}


def evaluate_native(
    root: Path,
    config: ProjectionConfig,
    commands: tuple[CommandSpec, ...],
    agents: tuple[AgentProfile, ...],
    rules: tuple[RuleSpec, ...],
) -> NativeEvalResult:
    """Render every supported command, agent, and rule twice or raise."""

    prompt_defense_path = root / "rules" / "security" / "prompt-defense.md"
    if prompt_defense_path.is_symlink() or not prompt_defense_path.is_file():
        raise ValueError(
            f"prompt-defense owner must be a physical file: {prompt_defense_path}"
        )
    raw_defense = prompt_defense_path.read_text(encoding="utf-8")
    if raw_defense.startswith("---\n"):
        end = raw_defense.find("\n---\n", 4)
        if end != -1:
            prompt_defense = raw_defense[end + 5 :].lstrip()
        else:
            prompt_defense = raw_defense
    else:
        prompt_defense = raw_defense
    counter = waza_bpe_counter(root)
    counts = {surface: 0 for surface in ProjectionSurface}
    for cell in config.cells.values():
        if cell.status is ProjectionStatus.UNSUPPORTED:
            continue
        if cell.surface is ProjectionSurface.COMMANDS:
            for command in commands:
                if not _command_selected(command, cell.context):
                    continue
                budget = CommandTokenBudget(cell.max_tokens, counter)
                command_artifact = render_command(
                    command, cell.provider.value, token_budget=budget
                )
                _require_destination(cell, command_artifact.destination)
                if command_artifact != render_command(
                    command, cell.provider.value, token_budget=budget
                ):
                    raise ValueError(
                        f"command rendering is not deterministic: {command.name}"
                    )
                counts[cell.surface] += 1
        elif cell.surface is ProjectionSurface.AGENTS:
            for agent in agents:
                if not _agent_selected(agent, cell.context):
                    continue
                agent_artifact = render_agent(
                    agent,
                    cell.provider.value,
                    AgentContext(cell.context.value),
                    prompt_defense=prompt_defense,
                )
                _require_destination(cell, agent_artifact.destination)
                if agent_artifact != render_agent(
                    agent,
                    cell.provider.value,
                    AgentContext(cell.context.value),
                    prompt_defense=prompt_defense,
                ):
                    raise ValueError(
                        f"agent rendering is not deterministic: {agent.name}"
                    )
                counts[cell.surface] += 1
        elif (
            cell.surface is ProjectionSurface.RULES
            and cell.layout is RuleLayout.DIRECTORY
        ):
            for rule in rules:
                if not _rule_selected(rule, cell.context):
                    continue
                rule_artifact = render_rule(
                    rule, cell.provider.value, RuleContext(cell.context.value)
                )
                _require_destination(cell, rule_artifact.destination)
                if rule_artifact != render_rule(
                    rule, cell.provider.value, RuleContext(cell.context.value)
                ):
                    raise ValueError(
                        f"rule rendering is not deterministic: {rule.identity}"
                    )
                counts[cell.surface] += 1
    return NativeEvalResult(
        counts[ProjectionSurface.COMMANDS],
        counts[ProjectionSurface.AGENTS],
        counts[ProjectionSurface.RULES],
    )


__all__ = ("NativeEvalResult", "evaluate_native")
